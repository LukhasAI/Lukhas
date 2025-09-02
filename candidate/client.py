from __future__ import annotations

import time
from typing import Any, TypedDict

import requests


class LukhasError(RuntimeError):
    def __init__(self, status: int, message: str, body: str | None = None):
        super().__init__(f"{status} {message}")
        self.status = status
        self.body = body


class FeedbackCard(TypedDict, total=False):
    target_action_id: str
    rating: int
    note: str | None
    user_id: str | None
    tags: list[str] | None


class Lukhas:
    """
    Minimal, production-safe client.
    - Adds x-api-key when provided
    - Retries 429/5xx with exponential backoff
    - 10s default timeout
    """

    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: float = 10.0,
        retries: int = 3,
    ):
        self.base = base_url.rstrip("/")
        self.s = requests.Session()
        self.timeout = timeout
        self.retries = retries
        if api_key:
            self.s.headers.update({"x-api-key": api_key})
        self.s.headers.update({"content-type": "application/json"})

    def _request(
        self, method: str, path: str, *, params=None, json_body=None
    ) -> dict[str, Any]:
        url = f"{self.base}{path}"
        attempt = 0
        last_err = None
        while attempt <= self.retries:
            try:
                resp = self.s.request(
                    method, url, params=params, json=json_body, timeout=self.timeout
                )
                if 200 <= resp.status_code < 300:
                    if "application/json" in resp.headers.get("content-type", ""):
                        return resp.json()
                    return {"ok": True, "text": resp.text}
                if (
                    resp.status_code in (429, 500, 502, 503, 504)
                    and attempt < self.retries
                ):
                    time.sleep(min(2**attempt * 0.2, 1.5))
                    attempt += 1
                    continue
                raise LukhasError(resp.status_code, resp.reason, resp.text)
            except requests.RequestException as e:
                last_err = e
                if attempt >= self.retries:
                    raise LukhasError(0, "network_error", str(e))
                time.sleep(min(2**attempt * 0.2, 1.5))
                attempt += 1
        raise LukhasError(0, "unknown_error", str(last_err))

    # ---- Feedback ----------------------------------------------------------
    def feedback_card(
        self,
        *,
        target_action_id: str,
        rating: int,
        note: str | None = None,
        user_id: str | None = None,
        tags: list[str] | None = None,
    ) -> dict[str, Any]:
        body: FeedbackCard = {
            "target_action_id": target_action_id,
            "rating": int(rating),
        }
        if note:
            body["note"] = note
        if user_id:
            body["user_id"] = user_id
        if tags:
            body["tags"] = tags
        return self._request("POST", "/feedback/card", json_body=body)

    def feedback_lut(self) -> dict[str, Any]:
        return self._request("GET", "/feedback/lut")

    # ---- Tools -------------------------------------------------------------
    def tools_registry(self) -> dict[str, Any]:
        return self._request("GET", "/tools/registry")

    def tools_names(self) -> dict[str, Any]:
        try:
            return self._request("GET", "/tools/available")
        except LukhasError as e:
            if e.status == 404:
                return self._request("GET", "/tools/names")
            raise

    def tool_schema(self, tool_name: str) -> dict[str, Any]:
        return self._request("GET", f"/tools/{tool_name}")

    # ---- DNA ---------------------------------------------------------------
    def dna_health(self) -> dict[str, Any]:
        return self._request("GET", "/dna/health")

    def dna_compare(self, key: str) -> dict[str, Any]:
        return self._request("GET", "/dna/compare", params={"key": key})

    # ---- Admin (read-only) -------------------------------------------------
    def admin_summary(self) -> dict[str, Any]:
        return self._request("GET", "/admin/summary.json")

    # ---- Helpers -----------------------------------------------------------
    def audit_view_url(self, audit_id: str) -> str:
        return f"{self.base}/audit/view/{audit_id}"


__all__ = ["FeedbackCard", "Lukhas", "LukhasError"]
