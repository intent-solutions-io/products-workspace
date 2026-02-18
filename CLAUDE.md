# CLAUDE.md — Products Workspace

This is the parent workspace for Intent Solutions digital products. Each product is a separate git repo cloned into this directory.

## Workspace Structure

```
products/
├── crypto-agent/              # Crypto Portfolio Agent — separate repo
├── ai-agent-wallet/           # AI Agent Wallet — separate repo
├── vincent-defi-agent/        # Vincent DeFi Agent — separate repo
├── derivatives-signal-agent/  # Derivatives Signal Agent — separate repo
├── membership-gateway/        # Whop → GitHub membership automation (Cloud Run)
├── bags/                      # Bags integration
├── .mcp.json                  # Whop MCP server config (shared across products)
├── CLAUDE.md                  # This file
├── AGENTS.md                  # Available specialist agents
└── README.md                  # Public workspace overview
```

## Products

| Product | Repo | Status |
|---------|------|--------|
| Crypto Portfolio Agent | `intent-solutions-io/crypto-agent` | Shipped |
| AI Agent Wallet | `intent-solutions-io/ai-agent-wallet` | Shipped |
| Vincent DeFi Agent | `intent-solutions-io/vincent-defi-agent` | Shipped |
| Derivatives Signal Agent | `intent-solutions-io/derivatives-signal-agent` | Shipped |

## Sales Model: All-Access Membership

Primary sales channel is a Whop membership granting access to all 4 agents via GitHub team.

| Plan | Price | Type |
|------|-------|------|
| Monthly | $29/mo | Renewal |
| Annual | $249/yr | Renewal (~28% discount) |
| Lifetime | $199 | One-time (capped at 50 seats) |

### How It Works

1. Customer purchases membership on Whop, enters GitHub username at checkout
2. `membership-gateway` (Cloud Run) receives webhook, adds user to `members` GitHub team
3. `members` team has pull access to all 4 product repos
4. On cancellation, webhook fires and user is removed from team
5. Daily sync at 3am reconciles any drift between Whop and GitHub

### Sales Channels

- **Whop**: All-Access membership (primary)
- **Gumroad**: Individual products (legacy, parallel sales)

## Whop Integration

Whop MCP server is configured in `.mcp.json` at this workspace level so all product projects inherit it. Auth via `WHOP_API_KEY` env var.

Three Whop specialist agents available in `~/.claude/agents/`:
- `whop-product-specialist` — Listing copy, pricing, highlights
- `whop-deployment-specialist` — API calls to create/update products
- `whop-analyst` — Market research, competitor analysis

Python SDK: `whop-sdk` installed in `/home/jeremy/.venvs/whop/`

## Membership Gateway

Located at `membership-gateway/`. FastAPI service on Cloud Run that automates GitHub team membership.

```bash
# Local development
cd membership-gateway
.venv/bin/python -m uvicorn main:app --reload --port 8080

# Run tests
cd membership-gateway && .venv/bin/python -m pytest tests/ -v

# Deploy to Cloud Run
GCP_PROJECT=your-project ./scripts/deploy.sh

# Create Whop product + plans
WHOP_API_KEY=... /home/jeremy/.venvs/whop/bin/python scripts/create_whop_membership.py

# Register webhook after deploy
WHOP_API_KEY=... python scripts/register_webhook.py https://membership-gateway-xxx.a.run.app
```

### GitHub Team Access

- **Org**: `intent-solutions-io`
- **Team**: `members` (pull access to all 4 product repos)
- **Management**: Automated via Whop webhooks + daily sync

## Common Commands

```bash
# Crypto Agent
cd crypto-agent && python main.py --config config.yaml --once
cd crypto-agent && python doctor.py --config config.yaml
cd crypto-agent && pytest tests/ -v

# AI Agent Wallet
cd ai-agent-wallet && python main.py
cd ai-agent-wallet && pytest tests/ -v

# Derivatives Signal Agent
cd derivatives-signal-agent && python main.py --config config.yaml --once
cd derivatives-signal-agent && python doctor.py --config config.yaml
cd derivatives-signal-agent && pytest tests/ -v

# Membership Gateway
cd membership-gateway && .venv/bin/python -m pytest tests/ -v
cd membership-gateway && .venv/bin/python -m uvicorn main:app --reload --port 8080

# Whop SDK
/home/jeremy/.venvs/whop/bin/python -c "from whop_sdk import Whop; print('OK')"
```

## Version Control

**Semantic versioning is required for all products.**

All products use [Semantic Versioning](https://semver.org/) (MAJOR.MINOR.PATCH):
- **MAJOR**: Breaking changes (config format, API changes, removed features)
- **MINOR**: New features (new abilities, policies, config options)
- **PATCH**: Bug fixes, docs updates, dependency bumps

Each product tracks its version in a `VERSION` file at the repo root. Release scripts read from this file. Bump the version before creating a release.

## Product Patterns

All products follow these conventions:
- **Versioning**: Semantic versioning (see above) tracked in `VERSION` file
- **Delivery**: GitHub repo access via membership + Docker option
- **Acceptance**: `doctor` command produces verifiable test report
- **License**: Non-exclusive, non-transferable, perpetual usage rights
- **Warranty**: 7-day defect warranty for reproducible bugs
- **Support**: Not included by default; paid add-on
- **Secrets**: Environment variables only; never in config or logs
- **Pricing**: Cents in API calls ($297 = 29700)

## Key Environment Variables

```bash
# Whop
WHOP_API_KEY         # Whop marketplace API (in pass whop/api-key)
WHOP_WEBHOOK_SECRET  # Webhook signature verification (Secret Manager)

# Membership Gateway (Cloud Run secrets)
GITHUB_TOKEN         # PAT with admin:org scope for team management
SLACK_WEBHOOK_URL    # Owner notifications

# Crypto Agent
ALCHEMY_API_KEY      # RPC provider
INFURA_API_KEY       # Backup RPC
SMTP_PASSWORD        # Email notifications
TELEGRAM_BOT_TOKEN   # Telegram notifications

# AI Agent Wallet
ENCRYPTION_KEY       # Fernet key for wallet encryption

# Derivatives Signal Agent
BYBIT_API_KEY        # Bybit API key
BYBIT_API_SECRET     # Bybit API secret
COINGLASS_API_KEY    # Coinglass API key ($29/mo)
ANTHROPIC_API_KEY    # Claude API key
```
