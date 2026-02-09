# Product Audit, Packaging & Anti-Chargeback Plan

> **Date:** 2026-02-09
> **Scope:** Crypto Portfolio Agent + AI Agent Wallet
> **Purpose:** Build spec truth table, Whop A/B/C packaging, pricing tiers, dispute prevention

---

## 1. Build Spec — Features vs Non-Features

### Crypto Portfolio Agent

| # | Claimed Feature | Actual Status | Evidence | Sell It? |
|---|----------------|---------------|----------|----------|
| 1 | Native + ERC-20 balance tracking | **SHIPPED** | `tools/balance_tracker.py` (164 lines), hardcoded COMMON_TOKENS for 5 chains | Yes |
| 2 | Price fetching (CoinGecko) | **SHIPPED** | `tools/price_fetcher.py` (138 lines), module-level cache | Yes |
| 3 | DeFi — Aave V3 | **SHIPPED** | `tools/defi_tracker.py` L86-132, The Graph subgraphs | Yes |
| 4 | DeFi — Uniswap V3 LP | **SHIPPED** | `tools/defi_tracker.py` L139-167 | Yes |
| 5 | DeFi — Lido stETH | **SHIPPED** | `tools/defi_tracker.py` L170-190, direct RPC | Yes |
| 6 | DeFi — Compound V3 | **STUBBED** | Returns empty list, explicit stub comment | **No — remove from listing** |
| 7 | Alert — Price threshold | **SHIPPED** | `services/alert_engine.py` L105-147, above/below | Yes |
| 8 | Alert — Balance change | **SHIPPED** | `services/alert_engine.py` L149-183, percentage-based | Yes |
| 9 | Alert — Whale movement | **MISSING** | Defined in schema, no evaluation function | **No — remove from listing** |
| 10 | Alert — Liquidation risk | **SHIPPED** | `services/alert_engine.py` L185-214, health factor | Yes |
| 11 | Alert — Gas threshold | **SHIPPED** | `services/alert_engine.py` L216-258 | Yes |
| 12 | Alert — Transaction detected | **SHIPPED** | `services/alert_engine.py` L260-293 | Yes |
| 13 | Notification — Webhook | **SHIPPED** | `services/notification_dispatcher.py` L72-103 | Yes |
| 14 | Notification — Email (SMTP) | **SHIPPED** | `services/notification_dispatcher.py` L105-149 | Yes |
| 15 | Notification — Telegram | **SHIPPED** | `services/notification_dispatcher.py` L151-189 | Yes |
| 16 | Notification — Slack | **SHIPPED** | `services/notification_dispatcher.py` L191-219 | Yes |
| 17 | JSON portfolio reports | **SHIPPED** | `services/report_generator.py` (317 lines), risk indicators | Yes |
| 18 | RPC client (circuit breaker, rate limit, cache, fallback) | **SHIPPED** | `tools/rpc_client.py`, stale data flag | Yes |
| 19 | Pydantic config validation | **SHIPPED** | `config/schema.py` + `config/loader.py` | Yes |
| 20 | Docker container (non-root) | **SHIPPED** | `Dockerfile` (51 lines), healthcheck | Yes |
| 21 | Doctor acceptance command | **SHIPPED** | `doctor.py` (287 lines), 5 checks, JSON output | Yes |
| 22 | Continuous monitoring loop | **SHIPPED** | `main.py` --interval flag | Yes |
| 23 | Alert evaluation in main loop | **STUBBED** | `main.py` L109-110 placeholder comment | **Fix before selling** |
| 24 | CoinMarketCap fallback | **MISSING** | Documented in header, never implemented | **No — remove from listing** |
| 25 | PDF reports | **STUBBED** | Config field exists, no generation code | No — Phase 2 |
| 26 | Tests (pytest) | **SHIPPED** | 4 test files, 11+ test cases, no network calls | Yes |
| 27 | CI (GitHub Actions) | **SHIPPED** | Lint + test + Docker build | Yes |

#### Crypto Agent: Honest Feature Count

- **Shipped & sellable:** 22 features
- **Must fix before selling:** 1 (alert evaluation wiring in main.py)
- **Must remove from listing:** 3 (whale movement, Compound V3, CoinMarketCap fallback)
- **Honest alert count:** 5 (not 6 — drop whale movement)

---

### AI Agent Wallet

| # | Claimed Feature | Actual Status | Evidence | Sell It? |
|---|----------------|---------------|----------|----------|
| 1 | Create wallet via API | **SHIPPED** | `main.py` POST /wallets, fresh keypair | Yes |
| 2 | Import wallet (private key) | **SHIPPED** | `main.py` POST /wallets/import | Yes |
| 3 | Multi-wallet support | **SHIPPED** | List, filter by active | Yes |
| 4 | Deactivate wallet | **SHIPPED** | DELETE /wallets/{id}, soft delete | Yes |
| 5 | Send native tokens | **SHIPPED** | `transaction_engine.py` (326 lines), EIP-1559 | Yes |
| 6 | Contract interactions (calldata) | **SHIPPED** | `data` parameter supported | Yes |
| 7 | Gas estimation | **SHIPPED** | `eth.estimate_gas` fallback | Yes |
| 8 | Guardrail — Per-TX limit | **SHIPPED** | `guardrails.py` L86-91 | Yes |
| 9 | Guardrail — Daily limit | **SHIPPED** | `guardrails.py` L112-118, spending_tracker table | Yes |
| 10 | Guardrail — Monthly limit | **SHIPPED** | `guardrails.py` L121-127 | Yes |
| 11 | Guardrail — Address whitelist | **SHIPPED** | `guardrails.py` L94-100 | Yes |
| 12 | Guardrail — Contract whitelist | **SHIPPED** | `guardrails.py` L103-109 | Yes |
| 13 | Guardrail — Large-TX delay | **STUBBED** | Config only, no runtime check | **Fix or remove** |
| 14 | Guardrail — Kill switch | **SHIPPED** | `guardrails.py` L32-43, in-memory (non-persistent) | Yes (with caveat) |
| 15 | Guardrail — Cooldown | **SHIPPED** | `guardrails.py` L130-140 | Yes |
| 16 | Encrypted key storage (Fernet) | **SHIPPED** | `wallet_manager.py` L26-40 | Yes |
| 17 | Audit logging | **SHIPPED** | `audit_log.py` (193 lines), all events | Yes |
| 18 | REST API + OpenAPI docs | **SHIPPED** | FastAPI auto-docs at /docs | Yes |
| 19 | Health + readiness endpoints | **SHIPPED** | /health and /ready | Yes |
| 20 | Multi-chain EVM (5 chains) | **SHIPPED** | Ethereum, Polygon, Arbitrum, Base, Optimism | Yes |
| 21 | Sepolia testnet | **PARTIAL** | In config.example.yaml, not code defaults | Yes (with docs) |
| 22 | Docker setup | **SHIPPED** | Dockerfile + docker-compose, non-root, healthcheck | Yes |
| 23 | Tests (pytest) | **SHIPPED** | 3 files, 525 lines | Yes |
| 24 | API authentication | **MISSING** | Model exists, no middleware | No — don't claim |
| 25 | Rate limiting | **MISSING** | No middleware | No — don't claim |

#### AI Agent Wallet: Honest Feature Count

- **Shipped & sellable:** 21 features
- **Must fix or remove:** 1 (large-tx delay)
- **Honest guardrail count:** 7 working (not 8 — drop large-tx delay or implement it)
- **Empty files to fill:** CHANGELOG.md, LICENSE.md, CLAUDE.md

---

### Non-Features (Do NOT Claim)

These do not exist in either product. Never mention in listings:

| Non-Feature | Product | Why Not |
|-------------|---------|---------|
| Trade execution | Crypto Agent | Read-only by design |
| Whale movement alerts | Crypto Agent | Schema only, no code |
| Compound V3 DeFi | Crypto Agent | Stub returns empty |
| CoinMarketCap fallback | Crypto Agent | Header comment only |
| PDF reports | Crypto Agent | Config field, no generator |
| Large-TX delay enforcement | Agent Wallet | Config only, no runtime check |
| API key authentication | Agent Wallet | Model exists, no middleware |
| Rate limiting | Agent Wallet | Not implemented |
| Kill switch persistence | Agent Wallet | Resets on restart |
| IP address logging | Agent Wallet | Audit field, never populated |

---

## 2. Whop Packaging — A/B/C Model

### Tier A: Starter — $20

**Both products at this tier.** One-time purchase, self-service.

| Attribute | Crypto Portfolio Agent | AI Agent Wallet |
|-----------|----------------------|-----------------|
| **Price** | $20 one-time | $20 one-time |
| **Delivery** | Docker + Python source ZIP | Docker + FastAPI source ZIP |
| **Docs** | README + config.example.yaml | README + config.example.yaml + OpenAPI |
| **Support** | None (7-day defect warranty) | None (7-day defect warranty) |
| **Updates** | Version at time of purchase | Version at time of purchase |
| **Chains** | 5 EVM chains | 5 EVM chains |
| **Position** | "Try it, learn from the code" | "Try it, learn from the code" |

**Why $20:** Low-friction entry. Buyer gets working code they can study, modify, deploy. Price is low enough to avoid chargeback motivation. Source code has resale deterrent (they'd need to support it).

### Tier B: Pro — $97

Unlocked when enough buyers validate Tier A. Same code, better packaging.

| Attribute | Crypto Portfolio Agent | AI Agent Wallet |
|-----------|----------------------|-----------------|
| **Price** | $97 one-time | $97 one-time |
| **Delivery** | Everything in A + | Everything in A + |
| **Extras** | Pre-built config templates (5 personas), example alert rules, sample reports | Pre-built config templates, example guardrail configs, Postman collection |
| **Support** | Email support for 30 days | Email support for 30 days |
| **Updates** | 90-day update window | 90-day update window |
| **Position** | "Deploy with confidence" | "Deploy with confidence" |

### Tier C: Business — $297

Premium tier. For buyers who want deployment help.

| Attribute | Crypto Portfolio Agent | AI Agent Wallet |
|-----------|----------------------|-----------------|
| **Price** | $297 one-time | $297 one-time |
| **Delivery** | Everything in B + | Everything in B + |
| **Extras** | 60-min onboarding call, managed deployment to buyer's infra, custom config review | 60-min onboarding call, managed deployment, security review of buyer's config |
| **Support** | 90-day email support | 90-day email support |
| **Updates** | 6-month update window | 6-month update window |
| **Position** | "Done for you" | "Done for you" |

### Packaging Rules

1. **Same codebase across all tiers** — no artificial feature gates
2. **Tiers differ by support, docs, and services** — not by functionality
3. **Never gate security features** — all guardrails ship in every tier
4. **Tier B/C are NOT on Whop yet** — launch A first, validate demand, then add

---

## 3. Pricing Tiers & Updates Subscription

### One-Time Pricing

| Tier | Price | Margin | Position |
|------|-------|--------|----------|
| **A: Starter** | $20 | ~100% (near-zero COGS) | Impulse buy, portfolio filler |
| **B: Pro** | $97 | ~95% (templates cost time to create) | Serious deployer |
| **C: Business** | $297 | ~80% (1hr call + deployment labor) | Done-for-you buyer |

### Optional Updates Subscription

| Plan | Price | What They Get | Billing |
|------|-------|---------------|---------|
| **Updates** | $9/mo | New features, chain additions, bug fixes, dependency updates | Monthly, cancel anytime |
| **Priority Support** | $49/mo | 4 hrs/mo, 48hr response, custom config help, priority bug fixes | Monthly, cancel anytime |

**Subscription positioning:** "Your purchase includes the version at time of sale. Subscribe to Updates for ongoing improvements."

### Why This Pricing Works

- **$20 Starter** eliminates chargeback incentive (not worth the hassle)
- **$97 Pro** feels like a deal vs building it yourself (100+ hours of dev time)
- **$297 Business** anchors against hiring a freelancer ($2K-5K for equivalent)
- **$9/mo Updates** is cheaper than a coffee, recurring revenue, high retention
- **$49/mo Support** filters out tire-kickers, attracts serious users

### Whop Plan Configuration (Current)

Both products are live at $20 (Tier A). To add tiers later:

```python
# Tier B: Pro
client.plans.create(
    company_id="biz_a8sRa66noA89yg",
    product_id="prod_xxx",
    plan_type="one_time",
    title="Pro",
    initial_price=97,
    currency="usd",
    visibility="hidden",  # enable when ready
)

# Updates subscription
client.plans.create(
    company_id="biz_a8sRa66noA89yg",
    product_id="prod_xxx",
    plan_type="renewal",
    title="Updates Subscription",
    initial_price=0,
    renewal_price=9,
    billing_period=30,
    currency="usd",
    visibility="hidden",
)
```

---

## 4. Anti-Chargeback Checklist

### A. Listing Copy — Dispute Prevention Language

Every product listing MUST include these elements:

#### What's Included (Explicit)

```
WHAT YOU GET:
- Docker container image
- Full Python source code
- Configuration template with examples
- README with setup instructions
- 7-day defect warranty

WHAT YOU DO NOT GET:
- Support of any kind (self-service only)
- Custom development
- Deployment to your infrastructure
- Future updates
- Financial advice or trading signals
```

#### Acceptance Criteria (Testable)

```
ACCEPTANCE:
Run the included doctor/health command. If all checks pass,
the product is delivered as described. You have 48 hours to
report reproducible defects.
```

#### Disclaimers (Required)

```
DISCLAIMER: This is a self-hosted software tool. It does not
constitute financial, investment, or legal advice. Cryptocurrency
involves extreme risk including total loss of funds. The seller
is not liable for any financial decisions, losses, or damages.
This is a digital product — no refunds after delivery. By
purchasing, you agree to these terms.
```

### B. Pre-Purchase Friction (Good Friction)

Add these to the Whop product page:

1. **"Requirements" section** — List what buyer must provide (Docker, RPC key, etc.)
2. **"This is NOT for you if..."** — Explicitly disqualify bad-fit buyers
3. **FAQ with objection handling** — Answer "do you guarantee returns" = NO
4. **Delivery timeline** — "Instant digital delivery via download link"

#### "NOT For You If" Copy

```
THIS IS NOT FOR YOU IF:
- You expect automated trading or profit guarantees
- You don't have Docker installed or can't use a terminal
- You want managed hosting included in the price
- You need phone support or hand-holding
- You're looking for a SaaS with a web dashboard
```

### C. Onboarding Flow (Post-Purchase)

Reduce "buyer's remorse" chargebacks by making the first 10 minutes excellent:

1. **Instant delivery email** — Download link + quick-start steps
2. **Doctor command** — Buyer verifies product works in 2 minutes
3. **First value in 5 minutes** — Pre-built config that shows a real balance
4. **Success confirmation** — "Reply to this email when your first report generates"

#### Post-Purchase Message Template

```
Your [Product Name] is ready!

STEP 1: Download and unzip
STEP 2: Copy config.example.yaml → config.yaml
STEP 3: Add your RPC URL and wallet address
STEP 4: Run: docker-compose up
STEP 5: Check output/ for your first report

VERIFY: Run the doctor command to confirm everything works:
  docker-compose run --rm doctor

If all checks pass, you're good to go!

Questions in the first 7 days? Reply to this email for
defect warranty support.

After 7 days, support is available as a paid subscription.
```

### D. Chargeback Defense Kit

If a dispute happens, have these ready:

| Evidence | What It Proves |
|----------|---------------|
| **Delivery confirmation** | Whop download timestamp + IP |
| **Doctor report** | Product worked at time of delivery |
| **Listing screenshots** | Disclaimers were visible pre-purchase |
| **Communication log** | Buyer was informed of terms |
| **No-refund policy** | Clearly stated on listing |
| **Product is digital** | Not returnable — standard for digital goods |

#### Defense Template

```
This is a digital software product delivered instantly via download.
The buyer received the product on [date] at [time] (Whop delivery
confirmation attached). The product listing clearly states:
1. Digital product, no refunds after delivery
2. 7-day defect warranty for reproducible bugs only
3. No financial advice or profit guarantees
4. Self-hosted tool requiring buyer's own infrastructure

The included doctor command verifies product functionality.
The buyer did not report any reproducible defects within the
warranty period.
```

### E. Chargeback Prevention Scorecard

| Control | Status | Priority |
|---------|--------|----------|
| No-refund policy in listing | **TODO** | P0 |
| Disclaimer in listing | **TODO** | P0 |
| "Not for you if" section | **TODO** | P0 |
| Requirements section | **TODO** | P0 |
| Doctor command works | **DONE** | — |
| Post-purchase email template | **TODO** | P1 |
| Acceptance criteria in listing | **TODO** | P1 |
| FAQ with dispute prevention | **TODO** | P1 |
| Download delivery confirmation | **AUTO** (Whop handles) | — |
| Chargeback defense template | **DONE** (this doc) | — |

---

## 5. Immediate Action Items

### Before Selling (P0)

1. **Fix crypto-agent main.py** — Wire alert engine evaluation into monitoring loop
2. **Remove false claims** — Drop whale movement, Compound V3, CoinMarketCap from all listings
3. **Update Whop listings** — Add disclaimers, requirements, "not for you if" sections
4. **Fix or remove large-tx delay** — Either implement in agent-wallet guardrails.py or remove from listing
5. **Fill empty files** — CHANGELOG.md, LICENSE.md in ai-agent-wallet
6. **Honest feature counts** — 5 alert types (not 6), 7 guardrails (not 8)

### After First Sales (P1)

7. **Create post-purchase email template** in Whop
8. **Add Tier B/C plans** (hidden, enable when demand validates)
9. **Add Updates subscription** ($9/mo plan, hidden until ready)
10. **Build pre-configured "starter" configs** for Tier B

### Long Term (P2)

11. **API authentication** for agent-wallet (needed for Pro/Business tiers)
12. **Kill switch persistence** (file or DB-backed)
13. **Implement whale movement** alert (then re-add to listing)
14. **Web dashboard** prototype for Tier C upsell

---

*Audit generated: 2026-02-09*
*Intent Solutions — jeremy@intentsolutions.io*
