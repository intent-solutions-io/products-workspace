# Vincent DeFi Agent — Setup Reference

## Product Identity

- **Name**: Vincent DeFi Agent
- **Runtime**: Node.js 20+ with pnpm 9+
- **Config**: `config.yaml` (from `config.example.yaml`) + `.env`
- **Doctor**: `pnpm doctor` (after `pnpm build`)
- **Run**: `pnpm agent:start -- --config config.yaml --once`
- **Docker**: `docker-compose up -d`
- **Build System**: Nx monorepo with pnpm workspaces

## Detection Markers

- `package.json` with `"name": "vincent-defi-agent"`
- `pnpm-workspace.yaml` exists
- `packages/` directory with abilities and policies
- `nx.json` exists

## Architecture Overview

Vincent uses **Lit Protocol** for cryptographic guardrails. Instead of software-only checks, policies run inside TEE (Trusted Execution Environment) nodes. This means:

- **Policies are enforced by hardware**, not just code
- **PKP wallets** (Programmable Key Pairs) hold funds — private keys never leave the TEE
- You need a **Lit Protocol account** and a **PKP wallet**

### Components

- **4 Abilities**: native-send, erc20-transfer, swap (Uniswap V3), dca
- **4 Policies**: counter (rate limit), spending-limit, whitelist, stop-loss
- **Agent CLI**: Command-line interface for running the agent

## Environment Variables

| Variable | Required | Description | How to Get |
|----------|----------|-------------|------------|
| `APP_DELEGATEE_PRIVATE_KEY` | **Yes** | EOA key delegated to use the PKP | Generate any Ethereum private key |
| `APP_MANAGER_PRIVATE_KEY` | **Yes** | EOA key that manages the PKP | Generate any Ethereum private key |
| `BASE_RPC_URL` | No | Base chain RPC (default: https://mainnet.base.org) | Alchemy/Infura for reliability |
| `PINATA_JWT` | No | Pinata IPFS for policy deployment | https://app.pinata.cloud — free tier |
| `WEBHOOK_URL` | No | Webhook for notifications | Any webhook endpoint |
| `TELEGRAM_BOT_TOKEN` | No | Telegram notifications | @BotFather on Telegram |

### Key Generation

For `APP_DELEGATEE_PRIVATE_KEY` and `APP_MANAGER_PRIVATE_KEY`:

```bash
# Using Node.js
node -e "const { randomBytes } = require('crypto'); console.log('0x' + randomBytes(32).toString('hex'))"
```

Or using any Ethereum wallet creation tool. These are standard Ethereum private keys.

**CRITICAL**: These keys control access to the PKP wallet. Back them up securely. If lost, funds may be inaccessible.

**Ask buyer**: "Do you already have delegatee and manager private keys, or should I generate them?"

### PKP Wallet Creation

The buyer needs a Lit Protocol PKP wallet. This is created through the Lit Protocol dashboard:

1. Go to https://developer.litprotocol.com
2. Create an account
3. Mint a PKP (Programmable Key Pair)
4. Note the PKP Ethereum address
5. Fund it with ETH on Base chain for gas

**Ask buyer**: "Do you already have a PKP wallet address, or do you need help creating one?"

### Pinata Setup (Optional)

Pinata is used for IPFS storage of policy bundles:

1. Go to https://app.pinata.cloud
2. Create free account
3. Go to API Keys section
4. Create new key with "pinFileToIPFS" permission
5. Copy the JWT token

## Config Sections

### Agent

```yaml
agent:
  name: "My DeFi Agent"
  rpcUrl: "https://mainnet.base.org"
  chainId: 8453
```

**Ask buyer**: "Do you have a custom RPC URL? The default public one works but may be rate-limited."

### Wallet

```yaml
wallet:
  pkpEthAddress: "0x..."  # Your PKP wallet address
```

**Ask buyer**: "Paste your PKP wallet Ethereum address." Validate: `^0x[a-fA-F0-9]{40}$`

### DCA (Dollar-Cost Averaging)

```yaml
dca:
  enabled: false
  tokenIn: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"   # USDC on Base
  tokenOut: "0x4200000000000000000000000000000000000006"     # WETH on Base
  amountPerInterval: "10.0"
  intervalSeconds: 3600
  totalBudget: "1000.0"
```

**Ask buyer**: "Do you want to enable DCA (dollar-cost averaging)?" If yes:
1. "Which token to spend?" (default: USDC)
2. "Which token to buy?" (default: WETH)
3. "How much per interval?" (default: 10 USDC)
4. "Interval in seconds?" (default: 3600 = 1 hour)
5. "Total budget?" (default: 1000 USDC)

### Policies

#### Counter (Rate Limiter)
```yaml
policies:
  counter:
    enabled: true
    maxSends: 10
    timeWindowSeconds: 3600
```

**Ask buyer**: "Max transactions per hour?" (default: 10)

#### Spending Limit
```yaml
  spendingLimit:
    enabled: true
    maxDailyUsd: 100
    maxWeeklyUsd: 500
    tokenCoinGeckoId: "ethereum"
```

**Ask buyer**: "Daily USD spending limit?" and "Weekly limit?"

#### Whitelist
```yaml
  whitelist:
    enabled: false
    allowedAddresses: []
```

**Ask buyer**: "Want to restrict to specific recipient addresses?"

#### Stop-Loss
```yaml
  stopLoss:
    enabled: false
    tokenCoinGeckoId: "ethereum"
    stopLossUsd: 2000.0
```

**Ask buyer**: "Want a stop-loss? At what ETH price should trades be blocked?"

## Doctor Output Interpretation

The doctor checks 4 categories:

### System Checks
- **Node.js version**: Must be >= 20. `[OK]` or `[FAIL]`
- **Environment variables**: Required keys present. `[OK]`, `[WARN]`, or `[SKIP]`

### Config Checks
- **Config file exists**: `config.yaml` found. `[OK]` or `[FAIL]`
- **Schema validation**: YAML validates against Zod schema. `[OK]` or `[FAIL]`

### Network Checks
- **RPC connectivity**: Base chain RPC responds to `eth_chainId`. `[OK]` or `[FAIL]`
- **Lit Network**: Yellowstone RPC reachable. `[OK]` or `[FAIL]`
- **CoinGecko API**: Price oracle accessible (returns ETH price). `[OK]` or `[FAIL]`
- **Pinata IPFS**: Auth works if JWT set. `[OK]`, `[FAIL]`, or `[SKIP]`

### Results Summary
```
Results: X passed, Y failed, Z warnings, W skipped
```
- Exit code 0: All passed or just warnings
- Exit code 1: At least one FAIL

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `Cannot find module` | Build not run | `pnpm install && pnpm build` |
| `ENOENT: config.yaml` | No config file | Copy `config.example.yaml` to `config.yaml` |
| `RPC connectivity FAIL` | Bad RPC URL | Check `agent.rpcUrl` in config |
| `Lit Network FAIL` | Network issue | Check internet, Lit may be down |
| `CoinGecko FAIL` | Rate limited | Wait a minute, try again |
| `APP_DELEGATEE_PRIVATE_KEY WARN` | Not set in env | Add to `.env` file |
| `pnpm build` type errors | TypeScript issues | Run `pnpm install`, check Node version |
| `ERR_MODULE_NOT_FOUND` | Node < 20 | Upgrade Node.js to 20+ |

## Build & Test

```bash
# Full build (required before doctor or run)
pnpm install
pnpm build

# Run tests (40 schema tests)
pnpm test

# Doctor check
pnpm doctor

# Start agent (single run)
pnpm agent:start -- --config config.yaml --once
```

## Base Chain Token Addresses

Common tokens on Base (chain ID 8453):

| Token | Address |
|-------|---------|
| USDC | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| WETH | `0x4200000000000000000000000000000000000006` |
| DAI | `0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb` |
| USDbC | `0xd9aAEc86B65D86f6A7B5B1b0c42FFA531710b6CA` |
