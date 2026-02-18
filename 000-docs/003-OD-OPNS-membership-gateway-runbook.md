# Membership Gateway — Operations Runbook

> **Version:** 1.0
> **Updated:** 2026-02-17
> **Service:** membership-gateway (Cloud Run)
> **Repo:** `products/membership-gateway/`

---

## Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Is the service up? |
| `/webhooks/whop` | POST | Receives Whop events (auto-called) |
| `/sync` | GET | Force reconciliation of Whop ↔ GitHub |

---

## Service Health Check

```bash
# Check if service is responding
curl https://CLOUD_RUN_URL/health

# Expected response:
# {"status":"ok","service":"membership-gateway","version":"1.0.0"}

# Check Cloud Run deployment status
gcloud run services describe membership-gateway \
  --region=us-central1 \
  --project=YOUR_PROJECT \
  --format="value(status.conditions[0].type, status.conditions[0].status)"

# View live logs (last 100 lines)
gcloud run services logs read membership-gateway \
  --region=us-central1 \
  --project=YOUR_PROJECT \
  --limit=100
```

---

## Manually Add a Member

Use when: webhook failed, user provided GitHub username late, manual override.

```bash
# Add a GitHub user to the members team
gh api /orgs/intent-solutions-io/teams/members/memberships/GITHUB_USERNAME \
  -X PUT -f role=member

# Verify they were added
gh api /orgs/intent-solutions-io/teams/members/members \
  --jq '.[].login'
```

---

## Manually Remove a Member

Use when: chargeback, abuse, manual cancellation.

```bash
# Remove a GitHub user from the members team
gh api /orgs/intent-solutions-io/teams/members/memberships/GITHUB_USERNAME \
  -X DELETE

# Verify removal
gh api /orgs/intent-solutions-io/teams/members/members --jq '.[].login'
```

---

## Force Sync

Reconciles Whop active memberships vs GitHub team. Adds missing members, removes stale ones.

```bash
# Trigger sync via HTTP (daily at 3am via Cloud Scheduler)
curl -X GET https://CLOUD_RUN_URL/sync

# Expected response shows added/removed/errors:
# {"status":"ok","added":[],"removed":[],"errors":[],"summary":"Sync complete: 0 added, 0 removed, 0 errors"}
```

---

## View Audit Log (Firestore)

All membership events are logged to Firestore collection `membership_audit`.

**Via Cloud Console:**
1. Go to Firestore → `membership_audit` collection
2. Filter by `action` field: `activated`, `deactivated`, `sync_added`, `sync_removed`
3. Look for `activated_no_github` or `deactivated_no_github` — these need manual follow-up

**Via gcloud:**
```bash
# Not easily queryable from CLI — use Cloud Console or set up a query script
```

---

## Deploy / Redeploy

```bash
# Deploy from source (builds + deploys)
cd /home/jeremy/000-projects/products/membership-gateway
GCP_PROJECT=your-project ./scripts/deploy.sh

# Quick redeploy with same image (e.g., after secret rotation)
gcloud run deploy membership-gateway \
  --image=gcr.io/YOUR_PROJECT/membership-gateway \
  --region=us-central1 \
  --project=YOUR_PROJECT
```

---

## Update a Secret

```bash
# Rotate a secret value
echo -n "NEW_VALUE" | gcloud secrets versions add SECRET_NAME \
  --data-file=- \
  --project=YOUR_PROJECT

# Redeploy to pick up new secret value
gcloud run deploy membership-gateway \
  --source . \
  --region=us-central1 \
  --project=YOUR_PROJECT
```

Secrets:
- `whop-webhook-secret` — from Whop developer settings
- `github-token-members` — GitHub PAT with `admin:org`
- `whop-api-key` — from Whop API settings
- `slack-webhook-url` — from Slack incoming webhooks

---

## Webhook Verification

The gateway verifies Whop webhook signatures using Standard Webhooks spec (HMAC-SHA256).

If you see `401` responses in logs:
1. Check `WHOP_WEBHOOK_SECRET` matches what Whop shows in developer settings
2. If rotated in Whop, update Secret Manager and redeploy

To **temporarily disable** verification (debugging only):
- Set `WHOP_WEBHOOK_SECRET=""` env var → gateway logs a warning but processes all requests
- **Re-enable immediately after debugging**

---

## Register / Update Webhook URL

Run when: new deployment, URL changed, webhook needs recreation.

```bash
# Get current Cloud Run URL
gcloud run services describe membership-gateway \
  --region=us-central1 --project=YOUR_PROJECT \
  --format="value(status.url)"

# Register webhook in Whop
cd /home/jeremy/000-projects/products/membership-gateway
WHOP_API_KEY=... python scripts/register_webhook.py https://THE_CLOUD_RUN_URL
```

---

## Incident Response

### Gateway Not Responding

```bash
# 1. Check Cloud Run status
gcloud run services describe membership-gateway --region=us-central1 --project=YOUR_PROJECT

# 2. Check recent logs for crash cause
gcloud run services logs read membership-gateway --region=us-central1 --project=YOUR_PROJECT --limit=50

# 3. Rollback to previous revision if needed
gcloud run services update-traffic membership-gateway \
  --to-revisions=PREVIOUS_REVISION=100 \
  --region=us-central1 --project=YOUR_PROJECT
```

### Webhook Events Missed

Whop retries failed webhooks for 24 hours. If gateway was down:
1. Check Whop developer portal → webhook logs for failed deliveries
2. Manually replay if needed, or trigger `/sync` to catch up

### Member Has Access But Shouldn't

```bash
# Immediately remove
gh api /orgs/intent-solutions-io/teams/members/memberships/GITHUB_USERNAME -X DELETE

# Log the incident in Firestore or here for reference
```

### GitHub API Down / Rate Limited

```bash
# Check GitHub status
curl https://www.githubstatus.com/api/v2/status.json | python3 -m json.tool | grep status

# Check rate limit remaining (auth'd)
gh api /rate_limit --jq '.rate.remaining'

# Gateway returns 502 when GitHub is down — Whop will retry automatically
```

---

## Testing a Webhook Locally

```bash
# Start gateway locally
cd /home/jeremy/000-projects/products/membership-gateway
WHOP_WEBHOOK_SECRET="" GITHUB_TOKEN="ghp_..." WHOP_API_KEY="" SLACK_WEBHOOK_URL="" \
  .venv/bin/uvicorn main:app --reload --port 8080

# Send a test activation event (signature verification disabled)
curl -X POST http://localhost:8080/webhooks/whop \
  -H "Content-Type: application/json" \
  -d '{
    "id": "test_001",
    "type": "membership.activated",
    "api_version": "v1",
    "timestamp": "2026-01-01T00:00:00Z",
    "data": {
      "id": "mem_test",
      "status": "active",
      "custom_field_responses": [
        {"id": "f1", "question": "GitHub Username", "answer": "octocat"}
      ],
      "user": {"id": "u1", "username": "testuser", "email": "test@example.com"},
      "company": {"id": "co1", "title": "Intent Solutions"},
      "plan": {"id": "plan_1"},
      "product": {"id": "prod_1", "title": "All-Access"},
      "cancel_at_period_end": false,
      "created_at": "2026-01-01T00:00:00Z",
      "updated_at": "2026-01-01T00:00:00Z",
      "metadata": {},
      "payment_collection_paused": false
    }
  }'
```

---

## Cloud Scheduler

Daily sync at 3am UTC. Created with:

```bash
gcloud scheduler jobs create http membership-sync \
  --schedule="0 3 * * *" \
  --uri="https://CLOUD_RUN_URL/sync" \
  --http-method=GET \
  --project=YOUR_PROJECT \
  --location=us-central1
```

Check job history:
```bash
gcloud scheduler jobs describe membership-sync \
  --project=YOUR_PROJECT \
  --location=us-central1
```

Trigger manually:
```bash
gcloud scheduler jobs run membership-sync \
  --project=YOUR_PROJECT \
  --location=us-central1
```
