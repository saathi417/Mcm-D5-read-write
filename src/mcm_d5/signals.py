"""J1939 signal (SPN) decoding for common engine and aftertreatment data.

Each :class:`Signal` describes how to extract one SPN from a PGN's payload:
the start byte (0-indexed within the PGN data), length in bytes, and the
linear ``raw * scale + offset`` conversion to engineering units.

Only a representative, commonly-broadcast subset is included here. Scaling
and byte positions follow SAE J1939-71; **verify against your engine's own
DBC before relying on absolute values**, since OEMs occasionally deviate.
This is read-only decoding of data already on the bus — nothing is requested
or written.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Signal:
    spn: int
    name: str
    start_byte: int
    length: int
    scale: float
    offset: float
    unit: str

    def decode(self, data: bytes) -> Optional[float]:
        """Decode this signal from ``data``; ``None`` if absent/not-available."""
        end = self.start_byte + self.length
        if len(data) < end:
            return None
        raw = int.from_bytes(data[self.start_byte:end], "little")
        # J1939 reserves the top two raw values per byte-width for
        # "error" (0xFE..) and "not available" (0xFF..) indicators.
        if raw >= (1 << (8 * self.length)) - 2:
            return None
        return raw * self.scale + self.offset


# PGN -> signals. PGNs are given in decimal with the hex in a comment.
PGN_SIGNALS: Dict[int, List[Signal]] = {
    61444: [  # EEC1 — Electronic Engine Controller 1 (0xF004)
        Signal(513, "Actual Engine - Percent Torque", 2, 1, 1.0, -125.0, "%"),
        Signal(190, "Engine Speed", 3, 2, 0.125, 0.0, "rpm"),
    ],
    65262: [  # ET1 — Engine Temperature 1 (0xFEEE)
        Signal(110, "Engine Coolant Temperature", 0, 1, 1.0, -40.0, "degC"),
        Signal(175, "Engine Oil Temperature 1", 2, 2, 0.03125, -273.0, "degC"),
    ],
    65263: [  # EFL/P1 — Engine Fluid Level/Pressure 1 (0xFEEF)
        Signal(100, "Engine Oil Pressure", 3, 1, 4.0, 0.0, "kPa"),
    ],
    65270: [  # IC1 — Inlet/Exhaust Conditions 1 (0xFEF6)
        Signal(102, "Engine Intake Manifold #1 Pressure (boost)", 1, 1, 2.0, 0.0, "kPa"),
        Signal(105, "Engine Intake Manifold 1 Temperature", 2, 1, 1.0, -40.0, "degC"),
        Signal(173, "Engine Exhaust Gas Temperature", 5, 2, 0.03125, -273.0, "degC"),
    ],
    65266: [  # LFE1 — Fuel Economy (Liquid) (0xFEF2)
        Signal(183, "Engine Fuel Rate", 0, 2, 0.05, 0.0, "L/h"),
    ],
    65265: [  # CCVS1 — Cruise Control/Vehicle Speed 1 (0xFEF1)
        Signal(84, "Wheel-Based Vehicle Speed", 1, 2, 1.0 / 256.0, 0.0, "km/h"),
    ],
    65276: [  # DD — Dash Display (0xFEFC)
        Signal(96, "Fuel Level 1", 1, 1, 0.4, 0.0, "%"),
    ],
    65110: [  # AT1T1I — Aftertreatment 1 DEF Tank 1 Information (0xFEC6)
        Signal(1761, "Aftertreatment 1 DEF Tank Volume", 0, 1, 0.4, 0.0, "%"),
        Signal(3031, "Aftertreatment 1 DEF Tank Temperature 1", 1, 1, 1.0, -40.0, "degC"),
    ],
    61454: [  # AT1IG1 — Aftertreatment 1 Intake Gas 1 (0xF00E)
        Signal(3216, "Aftertreatment 1 Intake NOx", 0, 2, 0.05, -200.0, "ppm"),
    ],
    61455: [  # AT1OG1 — Aftertreatment 1 Outlet Gas 1 (0xF00F)
        Signal(3226, "Aftertreatment 1 Outlet NOx", 0, 2, 0.05, -200.0, "ppm"),
    ],
}


def decode_pgn(pgn: int, data: bytes) -> Dict[str, float]:
    """Decode all known signals for ``pgn`` into ``{name: value}``.

    Unknown PGNs and not-available signals are simply omitted.
    """
    out: Dict[str, float] = {}
    for sig in PGN_SIGNALS.get(pgn, ()):
        value = sig.decode(data)
        if value is not None:
            out[sig.name] = value
    return out
