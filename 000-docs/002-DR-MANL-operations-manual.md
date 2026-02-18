# Intent Solutions — Operations Manual

> **Version:** 1.0
> **Updated:** 2026-02-17
> **Owner:** Jeremy
> **Audience:** Internal (Jeremy + any future team member)

---

## 1. Business Overview

**What we sell:** AI crypto agents delivered via GitHub repo access.
**How we sell it:** Whop All-Access membership ($29/mo, $249/yr, $199 lifetime).
**Who buys it:** Crypto traders and developers who want prebuilt AI tooling.

### Products

| Agent | Repo | What it does |
|-------|------|-------------|
| Crypto Portfolio Agent | `intent-solutions-io/crypto-agent` | Read-only EVM wallet monitoring, alerts, reports |
| AI Agent Wallet | `intent-solutions-io/ai-agent-wallet` | REST API wallet infra with guardrails |
| Vincent DeFi Agent | `intent-solutions-io/vincent-defi-agent` | DeFi trading on Base with cryptographic guardrails |
| Derivatives Signal Agent | `intent-solutions-io/derivatives-signal-agent` | Claude AI derivatives scoring from Bybit + Coinglass |

### Pricing

| Plan | Price | Notes |
|------|-------|-------|
| Monthly | $29/mo | Core offering |
| Annual | $249/yr | ~28% discount, reduces churn |
| Lifetime | $199 | Cap at 50 seats |

---

## 2. Infrastructure Map

```
Whop (billing/checkout)
    └── membership-gateway (Cloud Run)    ← webhook receiver
            ├── GitHub org (intent-solutions-io)
            │   └── members team (auto-managed)
            │       ├── crypto-agent (private)
            │       ├── ai-agent-wallet (private)
            │       ├── vincent-defi-agent (private)
            │       └── derivatives-signal-agent (private)
            ├── Firestore (audit log)
            └── Slack (owner notifications)
```

### Key URLs & IDs

| Resource | Value |
|----------|-------|
| GitHub Org | `intent-solutions-io` |
| GitHub Team | `members` (slug) |
| Cloud Run service | `membership-gateway` (us-central1) |
| Whop page | https://whop.com/intentsolutions |
| Gumroad store | https://intentsolutions.gumroad.com |
| Support email | jeremy@intentsolutions.io |

---

## 3. Day-to-Day Operations

### Normal Day (Nothing to Do)

The system is fully automated. Whop fires webhooks on purchase/cancellation, the gateway handles GitHub team membership. Firestore logs everything. If Slack is configured, you get DMs for every event.

### Weekly Check (5 min)

```bash
# Verify gateway is healthy
curl https://membership-gateway-xxx.a.run.app/health

# Trigger manual sync to catch drift
curl https://membership-gateway-xxx.a.run.app/sync

# Scan Firestore audit log for errors (Cloud Console)
# Filter: action contains "error" or "no_github"
```

### Monthly Check (15 min)

- Review Whop dashboard: active member count, churn rate, revenue
- Check Cloud Run logs for any repeated errors
- Verify Cloud Scheduler ran the 3am sync (check logs)
- Update any agent versions with new releases

---

## 4. New Member Flow

1. Customer purchases on Whop, enters GitHub username at checkout
2. Whop fires `membership.activated` webhook to gateway
3. Gateway extracts GitHub username from `custom_field_responses`
4. Gateway calls `PUT /orgs/intent-solutions-io/teams/members/memberships/{username}`
5. GitHub sends org invitation email to member
6. Member accepts invite (7-day expiry; re-invite on request)
7. Member can now clone all 4 repos
8. You receive Slack DM: "Added `username` to team"

**If GitHub username missing:** Gateway logs a warning, sends you Slack DM. You manually add them via:
```bash
gh api /orgs/intent-solutions-io/teams/members/memberships/THEIR_USERNAME \
  -X PUT -f role=member
```

---

## 5. Cancellation Flow

1. Member cancels on Whop OR payment fails enough times
2. Whop fires `membership.deactivated` webhook
3. Gateway removes member from `members` GitHub team
4. Member loses read access to all 4 repos immediately
5. You receive Slack DM: "Removed `username` from team"

Member retains any code they already cloned. They can re-subscribe to get access again.

---

## 6. Edge Cases & Resolutions

| Situation | What to Do |
|-----------|------------|
| Member never accepted GitHub invite | Re-invite: `gh api /orgs/intent-solutions-io/teams/members/memberships/USERNAME -X PUT -f role=member` |
| Wrong GitHub username provided | Member emails support → you manually update. Future: support form |
| Member changed GitHub username | Support request → remove old, add new |
| Webhook not firing | Check Whop webhook settings, gateway health, Cloud Run logs |
| Gateway down | Cloud Run auto-restarts. Check: `gcloud run services describe membership-gateway` |
| Drift (GitHub ≠ Whop) | Hit `/sync` endpoint. Runs daily at 3am automatically |
| Refund requested | Process in Whop. Webhook fires deactivated → access removed automatically |

---

## 7. Secrets & Credentials

All stored in Google Secret Manager. **Never in code or git.**

| Secret Name | Purpose | How to Rotate |
|-------------|---------|---------------|
| `whop-webhook-secret` | Verify webhook signatures | Get new secret from Whop → update SM → redeploy |
| `github-token-members` | GitHub PAT for team management | Rotate in GitHub → update SM → redeploy |
| `whop-api-key` | Whop API (sync endpoint) | Rotate in Whop → update SM → redeploy |
| `slack-webhook-url` | Owner notifications | Get new URL from Slack → update SM → redeploy |

```bash
# Update a secret value
echo -n "new-secret-value" | gcloud secrets versions add SECRET_NAME \
  --data-file=- --project=YOUR_PROJECT

# After updating, redeploy Cloud Run to pick up new value
gcloud run deploy membership-gateway --region=us-central1 --project=YOUR_PROJECT
```

---

## 8. GitHub Token Requirements

The `github-token-members` PAT needs:
- `admin:org` scope → manage team membership
- The token owner must be an org owner/admin

Classic PAT works. Fine-grained PAT needs explicit org permissions.

---

## 9. Scaling Thresholds

| Members | Action |
|---------|--------|
| 50 | Close Lifetime plan if still open |
| 100 | Review costs: GitHub ($4/seat) + Cloud Run |
| 250 | Consider raising Annual to $299/yr |
| 500 | Evaluate Docker-only delivery to eliminate GitHub seat cost |

---

## 10. Revenue Tracking

Track monthly in a spreadsheet or Whop dashboard:

```
MRR = (monthly members × $29) + (annual members × $249/12)
GitHub cost = active_members × $4/month
Cloud Run = ~$10-15/month
Net = MRR - GitHub - Cloud Run - Whop fee (3%)
```

---

## 11. Support Policy

Support is **not included** by default. Current channels:
- Email: jeremy@intentsolutions.io
- Response target: 48-72 hours for paying members

Paid support add-ons (optional upsell):
- Onboarding Call: $150 (60 min screenshare)
- Managed Deploy: $300-400 (deploy to buyer's infra)
- Support Subscription: $200/mo (4 hrs/mo, 48hr response)

---

## 12. License / Legal

- Products are proprietary. Buyers get access, not ownership.
- Non-exclusive, non-transferable commercial license
- Access is tied to active subscription (cancel = lose access)
- 7-day defect warranty for reproducible bugs
- No warranty for losses from trading or using agents
- See `LICENSE.md` in each product repo

---

## 13. Emergency Contacts

| Situation | Action |
|-----------|--------|
| Cloud Run down | GCP Console → Cloud Run → membership-gateway → revisions |
| GitHub API down | Check status.githubstatus.com. Queued actions resume when API recovers. |
| Whop outage | Check status.whop.com. Webhooks replay when restored. |
| Data breach | Rotate all secrets immediately (section 7), notify affected users |
