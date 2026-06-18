"""mcm_d5 — read-only J1939 / UDS diagnostics for the MCM D5 platform.

Passive monitoring and diagnostic *reads* only: decode live broadcast data,
parse DM1/DM2 fault codes, and issue UDS read services (ReadDataByIdentifier,
ReadDTCInformation, TesterPresent). The package has no ability to perform
security access, clear codes, reset a derate, or write/flash a module.
"""

from mcm_d5.dm1 import (
    DM1_PGN,
    DM2_PGN,
    DiagnosticMessage,
    Dtc,
    parse_diagnostic,
)
from mcm_d5.dbc import DbcDecoder
from mcm_d5.errors import DecodeError, LinkError, McmD5Error
from mcm_d5.frame import J1939Frame
from mcm_d5.link import Link, PythonCanLink, ReplayLink
from mcm_d5.monitor import J1939Monitor
from mcm_d5.obd import (
    ObdReadClient,
    PidValue,
    build_pid_request,
    build_read_stored_dtcs,
    decode_dtc,
    parse_pid_response,
    parse_stored_dtcs,
)
from mcm_d5.signals import PGN_SIGNALS, Signal, decode_pgn
from mcm_d5.uds import (
    DataByIdentifier,
    DtcReport,
    NegativeResponse,
    UdsDtc,
    UdsReadClient,
    build_read_data_by_identifier,
    build_read_dtc_by_status_mask,
    build_tester_present,
)

__all__ = [
    "McmD5Error",
    "DecodeError",
    "LinkError",
    "J1939Frame",
    "Link",
    "ReplayLink",
    "PythonCanLink",
    "J1939Monitor",
    "Signal",
    "PGN_SIGNALS",
    "decode_pgn",
    "DM1_PGN",
    "DM2_PGN",
    "Dtc",
    "DiagnosticMessage",
    "parse_diagnostic",
    "UdsReadClient",
    "DataByIdentifier",
    "DtcReport",
    "UdsDtc",
    "NegativeResponse",
    "build_read_data_by_identifier",
    "build_read_dtc_by_status_mask",
    "build_tester_present",
    "ObdReadClient",
    "PidValue",
    "build_pid_request",
    "build_read_stored_dtcs",
    "parse_pid_response",
    "parse_stored_dtcs",
    "decode_dtc",
    "DbcDecoder",
]

__version__ = "0.2.0"
