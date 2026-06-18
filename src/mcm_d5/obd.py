"""Light-duty OBD-II / SAE J1979 read helpers (read-only).

Builds Mode 0x01 (current data) PID requests and Mode 0x03 (stored DTCs)
requests, and parses their responses. DTCs are formatted to the standard
ISO 15031-5 code (e.g. ``P0301``). Pairs well with an ELM327-style adapter.

Read-only: only Modes 0x01 and 0x03 are implemented — no clearing (Mode 0x04),
no actuator/control modes. Pure functions do no I/O; :class:`ObdReadClient`
sends/receives over a caller-supplied transceiver.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Protocol, Tuple

from mcm_d5.errors import McmD5Error

MODE_CURRENT_DATA = 0x01
MODE_STORED_DTCS = 0x03


# pid -> (name, num_bytes, converter, unit)
_PID_TABLE: Dict[int, Tuple[str, int, Callable[[bytes], float], str]] = {
    0x04: ("Calculated Engine Load", 1, lambda d: d[0] * 100.0 / 255.0, "%"),
    0x05: ("Engine Coolant Temperature", 1, lambda d: d[0] - 40.0, "degC"),
    0x0C: ("Engine RPM", 2, lambda d: (d[0] * 256 + d[1]) / 4.0, "rpm"),
    0x0D: ("Vehicle Speed", 1, lambda d: float(d[0]), "km/h"),
    0x0F: ("Intake Air Temperature", 1, lambda d: d[0] - 40.0, "degC"),
    0x11: ("Throttle Position", 1, lambda d: d[0] * 100.0 / 255.0, "%"),
    0x2F: ("Fuel Tank Level Input", 1, lambda d: d[0] * 100.0 / 255.0, "%"),
}


def build_pid_request(pid: int) -> bytes:
    if not 0 <= pid <= 0xFF:
        raise ValueError("pid must be a byte")
    return bytes([MODE_CURRENT_DATA, pid])


def build_read_stored_dtcs() -> bytes:
    return bytes([MODE_STORED_DTCS])


@dataclass(frozen=True)
class PidValue:
    pid: int
    name: str
    value: float
    unit: str


def parse_pid_response(response: bytes) -> PidValue:
    """Parse a Mode 0x01 positive response (``0x41 pid data...``)."""
    if len(response) < 2 or response[0] != MODE_CURRENT_DATA + 0x40:
        raise McmD5Error("not a Mode 0x01 positive response")
    pid = response[1]
    if pid not in _PID_TABLE:
        raise McmD5Error(f"unsupported PID 0x{pid:02X}")
    name, nbytes, conv, unit = _PID_TABLE[pid]
    data = response[2:2 + nbytes]
    if len(data) < nbytes:
        raise McmD5Error("PID response truncated")
    return PidValue(pid=pid, name=name, value=conv(data), unit=unit)


def decode_dtc(high: int, low: int) -> str:
    """Decode a 2-byte OBD-II DTC into its standard code (e.g. ``P0301``)."""
    letter = "PCBU"[(high & 0xC0) >> 6]
    return f"{letter}{(high & 0x30) >> 4}{high & 0x0F:X}{(low & 0xF0) >> 4:X}{low & 0x0F:X}"


def parse_stored_dtcs(response: bytes) -> List[str]:
    """Parse a Mode 0x03 positive response into a list of DTC codes."""
    if not response or response[0] != MODE_STORED_DTCS + 0x40:
        raise McmD5Error("not a Mode 0x03 positive response")
    body = response[1:]
    codes: List[str] = []
    for i in range(0, len(body) - 1, 2):
        high, low = body[i], body[i + 1]
        if high == 0 and low == 0:
            continue  # empty slot
        codes.append(decode_dtc(high, low))
    return codes


class Transceiver(Protocol):
    def request(self, payload: bytes, timeout: float = 2.0) -> bytes:
        ...


class ObdReadClient:
    """Read-only OBD-II client: current-data PIDs and stored DTCs only."""

    def __init__(self, transceiver: Transceiver) -> None:
        self._tx = transceiver

    def read_pid(self, pid: int, timeout: float = 2.0) -> PidValue:
        return parse_pid_response(self._tx.request(build_pid_request(pid), timeout=timeout))

    def read_stored_dtcs(self, timeout: float = 2.0) -> List[str]:
        return parse_stored_dtcs(self._tx.request(build_read_stored_dtcs(), timeout=timeout))
