# AI Agent Wallet — Setup Reference

## Product Identity

- **Name**: AI Agent Wallet
- **Runtime**: Python 3.10+
- **Config**: `config.yaml` (from `config.example.yaml`) + `.env` (from `.env.example`)
- **Health Check**: `GET /health` and `GET /ready` endpoints
- **Run**: `python main.py` (starts FastAPI on port 8000)
- **Docker**: `docker-compose up -d`

## Detection Markers

- `requirements.txt` with `fastapi` in it
- `main.py` with FastAPI app
- `config/schema.py` has `Settings` with `env_prefix = "WALLET_"`
- No `doctor.py` — uses HTTP health endpoints instead

## Environment Variables

All env vars use the `WALLET_` prefix (Pydantic BaseSettings).

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `WALLET_ENCRYPTION_KEY` | **Yes (prod)** | None | Fernet key for encrypting private keys at rest |
| `WALLET_HOST` | No | `0.0.0.0` | Server bind address |
| `WALLET_PORT` | No | `8000` | Server port |
| `WALLET_DEBUG` | No | `false` | Debug mode |
| `WALLET_DATABASE_URL` | No | `sqlite+aiosqlite:///./agent_wallet.db` | Database connection |
| `WALLET_DEFAULT_CHAIN_ID` | No | `1` | Default chain ID |
| `WALLET_CONFIG_PATH` | No | `config.yaml` | Config file path |

### Generating the Encryption Key

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**CRITICAL**: This key encrypts wallet private keys at rest. If lost, wallets cannot be decrypted. Back it up securely.

**Ask buyer**: "Do you want me to generate an encryption key for you?" If yes, run the command and write directly to `.env`.

## Config Sections

### Server

```yaml
host: "0.0.0.0"
port: 8000
debug: false
database_url: "sqlite+aiosqlite:///./data/agent_wallet.db"
```

Defaults are fine for most users. Only change `database_url` for production PostgreSQL.

### Guardrails (8 controls)

```yaml
guardrails:
  enabled: true              # Master kill switch
  max_per_tx: "1.0"          # Max ETH per transaction
  max_daily: "10.0"          # Max ETH per day
  max_monthly: "100.0"       # Max ETH per month
  cooldown_seconds: 0        # Seconds between transactions
  large_tx_delay_seconds: 0  # Delay for large transactions
  large_tx_threshold: "5.0"  # What counts as "large" (ETH)
  address_whitelist: []      # Only send to these addresses
  contract_whitelist: []     # Only interact with these contracts
```

**Ask buyer** (one at a time):
1. "What's the maximum ETH per transaction?" (default: 1.0)
2. "What's the maximum daily spend?" (default: 10.0)
3. "Do you want to restrict to specific recipient addresses?" (address whitelist)
4. "Do you want a cooldown between transactions?" (seconds)

### Chains (5 pre-configured)

| Chain | ID | Default RPC |
|-------|----|------------|
| Ethereum | 1 | https://eth.llamarpc.com |
| Polygon | 137 | https://polygon.llamarpc.com |
| Arbitrum | 42161 | https://arbitrum.llamarpc.com |
| Base | 8453 | https://base.llamarpc.com |
| Optimism | 10 | https://optimism.llamarpc.com |

**Ask buyer**: "Which chains do you need?" (multi-select). Then: "Do you have your own RPC endpoint (Alchemy/Infura)? The defaults use public RPCs which may be rate-limited."

## Health Check Interpretation

### `GET /health`
Returns: `{"status": "healthy", "version": "1.0.0", "service": "ai-agent-wallet"}`
- If status != "healthy", the server has a startup issue

### `GET /ready`
Returns readiness details:
- `chains_configured`: Number of chains set up
- `kill_switch_active`: Whether guardrails master switch is on
- `transactions_enabled`: Whether the system can send transactions

## Verification Procedure (No Doctor Script)

Since there's no `doctor.py`, verify manually:

1. Start server: `python main.py`
2. Test health: `curl http://localhost:8000/health`
3. Test readiness: `curl http://localhost:8000/ready`
4. Create test wallet: `curl -X POST http://localhost:8000/wallets -H "Content-Type: application/json" -d '{"name": "test", "chain_id": 1}'`
5. Check guardrails: `curl http://localhost:8000/guardrails`
6. Stop server: Ctrl+C

## Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `WALLET_ENCRYPTION_KEY not set` | Missing env var | Generate key and add to `.env` |
| `ModuleNotFoundError: fastapi` | Deps not installed | `pip install -r requirements.txt` |
| `Address already in use` | Port 8000 taken | Change `WALLET_PORT` or stop other process |
| `database is locked` | SQLite concurrency | Use PostgreSQL for production |
| `Invalid Fernet key` | Malformed key | Regenerate with the Python command |
| `Permission denied: ./data/` | Missing directory | `mkdir -p data` |

## API Endpoints Reference

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/ready` | Readiness check |
| POST | `/wallets` | Create wallet |
| GET | `/wallets` | List wallets |
| GET | `/wallets/{id}` | Get wallet details |
| POST | `/wallets/{id}/send` | Send transaction |
| GET | `/transactions` | List transactions |
| GET | `/guardrails` | Get guardrail config |
| PUT | `/guardrails` | Update guardrails |
| GET | `/audit` | Audit trail |

## Dependencies

```
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
web3>=6.14.0
eth-account>=0.10.0
sqlalchemy>=2.0.25
aiosqlite>=0.19.0
cryptography>=42.0.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-dotenv>=1.0.0
httpx>=0.26.0
pyyaml>=6.0.1
```
