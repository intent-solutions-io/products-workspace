"""Tests for the membership gateway service."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Patch env vars before importing app
import os
os.environ["WHOP_WEBHOOK_SECRET"] = ""  # disable verification in tests
os.environ["GITHUB_TOKEN"] = "test-token"
os.environ["WHOP_API_KEY"] = "test-key"
os.environ["SLACK_WEBHOOK_URL"] = ""
os.environ["GCP_PROJECT"] = "test-project"

from main import app, extract_github_username


client = TestClient(app)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["service"] == "membership-gateway"


# ---------------------------------------------------------------------------
# extract_github_username
# ---------------------------------------------------------------------------
class TestExtractGithubUsername:
    def test_extracts_username(self):
        fields = [{"question": "GitHub Username", "answer": "octocat", "id": "f1"}]
        assert extract_github_username(fields) == "octocat"

    def test_strips_at_sign(self):
        fields = [{"question": "GitHub Username", "answer": "@octocat", "id": "f1"}]
        assert extract_github_username(fields) == "octocat"

    def test_case_insensitive_question(self):
        fields = [{"question": "github username", "answer": "octocat", "id": "f1"}]
        assert extract_github_username(fields) == "octocat"

    def test_returns_none_when_missing(self):
        fields = [{"question": "Your Email", "answer": "a@b.com", "id": "f1"}]
        assert extract_github_username(fields) is None

    def test_returns_none_for_empty_answer(self):
        fields = [{"question": "GitHub Username", "answer": "  ", "id": "f1"}]
        assert extract_github_username(fields) is None

    def test_returns_none_for_empty_list(self):
        assert extract_github_username([]) is None

    def test_partial_match(self):
        fields = [{"question": "What is your GitHub Username?", "answer": "octocat", "id": "f1"}]
        assert extract_github_username(fields) == "octocat"


# ---------------------------------------------------------------------------
# Webhook: membership.activated
# ---------------------------------------------------------------------------
class TestMembershipActivated:
    def _payload(self, github_username="octocat"):
        custom_fields = []
        if github_username is not None:
            custom_fields = [{"question": "GitHub Username", "answer": github_username, "id": "f1"}]
        return {
            "id": "wh_123",
            "type": "membership.activated",
            "api_version": "v1",
            "timestamp": "2026-01-01T00:00:00Z",
            "data": {
                "id": "mem_abc",
                "status": "active",
                "custom_field_responses": custom_fields,
                "user": {"id": "u1", "username": "whopuser", "email": "user@example.com"},
                "company": {"id": "co1", "title": "Intent Solutions"},
                "plan": {"id": "plan_1"},
                "product": {"id": "prod_1", "title": "All-Access"},
                "cancel_at_period_end": False,
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
                "metadata": {},
                "payment_collection_paused": False,
            },
        }

    @patch("main.audit_log", new_callable=AsyncMock)
    @patch("main.notify_slack", new_callable=AsyncMock)
    @patch("main.add_to_team", new_callable=AsyncMock)
    def test_adds_user_to_team(self, mock_add, mock_slack, mock_audit):
        mock_add.return_value = {"state": "pending"}
        r = client.post("/webhooks/whop", json=self._payload())
        assert r.status_code == 200
        data = r.json()
        assert data["action"] == "added"
        assert data["github_username"] == "octocat"
        mock_add.assert_called_once_with("octocat")

    @patch("main.audit_log", new_callable=AsyncMock)
    @patch("main.notify_slack", new_callable=AsyncMock)
    def test_no_github_username_warns(self, mock_slack, mock_audit):
        r = client.post("/webhooks/whop", json=self._payload(github_username=None))
        assert r.status_code == 200
        data = r.json()
        assert data["warning"] == "no_github_username"


# ---------------------------------------------------------------------------
# Webhook: membership.deactivated
# ---------------------------------------------------------------------------
class TestMembershipDeactivated:
    def _payload(self, github_username="octocat"):
        custom_fields = []
        if github_username is not None:
            custom_fields = [{"question": "GitHub Username", "answer": github_username, "id": "f1"}]
        return {
            "id": "wh_456",
            "type": "membership.deactivated",
            "api_version": "v1",
            "timestamp": "2026-01-15T00:00:00Z",
            "data": {
                "id": "mem_abc",
                "status": "inactive",
                "custom_field_responses": custom_fields,
                "user": {"id": "u1", "username": "whopuser", "email": "user@example.com"},
                "company": {"id": "co1", "title": "Intent Solutions"},
                "plan": {"id": "plan_1"},
                "product": {"id": "prod_1", "title": "All-Access"},
                "cancel_at_period_end": False,
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-15T00:00:00Z",
                "metadata": {},
                "payment_collection_paused": False,
            },
        }

    @patch("main.audit_log", new_callable=AsyncMock)
    @patch("main.notify_slack", new_callable=AsyncMock)
    @patch("main.remove_from_team", new_callable=AsyncMock)
    def test_removes_user_from_team(self, mock_remove, mock_slack, mock_audit):
        mock_remove.return_value = True
        r = client.post("/webhooks/whop", json=self._payload())
        assert r.status_code == 200
        data = r.json()
        assert data["action"] == "removed"
        assert data["github_username"] == "octocat"
        mock_remove.assert_called_once_with("octocat")


# ---------------------------------------------------------------------------
# Webhook: payment.failed
# ---------------------------------------------------------------------------
class TestPaymentFailed:
    @patch("main.audit_log", new_callable=AsyncMock)
    @patch("main.notify_slack", new_callable=AsyncMock)
    def test_logs_payment_failure(self, mock_slack, mock_audit):
        payload = {
            "id": "wh_789",
            "type": "payment.failed",
            "api_version": "v1",
            "timestamp": "2026-01-10T00:00:00Z",
            "data": {
                "id": "mem_abc",
                "custom_field_responses": [],
                "user": {"id": "u1", "username": "whopuser", "email": "user@example.com"},
            },
        }
        r = client.post("/webhooks/whop", json=payload)
        assert r.status_code == 200
        assert r.json()["action"] == "payment_failed_logged"


# ---------------------------------------------------------------------------
# Webhook: unknown event type
# ---------------------------------------------------------------------------
class TestUnknownEvent:
    def test_ignores_unknown_event(self):
        payload = {
            "id": "wh_000",
            "type": "invoice.created",
            "api_version": "v1",
            "timestamp": "2026-01-01T00:00:00Z",
            "data": {"id": "inv_123"},
        }
        r = client.post("/webhooks/whop", json=payload)
        assert r.status_code == 200
        assert r.json()["action"] == "ignored"
