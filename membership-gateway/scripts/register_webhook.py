#!/usr/bin/env python3
"""Register the membership-gateway webhook URL in Whop.

Run with: WHOP_API_KEY=... python register_webhook.py <CLOUD_RUN_URL>

Example:
  WHOP_API_KEY=... python register_webhook.py https://membership-gateway-xxx.a.run.app
"""

import os
import sys
import httpx

API_KEY = os.environ.get("WHOP_API_KEY")
if not API_KEY:
    print("Error: WHOP_API_KEY environment variable required")
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python register_webhook.py <CLOUD_RUN_URL>")
    sys.exit(1)

base_url = sys.argv[1].rstrip("/")
webhook_url = f"{base_url}/webhooks/whop"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

print(f"Registering webhook: {webhook_url}")
r = httpx.post(
    "https://api.whop.com/api/v5/webhooks",
    headers=HEADERS,
    json={
        "url": webhook_url,
        "events": [
            "membership.activated",
            "membership.deactivated",
            "payment.failed",
        ],
        "enabled": True,
    },
)
r.raise_for_status()
data = r.json()
print(f"Webhook registered: {data.get('id')}")
print(f"URL: {webhook_url}")
print(f"Events: {data.get('events')}")
print(f"\nIMPORTANT: Save the webhook secret for WHOP_WEBHOOK_SECRET env var")
