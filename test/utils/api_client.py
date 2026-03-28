"""Typed API wrapper for test use."""

from __future__ import annotations

from typing import Optional

import httpx


class APIClient:
    """Lightweight wrapper around httpx for testing the TimeHit API."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.client = httpx.Client(base_url=base_url, timeout=10.0)
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None

    def login(self, email: str, password: str) -> dict:
        resp = self.client.post(
            "/api/auth/login/",
            json={"email": email, "password": password},
        )
        if resp.status_code == 200:
            data = resp.json()
            self.access_token = data["access"]
            self.refresh_token = data["refresh"]
            return data
        return {"status_code": resp.status_code, "body": resp.text}

    def _headers(self, extra: Optional[dict] = None) -> dict:
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        if extra:
            headers.update(extra)
        return headers

    def get(self, path: str, **kwargs) -> httpx.Response:
        return self.client.get(path, headers=self._headers(), **kwargs)

    def post(self, path: str, **kwargs) -> httpx.Response:
        return self.client.post(path, headers=self._headers(), **kwargs)

    def patch(self, path: str, **kwargs) -> httpx.Response:
        return self.client.patch(path, headers=self._headers(), **kwargs)

    def put(self, path: str, **kwargs) -> httpx.Response:
        return self.client.put(path, headers=self._headers(), **kwargs)

    def delete(self, path: str, **kwargs) -> httpx.Response:
        return self.client.delete(path, headers=self._headers(), **kwargs)

    def close(self):
        self.client.close()
