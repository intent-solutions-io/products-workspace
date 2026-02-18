# New Member Onboarding Guide

> **Audience:** Internal reference — what happens when someone buys, and what to send them
> **Updated:** 2026-02-17

---

## What Happens Automatically (No Action Needed)

1. Customer completes Whop checkout → enters GitHub username
2. Whop fires webhook → gateway adds them to `members` team
3. GitHub sends org invite email to customer's GitHub-registered email
4. Customer accepts → has read access to all 4 repos

**You receive a Slack DM for each event.**

---

## Whop Welcome Message

Set this in Whop Dashboard → Product → Post-purchase message.

---

```
Welcome to Intent Solutions!

You now have access to all 4 AI crypto agents:

• Crypto Portfolio Agent — portfolio monitoring across EVM chains
• AI Agent Wallet — wallet infrastructure for AI agents with guardrails
• Vincent DeFi Agent — DeFi trading with cryptographic guardrails on Base
• Derivatives Signal Agent — AI-powered derivatives analysis (Bybit + Coinglass)

GET STARTED:
1. Check your GitHub email for an organization invitation from intent-solutions-io
2. Accept the invitation (expires in 7 days)
3. Clone any agent: git clone https://github.com/intent-solutions-io/crypto-agent.git
4. Follow the README and run `doctor` to verify your setup

NEED HELP SETTING UP?
• The AI setup wizard in Claude Code: /agent-setup
• Each repo has a SETUP-PROMPT.md — paste it into any AI assistant

QUESTIONS?
Email jeremy@intentsolutions.io — I respond within 48 hours.

Your membership includes all 4 agents, all updates, and any new agents released while you're subscribed.
```

---

## Common Support Responses

### "I didn't get the GitHub invitation"

```
Hi [name],

Your GitHub invitation should arrive at the email address on your GitHub account (not necessarily the email you used for Whop).

1. Check the email linked to your GitHub account
2. Also check github.com/notifications — invitations appear there
3. If it's been more than 30 minutes and nothing arrived, reply with your GitHub username and I'll re-send

Jeremy
```

### "I don't have a GitHub account"

```
Hi [name],

No problem! GitHub is free. Here's how to set it up:

1. Go to github.com and create a free account (takes 2 minutes)
2. Reply with your new GitHub username
3. I'll send you the organization invitation

Jeremy
```

### "I entered the wrong GitHub username"

```
Hi [name],

Got it. What's your correct GitHub username? I'll update it right away.

Jeremy
```

Then manually:
```bash
# Remove old (if they had access)
gh api /orgs/intent-solutions-io/teams/members/memberships/OLD_USERNAME -X DELETE

# Add correct one
gh api /orgs/intent-solutions-io/teams/members/memberships/CORRECT_USERNAME \
  -X PUT -f role=member
```

### "I cancelled by mistake"

```
Hi [name],

No problem — just re-subscribe through your Whop dashboard and you'll get access back immediately.

Jeremy
```

### "The agent isn't working"

```
Hi [name],

Let's get you sorted. Can you:

1. Run the doctor command: python doctor.py --config config.yaml
2. Paste the output here

That'll show exactly what's misconfigured.

Jeremy
```

### Refund Request (within 7 days)

Process via Whop dashboard. Access will be revoked automatically via webhook.

```
Hi [name],

I've processed your refund. You should see it within 3-5 business days depending on your bank.

Let me know if there's anything I could have done better.

Jeremy
```

---

## Onboarding Checklist (Internal)

For each new member, within 24 hours:

- [ ] Slack notification received ✓ (automatic)
- [ ] If `no_github_username` warning: email member asking for GitHub username
- [ ] If invitation expired (after 7 days without acceptance): send reminder
- [ ] Check Firestore audit log shows `activated` event

---

## Member Lifecycle States

```
Purchase → [activated] → GitHub invite sent → Invite accepted → Active member
                ↓
           [no_github] → Owner follow-up → Manual add when username confirmed

Active member → Cancel/Lapse → [deactivated] → GitHub access removed
             → Re-subscribe → [activated] → GitHub access restored
```
