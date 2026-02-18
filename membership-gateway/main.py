"""Intent Solutions Membership Gateway.

Handles Whop webhooks to manage GitHub team membership for subscribers.
Deployed on Cloud Run, ~200 lines of core logic.
"""

import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
ORG = "intent-solutions-io"
TEAM_SLUG = "members"
GITHUB_USERNAME_FIELD = "GitHub Username"

WHOP_WEBHOOK_SECRET = os.environ.get("WHOP_WEBHOOK_SECRET", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
WHOP_API_KEY = os.environ.get("WHOP_API_KEY", "")
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL", "")
GCP_PROJECT = os.environ.get("GCP_PROJECT", "diagnostic-pro-start-up")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("gateway")

@asynccontextmanager
async def lifespan(app):
    log.info("Membership Gateway starting...")
    if not GITHUB_TOKEN:
        log.warning("GITHUB_TOKEN not set — GitHub operations will fail")
    if not WHOP_WEBHOOK_SECRET:
        log.warning("WHOP_WEBHOOK_SECRET not set — webhook verification disabled")
    yield
    await github.aclose()
    await whop.aclose()
    await slack.aclose()
    log.info("Membership Gateway shut down")


app = FastAPI(title="Membership Gateway", version="1.0.0", lifespan=lifespan)

# ---------------------------------------------------------------------------
# Clients
# ---------------------------------------------------------------------------
github = httpx.AsyncClient(
    base_url="https://api.github.com",
    headers={
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    },
    timeout=10.0,
)

whop = httpx.AsyncClient(
    base_url="https://api.whop.com/api/v5",
    headers={
        "Authorization": f"Bearer {WHOP_API_KEY}",
        "Content-Type": "application/json",
    },
    timeout=10.0,
)

slack = httpx.AsyncClient(timeout=5.0)


# ---------------------------------------------------------------------------
# Firestore (lazy init)
# ---------------------------------------------------------------------------
_firestore_client = None


def get_firestore():
    global _firestore_client
    if _firestore_client is None:
        from google.cloud import firestore
        _firestore_client = firestore.Client(project=GCP_PROJECT)
    return _firestore_client


async def audit_log(membership_id: str, github_username: str, action: str, details: str = ""):
    """Log action to Firestore for audit trail."""
    try:
        db = get_firestore()
        db.collection("membership_audit").add({
            "membership_id": membership_id,
            "github_username": github_username,
            "action": action,
            "details": details,
            "timestamp": datetime.now(timezone.utc),
        })
    except Exception as e:
        log.error(f"Firestore audit log failed: {e}")


# ---------------------------------------------------------------------------
# Slack notifications
# ---------------------------------------------------------------------------
async def notify_slack(message: str):
    """Send notification to owner via Slack webhook."""
    if not SLACK_WEBHOOK_URL:
        log.info(f"Slack (disabled): {message}")
        return
    try:
        await slack.post(SLACK_WEBHOOK_URL, json={"text": f":robot_face: Membership Gateway: {message}"})
    except Exception as e:
        log.error(f"Slack notification failed: {e}")


# ---------------------------------------------------------------------------
# Webhook signature verification
# ---------------------------------------------------------------------------
def verify_webhook(payload: bytes, headers: dict) -> bool:
    """Verify Whop webhook using Standard Webhooks HMAC signature.

    Whop uses the Standard Webhooks spec. The signature is in the
    `webhook-signature` header, and the message ID and timestamp are in
    `webhook-id` and `webhook-timestamp` respectively.
    """
    if not WHOP_WEBHOOK_SECRET:
        log.warning("WHOP_WEBHOOK_SECRET not set — skipping verification")
        return True

    try:
        from standardwebhooks import Webhook
        wh = Webhook(WHOP_WEBHOOK_SECRET)
        wh.verify(payload, headers)
        return True
    except Exception as e:
        log.warning(f"Webhook verification failed: {e}")
        return False


# ---------------------------------------------------------------------------
# GitHub team management
# ---------------------------------------------------------------------------
async def add_to_team(username: str) -> dict:
    """Add a GitHub user to the members team (sends org invitation if needed)."""
    r = await github.put(
        f"/orgs/{ORG}/teams/{TEAM_SLUG}/memberships/{username}",
        json={"role": "member"},
    )
    if r.status_code in (200, 201):
        data = r.json()
        log.info(f"GitHub: added {username} to {TEAM_SLUG} (state={data.get('state')})")
        return data
    else:
        log.error(f"GitHub: failed to add {username}: {r.status_code} {r.text}")
        raise HTTPException(status_code=502, detail=f"GitHub API error: {r.status_code}")


async def remove_from_team(username: str) -> bool:
    """Remove a GitHub user from the members team."""
    r = await github.delete(f"/orgs/{ORG}/teams/{TEAM_SLUG}/memberships/{username}")
    if r.status_code == 204:
        log.info(f"GitHub: removed {username} from {TEAM_SLUG}")
        return True
    elif r.status_code == 404:
        log.info(f"GitHub: {username} was not on {TEAM_SLUG} (already removed)")
        return True
    else:
        log.error(f"GitHub: failed to remove {username}: {r.status_code} {r.text}")
        raise HTTPException(status_code=502, detail=f"GitHub API error: {r.status_code}")


async def get_team_members() -> set[str]:
    """Get all current members of the GitHub team."""
    members = set()
    page = 1
    while True:
        r = await github.get(
            f"/orgs/{ORG}/teams/{TEAM_SLUG}/members",
            params={"per_page": 100, "page": page},
        )
        if r.status_code != 200:
            log.error(f"GitHub: failed to list team members: {r.status_code}")
            break
        data = r.json()
        if not data:
            break
        for member in data:
            members.add(member["login"].lower())
        page += 1
    return members


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def extract_github_username(custom_field_responses: list[dict]) -> str | None:
    """Extract GitHub username from Whop custom field responses."""
    for field in custom_field_responses:
        question = field.get("question", "").strip()
        if GITHUB_USERNAME_FIELD.lower() in question.lower():
            answer = field.get("answer", "").strip().lstrip("@")
            if answer:
                return answer
    return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok", "service": "membership-gateway", "version": "1.0.0"}


@app.post("/webhooks/whop")
async def handle_webhook(request: Request):
    """Process Whop webhook events for membership changes."""
    body = await request.body()
    headers = dict(request.headers)

    # Verify signature
    if not verify_webhook(body, headers):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    payload = json.loads(body)
    event_type = payload.get("type", "")
    data = payload.get("data", {})
    membership_id = data.get("id", "unknown")

    log.info(f"Webhook received: {event_type} membership={membership_id}")

    # Extract GitHub username from custom fields
    custom_fields = data.get("custom_field_responses", [])
    github_username = extract_github_username(custom_fields)

    user_info = data.get("user", {})
    whop_username = user_info.get("username", "unknown")
    whop_email = user_info.get("email", "unknown")

    if event_type == "membership.activated":
        if not github_username:
            msg = (
                f"Membership activated for {whop_username} ({whop_email}) "
                f"but no GitHub username provided. Membership: {membership_id}"
            )
            log.warning(msg)
            await notify_slack(f":warning: {msg}")
            await audit_log(membership_id, "", "activated_no_github", msg)
            return JSONResponse({"status": "ok", "warning": "no_github_username"})

        result = await add_to_team(github_username)
        state = result.get("state", "unknown")
        msg = (
            f"Added `{github_username}` to team (state={state}). "
            f"Whop user: {whop_username} ({whop_email}), membership: {membership_id}"
        )
        await audit_log(membership_id, github_username, "activated", msg)
        await notify_slack(f":white_check_mark: {msg}")
        return JSONResponse({"status": "ok", "action": "added", "github_username": github_username, "state": state})

    elif event_type == "membership.deactivated":
        if not github_username:
            msg = (
                f"Membership deactivated for {whop_username} ({whop_email}) "
                f"but no GitHub username to remove. Membership: {membership_id}"
            )
            log.warning(msg)
            await notify_slack(f":warning: {msg}")
            await audit_log(membership_id, "", "deactivated_no_github", msg)
            return JSONResponse({"status": "ok", "warning": "no_github_username"})

        await remove_from_team(github_username)
        msg = (
            f"Removed `{github_username}` from team. "
            f"Whop user: {whop_username} ({whop_email}), membership: {membership_id}"
        )
        await audit_log(membership_id, github_username, "deactivated", msg)
        await notify_slack(f":x: {msg}")
        return JSONResponse({"status": "ok", "action": "removed", "github_username": github_username})

    elif event_type == "payment.failed":
        msg = (
            f"Payment failed for {whop_username} ({whop_email}), "
            f"membership: {membership_id}. Waiting for deactivation event."
        )
        log.info(msg)
        await notify_slack(f":money_with_wings: {msg}")
        return JSONResponse({"status": "ok", "action": "payment_failed_logged"})

    else:
        log.info(f"Ignoring event type: {event_type}")
        return JSONResponse({"status": "ok", "action": "ignored", "event_type": event_type})


@app.get("/sync")
async def sync_memberships():
    """Reconcile Whop active memberships with GitHub team membership.

    Scheduled daily via Cloud Scheduler. Ensures consistency:
    - Adds Whop members missing from GitHub team
    - Removes GitHub team members not active on Whop
    """
    if not WHOP_API_KEY:
        raise HTTPException(status_code=500, detail="WHOP_API_KEY not configured")

    log.info("Starting membership sync...")
    results = {"added": [], "removed": [], "errors": [], "skipped_no_github": []}

    # 1. Get active Whop memberships and their GitHub usernames
    whop_members: dict[str, str] = {}  # github_username -> membership_id
    cursor = None
    while True:
        params = {"first": 100}
        if cursor:
            params["after"] = cursor
        r = await whop.get("/memberships", params=params)
        if r.status_code != 200:
            log.error(f"Whop API error listing memberships: {r.status_code}")
            raise HTTPException(status_code=502, detail="Whop API error")
        data = r.json()
        memberships = data.get("data", [])
        if not memberships:
            break
        for m in memberships:
            status = m.get("status", "")
            if status not in ("active", "trialing"):
                continue
            gh_user = extract_github_username(m.get("custom_field_responses", []))
            if gh_user:
                whop_members[gh_user.lower()] = m.get("id", "")
            else:
                results["skipped_no_github"].append(m.get("id", ""))
        page_info = data.get("pagination", {})
        if page_info.get("has_next_page"):
            cursor = page_info.get("end_cursor")
        else:
            break

    # 2. Get current GitHub team members
    github_members = await get_team_members()

    # 3. Add missing members (on Whop but not on GitHub)
    for gh_user, mem_id in whop_members.items():
        if gh_user not in github_members:
            try:
                await add_to_team(gh_user)
                results["added"].append(gh_user)
                await audit_log(mem_id, gh_user, "sync_added", "Added during daily sync")
            except Exception as e:
                results["errors"].append({"user": gh_user, "error": str(e)})

    # 4. Remove stale members (on GitHub but not on Whop)
    # Exclude org owners/admins from removal
    org_owners = set()
    r = await github.get(f"/orgs/{ORG}/members", params={"role": "admin", "per_page": 100})
    if r.status_code == 200:
        for m in r.json():
            org_owners.add(m["login"].lower())

    for gh_user in github_members:
        if gh_user not in whop_members and gh_user not in org_owners:
            try:
                await remove_from_team(gh_user)
                results["removed"].append(gh_user)
                await audit_log("", gh_user, "sync_removed", "Removed during daily sync")
            except Exception as e:
                results["errors"].append({"user": gh_user, "error": str(e)})

    summary = (
        f"Sync complete: {len(results['added'])} added, {len(results['removed'])} removed, "
        f"{len(results['errors'])} errors, {len(results['skipped_no_github'])} skipped (no GitHub)"
    )
    log.info(summary)
    await notify_slack(f":arrows_counterclockwise: {summary}")

    return JSONResponse({"status": "ok", **results, "summary": summary})


