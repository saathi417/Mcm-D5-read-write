"""MCM D5 read/write client package.

Exposes a small client for reading from and writing to the MCM D5 API
service. The HTTP layer is pluggable (see :class:`~mcm_d5.transport.Transport`)
so the client can be exercised in tests without a live service.
"""

from mcm_d5.client import McmD5Client
from mcm_d5.errors import McmD5Error, NotFoundError, TransportError
from mcm_d5.transport import HttpTransport, Response, Transport

__all__ = [
    "McmD5Client",
    "McmD5Error",
    "NotFoundError",
    "TransportError",
    "Transport",
    "HttpTransport",
    "Response",
]

__version__ = "0.1.0"
