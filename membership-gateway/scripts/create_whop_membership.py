#!/usr/bin/env python3
"""Create the Intent Solutions All-Access membership product on Whop.

Run with: WHOP_API_KEY=... /home/jeremy/.venvs/whop/bin/python create_whop_membership.py

This script creates:
1. The "Intent Solutions All-Access" product/company
2. Three plans: Monthly ($29), Annual ($249), Lifetime ($199)
3. Requires WHOP_API_KEY environment variable
"""

import os
import sys
import httpx

API_KEY = os.environ.get("WHOP_API_KEY")
if not API_KEY:
    print("Error: WHOP_API_KEY environment variable required")
    sys.exit(1)

BASE_URL = "https://api.whop.com/api/v5"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}


def api(method: str, path: str, **kwargs) -> dict:
    r = httpx.request(method, f"{BASE_URL}{path}", headers=HEADERS, **kwargs)
    r.raise_for_status()
    return r.json()


def main():
    # 1. Create the product
    print("Creating product...")
    product = api("POST", "/products", json={
        "name": "Intent Solutions All-Access",
        "description": (
            "Full access to all Intent Solutions AI crypto agents. "
            "Includes Crypto Portfolio Agent, AI Agent Wallet, Vincent DeFi Agent, "
            "and Derivatives Signal Agent. All updates and new agents included."
        ),
        "visibility": "visible",
    })
    product_id = product.get("id")
    print(f"  Product created: {product_id}")

    # 2. Create Monthly plan ($29/mo)
    print("Creating Monthly plan ($29/mo)...")
    monthly = api("POST", f"/products/{product_id}/plans", json={
        "plan_type": "renewal",
        "billing_period": "monthly",
        "initial_price": 2900,  # cents
        "renewal_price": 2900,
        "currency": "usd",
    })
    print(f"  Monthly plan: {monthly.get('id')}")

    # 3. Create Annual plan ($249/yr)
    print("Creating Annual plan ($249/yr)...")
    annual = api("POST", f"/products/{product_id}/plans", json={
        "plan_type": "renewal",
        "billing_period": "yearly",
        "initial_price": 24900,
        "renewal_price": 24900,
        "currency": "usd",
    })
    print(f"  Annual plan: {annual.get('id')}")

    # 4. Create Lifetime plan ($199)
    print("Creating Lifetime plan ($199)...")
    lifetime = api("POST", f"/products/{product_id}/plans", json={
        "plan_type": "one_time",
        "initial_price": 19900,
        "currency": "usd",
    })
    print(f"  Lifetime plan: {lifetime.get('id')}")

    print("\n--- Summary ---")
    print(f"Product ID: {product_id}")
    print(f"Monthly:    {monthly.get('id')} ($29/mo)")
    print(f"Annual:     {annual.get('id')} ($249/yr)")
    print(f"Lifetime:   {lifetime.get('id')} ($199 one-time)")
    print("\nNOTE: You still need to:")
    print("  1. Add 'GitHub Username' custom checkout field in Whop dashboard")
    print("  2. Set up the welcome message in Whop dashboard")
    print("  3. Register the webhook URL after deploying membership-gateway")


if __name__ == "__main__":
    main()
