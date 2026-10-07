"""Cliente HTTP com retry, backoff e cache TTL curto.

Todas as fontes usadas por este servidor são públicas e não exigem credencial.
O cliente existe para absorver a instabilidade real dessas APIs: limites de
requisição, timeouts esporádicos e 5xx transitórios.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any
from urllib.parse import urlencode

import httpx

# O servidor fala JSON-RPC em stdout; log de requisição do httpx vai para stderr
# e polui o transporte. Mantenha em WARNING.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

USER_AGENT = "licitacoes-mcp/0.1.0 (+https://github.com/cYoren/licitacoes-mcp)"
MIN_PAGE_SIZE = 10
RETRY_STATUS = {429, 500, 502, 503, 504}


class ApiError(RuntimeError):
    """Falha definitiva ao consultar uma fonte pública."""


class ApiClient:
    def __init__(self, timeout: float = 45.0, retries: int = 3, cache_ttl: float = 120.0) -> None:
        self._client = httpx.Client(
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        )
        self._retries = retries
        self._cache_ttl = cache_ttl
        self._cache: dict[str, tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def close(self) -> None:
        self._client.close()

    def _cache_get(self, key: str) -> Any:
        with self._lock:
            hit = self._cache.get(key)
        if hit and (time.monotonic() - hit[0]) < self._cache_ttl:
            return hit[1]
        return None

    def _cache_put(self, key: str, value: Any) -> None:
        with self._lock:
            self._cache[key] = (time.monotonic(), value)

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        """GET que devolve JSON, ou ``None`` para 204 sem corpo."""
        params = {k: v for k, v in (params or {}).items() if v is not None}
        key = f"{url}?{urlencode(sorted(params.items()))}"
        cached = self._cache_get(key)
        if cached is not None:
            return cached

        last_error = "falha desconhecida"
        for attempt in range(self._retries + 1):
            try:
                response = self._client.get(url, params=params)
                if response.status_code in RETRY_STATUS and attempt < self._retries:
                    time.sleep(0.6 * (2**attempt))
                    continue
                response.raise_for_status()
                data = response.json() if response.content else None
                self._cache_put(key, data)
                return data
            except httpx.HTTPStatusError as exc:
                detail = exc.response.text[:300].replace("\n", " ")
                raise ApiError(
                    f"{exc.response.status_code} em {url}: {detail}"
                ) from exc
            except httpx.HTTPError as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                if attempt < self._retries:
                    time.sleep(0.6 * (2**attempt))
                    continue
        raise ApiError(f"sem resposta de {url} apos {self._retries + 1} tentativas ({last_error})")


def page_size(value: int) -> int:
    """Ambas as fontes exigem ``tamanhoPagina`` de no mínimo 10."""
    return max(MIN_PAGE_SIZE, min(int(value), 500))
