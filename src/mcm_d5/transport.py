"""Transport abstraction for the MCM D5 client.

The client talks to the API service through a :class:`Transport`. This keeps
the wire details (HTTP method, headers, auth) in one place and lets tests
inject a fake transport instead of hitting the network.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable

from mcm_d5.errors import TransportError


@dataclass
class Response:
    """A minimal HTTP-like response returned by a transport."""

    status: int
    body: bytes

    def json(self) -> object:
        """Decode the body as JSON."""
        return json.loads(self.body.decode("utf-8"))


@runtime_checkable
class Transport(Protocol):
    """Protocol for performing read/write requests against the service.

    Implement this to back the client with a real HTTP library, a test
    double, or an alternate protocol.
    """

    def get(self, path: str) -> Response:
        """Perform a read request for ``path``."""
        ...

    def put(self, path: str, body: bytes) -> Response:
        """Perform a write request for ``path`` with ``body``."""
        ...


class HttpTransport:
    """A small ``urllib``-based transport.

    This is a stub-grade implementation good enough for the skeleton: it
    issues real HTTP requests but makes no assumptions about auth or
    pagination. Swap in a more capable transport (e.g. ``requests`` or
    ``httpx``) once the service contract is finalized.
    """

    def __init__(self, base_url: str, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _request(self, path: str, method: str, body: Optional[bytes]) -> Response:
        req = urllib.request.Request(self._url(path), data=body, method=method)
        if body is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return Response(status=resp.status, body=resp.read())
        except urllib.error.HTTPError as exc:  # 4xx/5xx
            return Response(status=exc.code, body=exc.read())
        except urllib.error.URLError as exc:  # network failure
            raise TransportError(f"request to {self._url(path)} failed: {exc.reason}") from exc

    def get(self, path: str) -> Response:
        return self._request(path, method="GET", body=None)

    def put(self, path: str, body: bytes) -> Response:
        return self._request(path, method="PUT", body=body)
