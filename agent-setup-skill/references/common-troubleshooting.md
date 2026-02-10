# Common Troubleshooting — All Products

## Node.js Issues

### Wrong version
```
Error: node: --experimental-vm-modules is not supported
```
**Fix**: Upgrade to Node.js 20+
```bash
# Using nvm
nvm install 20
nvm use 20

# Using system package manager
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### pnpm not found
```bash
npm install -g pnpm
# Or with corepack (Node 16+)
corepack enable
corepack prepare pnpm@latest --activate
```

## Python Issues

### Wrong version
Need Python 3.10+.
```bash
# Check version
python3 --version

# Install with pyenv
pyenv install 3.12.0
pyenv local 3.12.0
```

### pip install fails
```bash
# Use venv
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### ModuleNotFoundError
Not in the virtual environment or deps not installed.
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Docker Issues

### Docker not found
```bash
# Check if installed
docker --version

# Install Docker (Ubuntu)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (avoid sudo)
sudo usermod -aG docker $USER
# Log out and back in
```

### Permission denied
```
Got permission denied while trying to connect to the Docker daemon socket
```
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Port already in use
```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```
```bash
# Find what's using the port
lsof -i :8000
# Kill it or change port in config
```

## RPC Connectivity

### Connection refused / timeout
1. Check your internet connection
2. Verify the RPC URL is correct
3. Check if API key is valid
4. Try a public fallback:
   - Ethereum: `https://eth.llamarpc.com`
   - Polygon: `https://polygon.llamarpc.com`
   - Base: `https://mainnet.base.org`
   - Arbitrum: `https://arbitrum.llamarpc.com`
   - Optimism: `https://optimism.llamarpc.com`

### Rate limited (429 errors)
- Free tier Alchemy/Infura has rate limits
- Reduce `requests_per_minute` in config
- Or upgrade to a paid plan

### Invalid API key
- Alchemy: Check dashboard at https://dashboard.alchemy.com
- Infura: Check dashboard at https://infura.io/dashboard
- Make sure the key is for the correct network

## Config Issues

### YAML syntax error
```
yaml.scanner.ScannerError: mapping values are not allowed here
```
- Check indentation (must be spaces, not tabs)
- Ensure colons have a space after them
- Quote strings with special characters

### Schema validation failed
- Check the error message for which field failed
- Compare with `config.example.yaml`
- Ensure wallet addresses match `0x` + 40 hex chars

## Secrets / Environment Variables

### Variable not found
```bash
# Check if set
echo $ALCHEMY_API_KEY

# Set temporarily
export ALCHEMY_API_KEY="your-key-here"

# Set permanently in .env file
echo 'ALCHEMY_API_KEY=your-key-here' >> .env
```

### .env not loading
- Python: Ensure `python-dotenv` is installed
- Node.js: Ensure `.env` is in the project root
- Docker: Check `env_file` or `environment` in docker-compose

## Permission Issues

### Cannot write to output directory
```bash
mkdir -p output
chmod 755 output
```

### Cannot write to data directory (Wallet)
```bash
mkdir -p data
chmod 755 data
```

## Network-Specific Issues

### CoinGecko rate limit
Free CoinGecko API allows ~10 calls/minute. If you're getting failures:
- Wait 60 seconds and retry
- Reduce alert check frequency
- CoinGecko has occasional outages — not a critical failure

### Lit Protocol connectivity (Vincent only)
Yellowstone RPC (`https://yellowstone-rpc.litprotocol.com/`) must be reachable.
- If it fails, Lit Protocol network may be down
- Check https://status.litprotocol.com for status
- This is required for Vincent to function

### Telegram bot not responding
1. Verify bot token with: `curl https://api.telegram.org/bot<TOKEN>/getMe`
2. Get chat ID: Message @userinfobot on Telegram
3. Ensure the bot is added to the chat/group
