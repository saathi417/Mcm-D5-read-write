"""Read-only UDS (ISO 14229) helpers.

This module deliberately implements **only** the diagnostic *read* services:

- ``0x22`` ReadDataByIdentifier
- ``0x19`` ReadDTCInformation
- ``0x3E`` TesterPresent (keep-alive)

It intentionally does **not** implement SecurityAccess (0x27), session changes
into programming mode, RequestDownload/Upload/TransferData (0x34/0x35/0x36/
0x37), WriteDataByIdentifier/WriteMemoryByAddress (0x2E/0x3D), ClearDTC (0x14),
or RoutineControl (0x31). The request builders here can only produce read
requests.

The pure functions (``build_*`` / ``parse_*``) do no I/O. :class:`UdsReadClient`
sends a request and reads the response over a caller-supplied transceiver, but
is restricted to the read services above.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Protocol

from mcm_d5.errors import McmD5Error

# Service IDs (request) and their positive-response IDs (request + 0x40).
SID_READ_DATA_BY_ID = 0x22
SID_READ_DTC_INFO = 0x19
SID_TESTER_PRESENT = 0x3E
NEGATIVE_RESPONSE = 0x7F

# ReadDTCInformation sub-function: report DTCs by status mask.
DTC_SUBFN_BY_STATUS_MASK = 0x02


class NegativeResponse(McmD5Error):
    """The ECU returned a UDS negative response (0x7F)."""

    def __init__(self, service: int, nrc: int) -> None:
        super().__init__(f"negative response to service 0x{service:02X}: NRC 0x{nrc:02X}")
        self.service = service
        self.nrc = nrc


# --- request builders (read-only) ----------------------------------------

def build_read_data_by_identifier(did: int) -> bytes:
    """Build a ReadDataByIdentifier (0x22) request for a 16-bit DID."""
    if not 0 <= did <= 0xFFFF:
        raise ValueError("DID must be a 16-bit value")
    return bytes([SID_READ_DATA_BY_ID, (did >> 8) & 0xFF, did & 0xFF])


def build_read_dtc_by_status_mask(status_mask: int = 0xFF) -> bytes:
    """Build a ReadDTCInformation (0x19) request, sub-function 0x02."""
    if not 0 <= status_mask <= 0xFF:
        raise ValueError("status_mask must be a byte")
    return bytes([SID_READ_DTC_INFO, DTC_SUBFN_BY_STATUS_MASK, status_mask])


def build_tester_present() -> bytes:
    """Build a TesterPresent (0x3E) keep-alive request (suppress response off)."""
    return bytes([SID_TESTER_PRESENT, 0x00])


# --- response parsing ------------------------------------------------------

def _check_negative(response: bytes, expected_sid: int) -> None:
    if response and response[0] == NEGATIVE_RESPONSE and len(response) >= 3:
        raise NegativeResponse(service=response[1], nrc=response[2])
    if not response or response[0] != expected_sid + 0x40:
        raise McmD5Error(
            f"unexpected response 0x{response[0]:02X} for service 0x{expected_sid:02X}"
            if response
            else "empty response"
        )


def parse_read_data_by_identifier(response: bytes) -> "DataByIdentifier":
    """Parse a 0x62 positive response into its DID and data record."""
    _check_negative(response, SID_READ_DATA_BY_ID)
    if len(response) < 3:
        raise McmD5Error("ReadDataByIdentifier response too short")
    did = (response[1] << 8) | response[2]
    return DataByIdentifier(did=did, data=bytes(response[3:]))


def parse_read_dtc_by_status_mask(response: bytes) -> "DtcReport":
    """Parse a 0x59 positive response (sub-function 0x02) into DTC records."""
    _check_negative(response, SID_READ_DTC_INFO)
    if len(response) < 3:
        raise McmD5Error("ReadDTCInformation response too short")
    availability_mask = response[2]
    records: List[UdsDtc] = []
    body = response[3:]
    for i in range(0, len(body) - 3, 4):
        dtc = (body[i] << 16) | (body[i + 1] << 8) | body[i + 2]
        status = body[i + 3]
        records.append(UdsDtc(dtc=dtc, status=status))
    return DtcReport(status_availability_mask=availability_mask, dtcs=records)


@dataclass(frozen=True)
class DataByIdentifier:
    did: int
    data: bytes


@dataclass(frozen=True)
class UdsDtc:
    dtc: int  # 3-byte DTC (e.g. ISO 15031 / manufacturer format)
    status: int  # status byte (testFailed, confirmed, etc.)


@dataclass(frozen=True)
class DtcReport:
    status_availability_mask: int
    dtcs: List[UdsDtc]


# --- thin client (read services only) --------------------------------------

class Transceiver(Protocol):
    """A request/response channel (e.g. ISO-TP over CAN)."""

    def request(self, payload: bytes, timeout: float = 2.0) -> bytes:
        ...


class UdsReadClient:
    """Read-only UDS client. Exposes only ReadDataByIdentifier, ReadDTC, and
    TesterPresent; there is no method that writes, unlocks, or programs."""

    def __init__(self, transceiver: Transceiver) -> None:
        self._tx = transceiver

    def read_data_by_identifier(self, did: int, timeout: float = 2.0) -> DataByIdentifier:
        resp = self._tx.request(build_read_data_by_identifier(did), timeout=timeout)
        return parse_read_data_by_identifier(resp)

    def read_dtcs(self, status_mask: int = 0xFF, timeout: float = 2.0) -> DtcReport:
        resp = self._tx.request(build_read_dtc_by_status_mask(status_mask), timeout=timeout)
        return parse_read_dtc_by_status_mask(resp)

    def tester_present(self, timeout: float = 2.0) -> None:
        self._tx.request(build_tester_present(), timeout=timeout)
