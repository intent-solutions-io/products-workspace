# AGENTS.md — Products Workspace

Specialist agents available for product development and marketplace operations.

## Whop Marketplace Agents

| Agent | Purpose | Location |
|-------|---------|----------|
| `whop-product-specialist` | Craft listings, marketing copy, pricing strategies, feature highlights | `~/.claude/agents/whop-product-specialist.md` |
| `whop-deployment-specialist` | Execute Whop API calls to create/update products and plans | `~/.claude/agents/whop-deployment-specialist.md` |
| `whop-analyst` | Research marketplace trends, competitor pricing, category analysis | `~/.claude/agents/whop-analyst.md` |

### Usage

**Create a new listing:**
1. Use `whop-analyst` to research competitor pricing and positioning
2. Use `whop-product-specialist` to draft listing copy and highlights
3. Use `whop-deployment-specialist` to push to Whop API (creates as draft first)

**Optimize an existing listing:**
1. Use `whop-analyst` for market intelligence
2. Use `whop-product-specialist` to revise copy
3. Use `whop-deployment-specialist` to update via API

## General Agents (Useful for Products)

| Agent | When to Use |
|-------|-------------|
| `blockchain-developer` | Crypto/Web3 features, smart contract interactions |
| `backend-architect` | API design, service architecture |
| `security-auditor` | Security review of wallet/crypto code |
| `content-marketer` | Blog posts, social media for product launches |
| `sales-automator` | Cold emails, proposals, follow-ups |
| `payment-integration` | Stripe/payment processor setup |
| `deployment-engineer` | Docker, CI/CD, cloud deployment |
| `test-automator` | Test suites, coverage improvement |

## MCP Integration

The Whop MCP server is configured at `products/.mcp.json` and provides direct Whop API access from any product workspace via Claude.
