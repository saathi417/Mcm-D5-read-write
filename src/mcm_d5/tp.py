"""J1939 Transport Protocol (TP) reassembly — receive side only.

Multi-packet J1939 messages are split across TP.CM (connection management,
PGN 60416) and TP.DT (data transfer, PGN 60160) frames. This reassembler
passively observes those frames and, when a message is complete, returns a
synthesized :class:`J1939Frame` carrying the full reassembled payload under
its real PGN — so a multi-DTC DM1, a VIN, or a component ID decodes normally.

It handles BAM (broadcast) sessions, and reassembles RTS/CTS sessions by
passively watching the data transfer; it never sends CTS or any other frame.
"""

from __future__ import annotations

from typing import Dict, Optional

from mcm_d5.frame import J1939Frame

TP_CM_PGN = 60416  # 0xEC00 — Transport Protocol, Connection Management
TP_DT_PGN = 60160  # 0xEB00 — Transport Protocol, Data Transfer

CONTROL_RTS = 0x10  # Request To Send (destination-specific session)
CONTROL_BAM = 0x20  # Broadcast Announce Message


class _Session:
    __slots__ = ("total", "num_packets", "pgn", "priority", "packets")

    def __init__(self, total: int, num_packets: int, pgn: int, priority: int) -> None:
        self.total = total
        self.num_packets = num_packets
        self.pgn = pgn
        self.priority = priority
        self.packets: Dict[int, bytes] = {}


class TransportProtocolReassembler:
    """Passively reassembles TP sessions keyed by source address."""

    def __init__(self) -> None:
        self._sessions: Dict[int, _Session] = {}

    def observe(self, frame: J1939Frame) -> Optional[J1939Frame]:
        """Feed a frame; returns the reassembled frame when one completes."""
        if frame.pgn == TP_CM_PGN:
            self._handle_cm(frame)
            return None
        if frame.pgn == TP_DT_PGN:
            return self._handle_dt(frame)
        return None

    def _handle_cm(self, frame: J1939Frame) -> None:
        d = frame.data
        if len(d) < 8:
            return
        control = d[0]
        if control in (CONTROL_BAM, CONTROL_RTS):
            total = d[1] | (d[2] << 8)
            num_packets = d[3]
            pgn = d[5] | (d[6] << 8) | (d[7] << 16)
            self._sessions[frame.source] = _Session(total, num_packets, pgn, frame.priority)

    def _handle_dt(self, frame: J1939Frame) -> Optional[J1939Frame]:
        d = frame.data
        if not d:
            return None
        session = self._sessions.get(frame.source)
        if session is None:
            return None
        seq = d[0]
        session.packets[seq] = bytes(d[1:8])
        if len(session.packets) < session.num_packets:
            return None

        # Complete: concatenate packets in sequence order and trim to size.
        buf = bytearray()
        for i in range(1, session.num_packets + 1):
            buf.extend(session.packets.get(i, b"\xff" * 7))
        data = bytes(buf[: session.total])
        del self._sessions[frame.source]
        return J1939Frame(
            can_id=0,  # synthesized: reassembled message has no single CAN id
            data=data,
            priority=session.priority,
            pgn=session.pgn,
            source=frame.source,
            destination=None,
        )
