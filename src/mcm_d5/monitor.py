"""Passive J1939 monitor: decode live data and read fault codes.

Pulls frames from a :class:`~mcm_d5.link.Link`, decodes known PGNs into named
signals, and parses DM1/DM2 diagnostic messages. It registers callbacks for
new signal values and for DTC messages, and keeps the latest value of every
decoded signal in :attr:`latest`.

The monitor never transmits. It cannot perform security access, clear codes,
reset a derate, or write to a module — it only listens.
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

from mcm_d5.dm1 import (
    DM5_PGN,
    DTC_DIAGNOSTIC_PGNS,
    DiagnosticMessage,
    DiagnosticReadiness,
    parse_diagnostic,
    parse_readiness,
)
from mcm_d5.frame import J1939Frame
from mcm_d5.link import Link
from mcm_d5.signals import decode_pgn
from mcm_d5.tp import TP_CM_PGN, TP_DT_PGN, TransportProtocolReassembler

SignalCallback = Callable[[str, float, J1939Frame], None]
DiagnosticCallback = Callable[[DiagnosticMessage, J1939Frame], None]
ReadinessCallback = Callable[[DiagnosticReadiness, J1939Frame], None]


class J1939Monitor:
    def __init__(self, link: Link) -> None:
        self._link = link
        self._signal_cbs: List[SignalCallback] = []
        self._diag_cbs: List[DiagnosticCallback] = []
        self._readiness_cbs: List[ReadinessCallback] = []
        self._tp = TransportProtocolReassembler()
        self.latest: Dict[str, float] = {}

    def on_signal(self, callback: SignalCallback) -> None:
        """Register a callback invoked for each decoded signal value."""
        self._signal_cbs.append(callback)

    def on_diagnostic(self, callback: DiagnosticCallback) -> None:
        """Register a callback invoked for each DTC message (DM1/2/6/27/28)."""
        self._diag_cbs.append(callback)

    def on_readiness(self, callback: ReadinessCallback) -> None:
        """Register a callback invoked for each DM5 readiness message."""
        self._readiness_cbs.append(callback)

    def handle(self, frame: J1939Frame) -> None:
        """Decode and dispatch a single frame."""
        if frame.pgn in (TP_CM_PGN, TP_DT_PGN):
            reassembled = self._tp.observe(frame)
            if reassembled is not None:
                self.handle(reassembled)
            return
        if frame.pgn in DTC_DIAGNOSTIC_PGNS:
            diag = parse_diagnostic(frame.data)
            for diag_cb in self._diag_cbs:
                diag_cb(diag, frame)
            return
        if frame.pgn == DM5_PGN:
            readiness = parse_readiness(frame.data)
            for readiness_cb in self._readiness_cbs:
                readiness_cb(readiness, frame)
            return
        for name, value in decode_pgn(frame.pgn, frame.data).items():
            self.latest[name] = value
            for signal_cb in self._signal_cbs:
                signal_cb(name, value, frame)

    def pump(self, max_frames: Optional[int] = None, timeout: float = 1.0) -> int:
        """Read and process frames until the link is exhausted or the limit hits.

        Returns the number of frames processed. With ``max_frames=None`` this
        runs until ``recv`` returns ``None`` (e.g. a finished log replay).
        """
        count = 0
        while max_frames is None or count < max_frames:
            frame = self._link.recv(timeout=timeout)
            if frame is None:
                break
            self.handle(frame)
            count += 1
        return count
