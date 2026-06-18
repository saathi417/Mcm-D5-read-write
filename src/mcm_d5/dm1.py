"""J1939 diagnostic trouble code (DTC) parsing — DM1 and DM2.

DM1 (PGN 65226) reports *active* DTCs; DM2 (PGN 65227) reports *previously
active* DTCs. Both share the same layout: two lamp-status bytes followed by
one or more 4-byte DTCs.

This module parses an already-assembled payload. Messages carrying more than
one DTC arrive via the J1939 Transport Protocol (BAM/RTS-CTS) and must be
reassembled first; pass the reassembled data here. Parsing is read-only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from mcm_d5.errors import DecodeError

DM1_PGN = 65226  # 0xFECA — active DTCs
DM2_PGN = 65227  # 0xFECB — previously active DTCs
DM6_PGN = 65231  # 0xFECF — pending DTCs
DM27_PGN = 64898  # 0xFD82 — all pending DTCs
DM28_PGN = 64896  # 0xFD80 — permanent DTCs
DM5_PGN = 65230  # 0xFECE — diagnostic readiness 1

# DM messages that share the lamp + 4-byte-DTC layout parsed by parse_diagnostic.
DTC_DIAGNOSTIC_PGNS = frozenset({DM1_PGN, DM2_PGN, DM6_PGN, DM27_PGN, DM28_PGN})


@dataclass(frozen=True)
class Dtc:
    """A single diagnostic trouble code."""

    spn: int  # Suspect Parameter Number
    fmi: int  # Failure Mode Identifier
    occurrence_count: int


@dataclass(frozen=True)
class DiagnosticMessage:
    """Decoded DM1/DM2 message: lamp status plus the list of DTCs."""

    malfunction_indicator_lamp: bool
    red_stop_lamp: bool
    amber_warning_lamp: bool
    protect_lamp: bool
    dtcs: List[Dtc]


def _lamp_on(two_bits: int) -> bool:
    # 00 = off, 01 = on, 10/11 = reserved / not available.
    return two_bits == 0b01


def parse_diagnostic(payload: bytes) -> DiagnosticMessage:
    """Parse a (reassembled) DM1/DM2 payload."""
    if len(payload) < 2:
        raise DecodeError("DM1/DM2 payload must be at least 2 bytes")

    lamp = payload[0]
    msg_lamps = dict(
        malfunction_indicator_lamp=_lamp_on((lamp >> 6) & 0x03),
        red_stop_lamp=_lamp_on((lamp >> 4) & 0x03),
        amber_warning_lamp=_lamp_on((lamp >> 2) & 0x03),
        protect_lamp=_lamp_on(lamp & 0x03),
    )

    dtcs: List[Dtc] = []
    body = payload[2:]
    for i in range(0, len(body) - 3, 4):
        b0, b1, b2, b3 = body[i], body[i + 1], body[i + 2], body[i + 3]
        spn = b0 | (b1 << 8) | ((b2 >> 5) << 16)
        fmi = b2 & 0x1F
        occurrence = b3 & 0x7F
        if spn == 0 and fmi == 0:
            continue  # padding / "no active fault" placeholder
        dtcs.append(Dtc(spn=spn, fmi=fmi, occurrence_count=occurrence))

    return DiagnosticMessage(dtcs=dtcs, **msg_lamps)


@dataclass(frozen=True)
class DiagnosticReadiness:
    """Decoded DM5 (Diagnostic Readiness 1) summary."""

    active_trouble_codes: int
    previously_active_trouble_codes: int
    obd_compliance: int


def parse_readiness(payload: bytes) -> DiagnosticReadiness:
    """Parse a DM5 (PGN 65230) payload."""
    if len(payload) < 3:
        raise DecodeError("DM5 payload must be at least 3 bytes")
    return DiagnosticReadiness(
        active_trouble_codes=payload[0],
        previously_active_trouble_codes=payload[1],
        obd_compliance=payload[2],
    )
