# Membership Gateway — First Deploy Checklist

> **Purpose:** One-time setup checklist for deploying membership-gateway to Cloud Run
> **Estimated time:** 45-60 minutes
> **Prerequisites:** `gcloud` CLI authenticated, `gh` CLI authenticated as org owner

---

## Phase 1: GCP Prerequisites

- [ ] Decide which GCP project to use (or create a new one)
  ```bash
  gcloud projects list | grep intent
  ```

- [ ] Enable required APIs
  ```bash
  GCP_PROJECT=your-project-id
  gcloud services enable \
    run.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    cloudscheduler.googleapis.com \
    firestore.googleapis.com \
    --project=$GCP_PROJECT
  ```

- [ ] Create Firestore database (if not exists)
  ```bash
  gcloud firestore databases create \
    --location=nam5 \
    --project=$GCP_PROJECT
  ```

---

## Phase 2: GitHub Token

- [ ] Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
- [ ] Generate new token with scope: `admin:org`
- [ ] Token description: "membership-gateway Cloud Run"
- [ ] Copy token value — save as `GITHUB_TOKEN_VALUE`

---

## Phase 3: Whop Setup

- [ ] Create the membership product (run the script):
  ```bash
  cd /home/jeremy/000-projects/products/membership-gateway
  WHOP_API_KEY=$(pass whop/api-key) \
    /home/jeremy/.venvs/whop/bin/python scripts/create_whop_membership.py
  ```
  Note the product ID and plan IDs from output.

- [ ] Go to Whop Dashboard → your product → Checkout settings
- [ ] Add custom field: **"GitHub Username"** (required text field)
- [ ] Set up welcome message (from `002-DR-MANL-operations-manual.md` section 4 or plan doc)

- [ ] Get webhook secret: Whop Dashboard → Developer → Webhooks
  - Save as `WHOP_WEBHOOK_SECRET_VALUE`

---

## Phase 4: Populate Secrets

```bash
GCP_PROJECT=your-project-id

# Whop webhook secret
echo -n "WHOP_WEBHOOK_SECRET_VALUE" | gcloud secrets versions add whop-webhook-secret \
  --data-file=- --project=$GCP_PROJECT

# GitHub token
echo -n "GITHUB_TOKEN_VALUE" | gcloud secrets versions add github-token-members \
  --data-file=- --project=$GCP_PROJECT

# Whop API key
echo -n "WHOP_API_KEY_VALUE" | gcloud secrets versions add whop-api-key \
  --data-file=- --project=$GCP_PROJECT

# Slack webhook URL (optional — skip if not using Slack)
echo -n "SLACK_WEBHOOK_URL_VALUE" | gcloud secrets versions add slack-webhook-url \
  --data-file=- --project=$GCP_PROJECT
```

---

## Phase 5: Deploy to Cloud Run

```bash
cd /home/jeremy/000-projects/products/membership-gateway
GCP_PROJECT=your-project-id ./scripts/deploy.sh
```

- [ ] Deployment succeeds
- [ ] Note the Cloud Run URL from output
- [ ] Health check passes:
  ```bash
  curl https://YOUR_CLOUD_RUN_URL/health
  # Expected: {"status":"ok","service":"membership-gateway","version":"1.0.0"}
  ```

---

## Phase 6: Register Webhook in Whop

```bash
cd /home/jeremy/000-projects/products/membership-gateway
WHOP_API_KEY=$(pass whop/api-key) \
  /home/jeremy/.venvs/whop/bin/python scripts/register_webhook.py \
  https://YOUR_CLOUD_RUN_URL
```

- [ ] Webhook registered successfully (note the webhook ID)
- [ ] Events registered: `membership.activated`, `membership.deactivated`, `payment.failed`

---

## Phase 7: Cloud Scheduler

```bash
gcloud scheduler jobs create http membership-sync \
  --schedule="0 3 * * *" \
  --uri="https://YOUR_CLOUD_RUN_URL/sync" \
  --http-method=GET \
  --project=$GCP_PROJECT \
  --location=us-central1
```

- [ ] Scheduler job created
- [ ] Trigger a test run:
  ```bash
  gcloud scheduler jobs run membership-sync \
    --project=$GCP_PROJECT --location=us-central1
  ```
- [ ] Sync completed successfully

---

## Phase 8: End-to-End Test

- [ ] Make a test purchase on Whop (use real payment method, then refund)
  - Enter your own GitHub username (one that's NOT already an org member)
- [ ] Wait ~30 seconds, check:
  ```bash
  gh api /orgs/intent-solutions-io/teams/members/members --jq '.[].login'
  # Your test username should appear
  ```
- [ ] Accept GitHub org invitation (check email)
- [ ] Verify repo access:
  ```bash
  git clone https://github.com/intent-solutions-io/crypto-agent.git /tmp/test-clone
  ls /tmp/test-clone
  rm -rf /tmp/test-clone
  ```
- [ ] Cancel the test membership in Whop
- [ ] Wait ~30 seconds, verify removal:
  ```bash
  gh api /orgs/intent-solutions-io/teams/members/members --jq '.[].login'
  # Your test username should be gone
  ```
- [ ] Check Firestore audit log shows all 4 events
- [ ] Check Slack received notifications (if configured)
- [ ] Issue refund for the test purchase in Whop

---

## Phase 9: Update Config Files

- [ ] Update `003-OD-OPNS-membership-gateway-runbook.md` with actual Cloud Run URL
- [ ] Update `002-DR-MANL-operations-manual.md` section 2 with actual Cloud Run URL
- [ ] Update `CLAUDE.md` with actual GCP project ID

---

## Rollback Plan

If anything breaks during deploy:

```bash
# List revisions
gcloud run revisions list --service=membership-gateway \
  --region=us-central1 --project=$GCP_PROJECT

# Route 100% traffic to previous revision
gcloud run services update-traffic membership-gateway \
  --to-revisions=PREVIOUS_REVISION_ID=100 \
  --region=us-central1 --project=$GCP_PROJECT
```

Manual fallback while gateway is down: use `gh` CLI to add/remove members directly (see `003-OD-OPNS-membership-gateway-runbook.md`).
