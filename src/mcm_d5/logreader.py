"""Read CAN capture files into frames for offline decoding.

Supports the common text formats natively (Linux ``candump`` logs and SavvyCAN
CSV exports) and defers to ``python-can`` for Vector ``.asc``/``.blf`` when the
optional ``[can]`` extra is installed. :func:`open_log` autodetects by file
extension and returns a :class:`~mcm_d5.link.ReplayLink` ready for a monitor.

Read-only: these helpers only parse existing captures.
"""

from __future__ import annotations

import csv
from collections.abc import Iterator

from mcm_d5.errors import McmD5Error
from mcm_d5.frame import J1939Frame
from mcm_d5.link import ReplayLink


def read_candump(path: str) -> Iterator[J1939Frame]:
    """Parse a ``candump`` log: ``(ts) iface  18FEF100#FFFF...``."""
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            token = next((t for t in line.split() if "#" in t), None)
            if token is None:
                continue
            id_str, _, data_str = token.partition("#")
            data_str = data_str.replace("#", "")  # CAN-FD marker, if any
            if len(data_str) % 2:
                continue
            try:
                can_id = int(id_str, 16)
                data = bytes.fromhex(data_str)
            except ValueError:
                continue
            yield J1939Frame.from_can_id(can_id, data)


def read_savvycan_csv(path: str) -> Iterator[J1939Frame]:
    """Parse a SavvyCAN CSV export (``Time Stamp,ID,Extended,...,LEN,D1..D8``)."""
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            id_raw = (row.get("ID") or "").strip()
            if not id_raw:
                continue
            try:
                can_id = int(id_raw, 16)
                length = int((row.get("LEN") or "0").strip() or 0)
                data = bytes(int(row[f"D{i}"], 16) for i in range(1, length + 1))
            except (ValueError, KeyError):
                continue
            yield J1939Frame.from_can_id(can_id, data)


def _read_via_python_can(path: str, reader_name: str) -> Iterator[J1939Frame]:
    try:
        import can.io  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dep
        raise ImportError(
            "reading .asc/.blf requires python-can; install with pip install 'mcm-d5[can]'"
        ) from exc
    reader_cls = getattr(can.io, reader_name)
    with reader_cls(path) as messages:  # pragma: no cover - optional dep
        for msg in messages:
            if msg.is_error_frame:
                continue
            yield J1939Frame.from_can_id(msg.arbitration_id, bytes(msg.data))


def open_log(path: str) -> ReplayLink:
    """Open a capture file as a :class:`ReplayLink`, autodetecting by extension."""
    lower = path.lower()
    if lower.endswith(".csv"):
        frames = read_savvycan_csv(path)
    elif lower.endswith(".asc"):
        frames = _read_via_python_can(path, "ASCReader")
    elif lower.endswith(".blf"):
        frames = _read_via_python_can(path, "BLFReader")
    elif lower.endswith((".log", ".candump", ".txt")):
        frames = read_candump(path)
    else:
        raise McmD5Error(f"unrecognized log extension: {path}")
    return ReplayLink(list(frames))
