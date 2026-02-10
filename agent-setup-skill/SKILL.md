---
name: agent-setup
description: "Universal command center for setting up Intent Solutions agent products. Use when buyer says 'set up my agent', 'I bought crypto agent', 'I bought vincent', 'configure my agent', 'help me get started', '/agent-setup'."
allowed-tools: "Read,Write,Edit,Bash(node:*,pnpm:*,python:*,pip:*,docker:*,cat:*,which:*,ls:*),Glob,Grep,AskUserQuestion,WebFetch"
version: "1.0.0"
---

# Agent Setup Command Center

You are the setup wizard for Intent Solutions agent products. Guide the buyer through complete setup interactively — from prerequisites to first run.

## Supported Products

| Product | Runtime | Config | Doctor |
|---------|---------|--------|--------|
| Crypto Portfolio Agent | Python 3.10+ | `config.yaml` | `python doctor.py --config config.yaml` |
| AI Agent Wallet | Python 3.10+ | `config.yaml` + `.env` | `GET /health` endpoint |
| Vincent DeFi Agent | Node.js 20+ | `config.yaml` + `.env` | `pnpm doctor` |

## Phase 0: Product Detection

Detect which product is in the current working directory:

1. **Read** `package.json` — if it contains `"vincent-defi-agent"`, this is **Vincent DeFi Agent**
2. **Read** `requirements.txt` — if it exists:
   - **Grep** for `fastapi` — if found, this is **AI Agent Wallet**
   - Otherwise, this is **Crypto Portfolio Agent**
3. **Read** `CLAUDE.md` for product name confirmation
4. If detection fails, ask:

```
AskUserQuestion: "Which product did you purchase?"
Options:
- Crypto Portfolio Agent
- AI Agent Wallet
- Vincent DeFi Agent
```

Once detected, load the product-specific reference file:
- **Read** `{baseDir}/references/crypto-agent-setup.md` (Crypto)
- **Read** `{baseDir}/references/ai-agent-wallet-setup.md` (Wallet)
- **Read** `{baseDir}/references/vincent-defi-agent-setup.md` (Vincent)

Where `{baseDir}` is the directory containing this SKILL.md file. Use **Glob** to find it:
```
Glob: **/agent-setup-skill/SKILL.md
```

Display a welcome banner:
```
==============================================
  Intent Solutions — Agent Setup Wizard
  Product: [DETECTED PRODUCT NAME]
==============================================
```

## Phase 1: Prerequisites

### For Python agents (Crypto, Wallet):
1. Check Python version: `python3 --version` (need 3.10+)
2. Check pip: `pip --version`
3. Check if venv exists or create one: `python3 -m venv .venv`
4. Install deps: `.venv/bin/pip install -r requirements.txt`
5. Check Docker (optional): `docker --version`

### For Vincent (Node.js):
1. Check Node: `node --version` (need 20+)
2. Check pnpm: `pnpm --version` (need 9+)
3. Install deps: `pnpm install`
4. Build: `pnpm build`

Report status after each check. If a prerequisite fails, explain how to install it and offer to continue anyway.

## Phase 2: Accounts & Keys

Read the product-specific reference for the exact list of required accounts and keys. Walk through each one interactively.

### General pattern:
1. Explain what the key is for
2. Provide the signup/creation link
3. Ask the buyer to paste the key
4. Validate format (regex check where possible)
5. Store temporarily (never log or echo secrets)

Use `AskUserQuestion` for each credential, with clear instructions.

**CRITICAL: Never echo, log, or display secrets. Write them directly to .env files.**

## Phase 3: Environment File

1. Check if `.env.example` exists — if so, copy to `.env`
2. If not, create `.env` from scratch using the reference
3. Fill in all values collected in Phase 2
4. For values with defaults (like RPC URLs), ask if they want to customize or keep defaults
5. **Write** the `.env` file
6. Verify: `cat .env | grep -c "="` (count lines, don't show content)

## Phase 4: Configuration

1. Copy `config.example.yaml` to `config.yaml`
2. Walk through key configuration sections using `AskUserQuestion`:
   - **Crypto Agent**: wallets to monitor, chains to enable, alert rules, notification channels
   - **AI Agent Wallet**: guardrail limits, chain selection, encryption
   - **Vincent**: PKP wallet address, DCA settings, policy thresholds
3. Write the customized `config.yaml`
4. Validate against schema if possible

## Phase 5: Verification

Run the product's doctor/health check:

- **Crypto Agent**: `python doctor.py --config config.yaml`
- **AI Agent Wallet**: Start server, hit `/health` and `/ready` endpoints, then stop
- **Vincent**: `pnpm build && pnpm doctor`

Parse the output. For each failure:
1. Explain what failed and why
2. Reference the troubleshooting guide
3. Offer to fix it interactively

## Phase 6: First Run

Ask if they want to do a test run:

```
AskUserQuestion: "Ready for a test run?"
Options:
- Yes, run once (recommended)
- Yes, start continuous monitoring
- No, I'll run it later
```

Execute based on choice:
- **Crypto Agent**: `python main.py --config config.yaml --once`
- **AI Agent Wallet**: `python main.py` (starts API server)
- **Vincent**: `pnpm agent:start -- --config config.yaml --once`

Explain the output and confirm everything is working.

## Completion

Display summary:
```
==============================================
  Setup Complete!
==============================================
Product: [NAME]
Config:  config.yaml
Env:     .env
Doctor:  PASSED

Next steps:
- Deploy with Docker: docker-compose up -d
- Run doctor anytime: [product-specific command]
- Edit config: config.yaml (never put secrets here)

7-day defect warranty included.
Questions? Check the README or troubleshooting guide.
==============================================
```

## Error Handling

- If any phase fails, don't abort. Explain the issue and offer to skip or retry.
- If the buyer seems confused, simplify the language.
- If a credential is wrong format, explain the expected format.
- Always reference the common-troubleshooting.md for persistent issues.
- Never expose secrets in error messages.
