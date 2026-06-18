"""SAE J1939 frame model.

Parses a 29-bit extended CAN identifier into its J1939 fields (priority,
PGN, source address, and — for PDU1 messages — destination address).

This module is purely passive: it interprets identifiers and data bytes that
were already received off the bus. It does not transmit anything.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

CAN_EXT_MASK = 0x1FFFFFFF


@dataclass(frozen=True)
class J1939Frame:
    """A decoded J1939 message.

    Attributes:
        can_id: The raw 29-bit extended CAN identifier.
        data: The payload bytes (0-8 for classic CAN).
        priority: 3-bit message priority (0 = highest).
        pgn: Parameter Group Number.
        source: Source address (the node that sent the message).
        destination: Destination address for PDU1 (destination-specific)
            messages; ``None`` for PDU2 (broadcast) messages.
    """

    can_id: int
    data: bytes
    priority: int
    pgn: int
    source: int
    destination: Optional[int]

    @classmethod
    def from_can_id(cls, can_id: int, data: bytes) -> J1939Frame:
        """Build a frame from a raw extended CAN id and payload."""
        cid = can_id & CAN_EXT_MASK
        source = cid & 0xFF
        ps = (cid >> 8) & 0xFF
        pf = (cid >> 16) & 0xFF
        dp = (cid >> 24) & 0x01
        edp = (cid >> 25) & 0x01
        priority = (cid >> 26) & 0x07

        if pf < 240:  # PDU1 — destination specific
            pgn = (edp << 17) | (dp << 16) | (pf << 8)
            destination = ps
        else:  # PDU2 — broadcast; PS is the group extension
            pgn = (edp << 17) | (dp << 16) | (pf << 8) | ps
            destination = None

        return cls(
            can_id=cid,
            data=bytes(data),
            priority=priority,
            pgn=pgn,
            source=source,
            destination=destination,
        )
