"""Client for reading from and writing to the MCM D5 API service.

This is the skeleton interface. The two public operations are
:meth:`McmD5Client.read` and :meth:`McmD5Client.write`; they translate a
logical key into a service path and delegate the wire work to a
:class:`~mcm_d5.transport.Transport`.

The request/response shape here (JSON ``{"value": ...}`` envelope) is a
placeholder. Adjust :meth:`read`/:meth:`write` once the real MCM D5 service
contract is known.
"""

from __future__ import annotations

import json
from typing import Any, Optional

from mcm_d5.errors import NotFoundError, TransportError
from mcm_d5.transport import HttpTransport, Transport


class McmD5Client:
    """Read/write client for the MCM D5 service.

    Args:
        base_url: Base URL of the service. Required unless a ``transport``
            is supplied.
        transport: Transport to use. Defaults to an :class:`HttpTransport`
            built from ``base_url``. Inject a fake here in tests.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        transport: Optional[Transport] = None,
    ) -> None:
        if transport is None:
            if base_url is None:
                raise ValueError("either base_url or transport must be provided")
            transport = HttpTransport(base_url)
        self._transport = transport

    @staticmethod
    def _path(key: str) -> str:
        if not key:
            raise ValueError("key must be a non-empty string")
        return f"d5/{key}"

    def read(self, key: str) -> Any:
        """Read the value stored at ``key``.

        Raises:
            NotFoundError: if the key does not exist (HTTP 404).
            TransportError: on any other non-success status.
        """
        resp = self._transport.get(self._path(key))
        if resp.status == 404:
            raise NotFoundError(f"key not found: {key}")
        if resp.status >= 400:
            raise TransportError(f"read {key} failed with status {resp.status}")
        return resp.json()["value"]

    def write(self, key: str, value: Any) -> None:
        """Write ``value`` to ``key``.

        Raises:
            TransportError: on any non-success status.
        """
        body = json.dumps({"value": value}).encode("utf-8")
        resp = self._transport.put(self._path(key), body)
        if resp.status >= 400:
            raise TransportError(f"write {key} failed with status {resp.status}")
