"""Exception types raised by the MCM D5 client."""


class McmD5Error(Exception):
    """Base class for all errors raised by this package."""


class TransportError(McmD5Error):
    """Raised when the underlying transport fails (network, bad status, etc.)."""


class NotFoundError(McmD5Error):
    """Raised by :meth:`McmD5Client.read` when a key does not exist."""
