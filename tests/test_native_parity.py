"""Parity guard: the C++ core SPN table must match the Python signals table.

The desktop C++ core (desktop/core/src/mcm_core.cpp) mirrors a subset of
src/mcm_d5/signals.py. This test parses the C++ SignalDef tables and asserts
that, for every PGN the C++ core implements, each signal's start byte, length,
scale, and offset match the Python definition. Keeps the two in sync.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from mcm_d5.signals import PGN_SIGNALS

CORE_CPP = Path(__file__).resolve().parents[1] / "desktop" / "core" / "src" / "mcm_core.cpp"

_ROW = re.compile(
    r'\{\s*(\d+)\s*,\s*"[^"]*"\s*,\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*"[^"]*"\s*\}'
)


def _parse_core():
    text = CORE_CPP.read_text()

    arrays: dict[str, list[tuple]] = {}
    for m in re.finditer(r"const SignalDef (\w+)\[\]\s*=\s*\{(.*?)\};", text, re.S):
        name, body = m.group(1), m.group(2)
        sigs = []
        for row in _ROW.finditer(body):
            spn = int(row.group(1))
            start = int(row.group(2))
            length = int(row.group(3))
            scale = eval(row.group(4))  # e.g. "0.125" or "1.0 / 256.0"
            offset = float(row.group(5))
            sigs.append((spn, start, length, scale, offset))
        arrays[name] = sigs

    pgns_block = re.search(r"const PgnDef PGNS\[\]\s*=\s*\{(.*?)\};", text, re.S).group(1)
    pgn_map = {
        int(m.group(1)): m.group(2)
        for m in re.finditer(r"\{\s*(\d+)\s*,\s*(\w+)\s*,\s*\d+\s*\}", pgns_block)
    }
    return pgn_map, arrays


def test_core_table_parses():
    pgn_map, arrays = _parse_core()
    assert pgn_map, "no PGNs parsed from C++ core"
    assert arrays, "no SignalDef arrays parsed from C++ core"


def test_cpp_signals_match_python():
    pgn_map, arrays = _parse_core()
    for pgn, array_name in pgn_map.items():
        assert pgn in PGN_SIGNALS, f"C++ PGN {pgn} missing from Python signals table"
        py_by_spn = {s.spn: s for s in PGN_SIGNALS[pgn]}
        for spn, start, length, scale, offset in arrays[array_name]:
            assert spn in py_by_spn, f"C++ SPN {spn} (PGN {pgn}) missing from Python"
            py = py_by_spn[spn]
            assert py.start_byte == start, f"SPN {spn}: start {start} != {py.start_byte}"
            assert py.length == length, f"SPN {spn}: length {length} != {py.length}"
            assert py.scale == pytest.approx(scale), f"SPN {spn}: scale mismatch"
            assert py.offset == pytest.approx(offset), f"SPN {spn}: offset mismatch"
