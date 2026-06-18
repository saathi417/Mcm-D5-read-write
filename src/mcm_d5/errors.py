"""Exception types for the mcm_d5 read-only diagnostics package."""


class McmD5Error(Exception):
    """Base class for all errors raised by this package."""


class DecodeError(McmD5Error):
    """Raised when a frame or payload cannot be decoded."""


class LinkError(McmD5Error):
    """Raised when the underlying CAN link fails."""
