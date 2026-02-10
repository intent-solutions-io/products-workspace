# CLAUDE.md — Products Workspace

This is the parent workspace for Intent Solutions digital products. Each product is a separate git repo cloned into this directory.

## Workspace Structure

```
products/
├── crypto-agent/          # Crypto Portfolio Agent ($20) — separate repo
├── ai-agent-wallet/       # AI Agent Wallet ($20) — separate repo
├── vincent-defi-agent/    # Vincent DeFi Agent ($20) — separate repo
├── bags/                  # Bags integration
├── .mcp.json              # Whop MCP server config (shared across products)
├── CLAUDE.md              # This file
├── AGENTS.md              # Available specialist agents
└── README.md              # Public workspace overview
```

## Products

| Product | Repo | Price | Status |
|---------|------|-------|--------|
| Crypto Portfolio Agent | `intent-solutions-io/crypto-agent` | $20 | Shipped |
| AI Agent Wallet | `intent-solutions-io/ai-agent-wallet` | $20 | Shipped |
| Vincent DeFi Agent | `intent-solutions-io/vincent-defi-agent` | $20 | Shipped |

## Sales Channels

- **Gumroad**: https://intentsolutions.gumroad.com (all 3 products live)
- **Whop**: Live via MCP + SDK (API key in `pass whop/api-key`)

## Whop Integration

Whop MCP server is configured in `.mcp.json` at this workspace level so all product projects inherit it. Auth via `WHOP_API_KEY` env var.

Three Whop specialist agents available in `~/.claude/agents/`:
- `whop-product-specialist` — Listing copy, pricing, highlights
- `whop-deployment-specialist` — API calls to create/update products
- `whop-analyst` — Market research, competitor analysis

Python SDK: `whop-sdk` installed in `/home/jeremy/.venvs/whop/`

## Common Commands

```bash
# Crypto Agent
cd crypto-agent && python main.py --config config.yaml --once
cd crypto-agent && python doctor.py --config config.yaml
cd crypto-agent && pytest tests/ -v

# AI Agent Wallet
cd ai-agent-wallet && python main.py
cd ai-agent-wallet && pytest tests/ -v

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
- **Delivery**: Docker container + source ZIP + config template + README
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

# Crypto Agent
ALCHEMY_API_KEY      # RPC provider
INFURA_API_KEY       # Backup RPC
SMTP_PASSWORD        # Email notifications
TELEGRAM_BOT_TOKEN   # Telegram notifications

# AI Agent Wallet
ENCRYPTION_KEY       # Fernet key for wallet encryption
```
