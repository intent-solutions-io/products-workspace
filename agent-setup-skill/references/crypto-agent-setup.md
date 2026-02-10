# Crypto Portfolio Agent — Setup Reference

## Product Identity

- **Name**: Crypto Portfolio Agent
- **Runtime**: Python 3.10+
- **Config**: `config.yaml` (from `config.example.yaml`)
- **Doctor**: `python doctor.py --config config.yaml`
- **Run**: `python main.py --config config.yaml --once`
- **Continuous**: `python main.py --config config.yaml --interval 300`
- **Docker**: `docker-compose up -d`

## Detection Markers

- `requirements.txt` exists (no `fastapi` in it)
- `doctor.py` in root
- `config/schema.py` has `ConfigSchema`
- `tools/` directory with `balance_tracker.py`, `price_fetcher.py`

## Environment Variables

| Variable | Required | Description | How to Get |
|----------|----------|-------------|------------|
| `ALCHEMY_API_KEY` | Yes | Primary RPC provider | Sign up at https://www.alchemy.com — free tier works |
| `INFURA_API_KEY` | No | Fallback RPC provider | Sign up at https://infura.io — free tier works |
| `SMTP_PASSWORD` | If email | SMTP auth for email alerts | Your email provider's app password |
| `TELEGRAM_BOT_TOKEN` | If telegram | Telegram Bot API token | Message @BotFather on Telegram |
| `ETHEREUM_SCAN_API_KEY` | No | Etherscan for tx history | Sign up at https://etherscan.io/apis |
| `POLYGON_SCAN_API_KEY` | No | PolygonScan API | https://polygonscan.com/apis |
| `ARBITRUM_SCAN_API_KEY` | No | Arbiscan API | https://arbiscan.io/apis |

## Config Sections

### Chains (5 supported)

```yaml
chains:
  - chain_id: ethereum
    rpc_url: "https://eth-mainnet.g.alchemy.com/v2/YOUR_KEY"
    fallback_rpc_url: "https://eth.llamarpc.com"
    block_confirmations: 12
    enabled: true
```

Available: `ethereum`, `polygon`, `arbitrum`, `optimism`, `base`

**Ask buyer**: "Which chains do you want to monitor?" (multi-select)

### Wallets

```yaml
wallets:
  - address: "0x..."
    label: "My Main Wallet"
    chains: [ethereum, polygon]
    track_tokens: true
    track_defi: true
    track_transactions: true
```

**Ask buyer**: Paste wallet address(es). Validate format: `^0x[a-fA-F0-9]{40}$`

### Alerts (5 types)

| Type | Description | Key Field |
|------|-------------|-----------|
| `price_threshold` | Price above/below target | `threshold`, `direction` |
| `balance_change` | Balance changed by X% | `percentage` |
| `liquidation_risk` | DeFi health factor low | `threshold` |
| `gas_threshold` | Gas price above X gwei | `threshold` |
| `transaction_detected` | New tx on address | N/A |

Each alert needs: `id`, `type`, `enabled`, `channels`, `cooldown_minutes`

**Ask buyer**: "Which alerts do you want to enable?" (multi-select)

### Notifications

```yaml
notifications:
  webhook_url: "https://..."       # Any webhook endpoint
  smtp_host: "smtp.gmail.com"      # For email
  smtp_port: 587
  smtp_user: "you@gmail.com"
  email_from: "you@gmail.com"
  email_to: ["you@gmail.com"]
  telegram_chat_id: "123456789"    # From @userinfobot
```

**Ask buyer**: "How do you want to receive alerts?" (multi-select: Webhook, Email, Telegram, Slack)

### Guardrails (hardcoded)

These cannot be changed — they're safety rails:
- `read_only: true` — cannot execute transactions
- `max_alerts_per_day: 100`
- `alert_dedup_minutes: 15`

### Cache & Rate Limits

Defaults are fine for most users. Only ask if they have a paid RPC plan:
- `requests_per_minute: 100` (increase for paid plans)
- `balance_ttl_seconds: 30`
- `price_ttl_seconds: 60`

## Doctor Output Interpretation

The doctor runs 5 checks:

1. **config_validation** — Parses config.yaml against Pydantic schema
   - FAIL: Invalid YAML syntax or missing required fields
   - Fix: Check YAML formatting, ensure all required fields present

2. **rpc_connection** — Tests each enabled chain's RPC
   - FAIL: RPC unreachable or wrong API key
   - Fix: Verify ALCHEMY_API_KEY is correct, check URL format

3. **wallet_balance** — Fetches balance of first wallet
   - FAIL: RPC issues or invalid wallet address
   - Fix: Verify wallet address is valid, RPC is working

4. **alert_trigger** — Dry-run of alert engine
   - FAIL: Alert rule configuration issue
   - Fix: Check alert rule format in config.yaml

5. **report_generation** — Creates test report
   - FAIL: Output directory permission issue
   - Fix: Ensure `output/` directory exists and is writable

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError` | Dependencies not installed | `pip install -r requirements.txt` |
| `ALCHEMY_API_KEY not set` | Env var missing | Add to `.env` or export in shell |
| `Config file not found` | Wrong path | Check `--config` path is correct |
| `RPC connection failed` | Bad API key or rate limited | Verify key, try fallback RPC |
| `Permission denied: output/` | Missing directory | `mkdir -p output` |

## Dependencies

```
httpx>=0.27.0
pydantic>=2.9.0
pyyaml>=6.0.2
python-dateutil>=2.9.0
pytz>=2024.1
rich>=13.9.0
typing-extensions>=4.12.0
```
