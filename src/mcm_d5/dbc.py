"""DBC-based signal decoding via the optional ``cantools`` library.

Lets you decode frames against a DBC file (e.g. an opendbc database or one
exported from SavvyCAN) instead of, or alongside, the built-in J1939 SPN
table in :mod:`mcm_d5.signals`. Decoding only — DBC files are never written.

Install the extra with ``pip install 'mcm-d5[dbc]'``.
"""

from __future__ import annotations

from typing import Dict

from mcm_d5.frame import J1939Frame


class DbcDecoder:
    """Decode CAN frames using a loaded ``cantools`` database."""

    def __init__(self, database) -> None:  # type: ignore[no-untyped-def]
        self._db = database

    @classmethod
    def from_file(cls, path: str) -> "DbcDecoder":
        try:
            import cantools  # type: ignore
        except ImportError as exc:  # pragma: no cover - optional dep
            raise ImportError(
                "DbcDecoder requires 'cantools'; install with pip install 'mcm-d5[dbc]'"
            ) from exc
        return cls(cantools.database.load_file(path))

    def decode(self, can_id: int, data: bytes) -> Dict[str, object]:
        """Decode raw ``data`` for ``can_id``; ``{}`` if the id is unknown."""
        try:
            message = self._db.get_message_by_frame_id(can_id)
        except KeyError:
            return {}
        return dict(message.decode(bytes(data), decode_choices=False))

    def decode_frame(self, frame: J1939Frame) -> Dict[str, object]:
        """Decode a :class:`J1939Frame` using its raw CAN id."""
        return self.decode(frame.can_id, frame.data)
