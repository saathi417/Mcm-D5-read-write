# Mcm-D5-read-write

A small Python library for **read-only diagnostics** on the MCM D5 platform:
decode live SAE J1939 data, read DM1/DM2 fault codes, and issue UDS read
services. It connects to a CAN adapter for **listening only** — it does not
transmit control commands, perform security access, clear codes, reset a
derate, or write/flash any module.

## Install

```bash
pip install -e ".[dev]"              # library + tests
pip install -e ".[dev,can]"          # + python-can for live capture
pip install -e ".[dev,can,dbc]"      # + cantools for DBC decoding
```

## Live monitor (connect for read)

```bash
python examples/live_monitor.py --interface socketcan --channel can0 --bitrate 250000
```

Any `python-can` interface works (SocketCAN, and RP1210/J2534 bridges for a
NEXIQ-style adapter). Decoding is the same regardless of adapter.

## Library usage

```python
from mcm_d5 import J1939Monitor, PythonCanLink

link = PythonCanLink.open("can0", interface="socketcan", bitrate=250000)
mon = J1939Monitor(link)
mon.on_signal(lambda name, value, frame: print(name, value))
mon.on_diagnostic(lambda diag, frame: print("DTCs:", diag.dtcs))
mon.pump()
```

Offline decoding / tests use `ReplayLink` instead of hardware:

```python
from mcm_d5 import J1939Frame, J1939Monitor, ReplayLink

frames = [J1939Frame.from_can_id(0x0CF00400, b"...")]
J1939Monitor(ReplayLink(frames)).pump()
```

### Light-duty OBD-II (J1979)

`ObdReadClient` reads Mode 0x01 current-data PIDs (RPM, coolant temp, speed,
load, throttle, fuel level, …) and Mode 0x03 stored DTCs (decoded to codes
like `P0301`) over an ELM327-style transceiver. Read-only — no Mode 0x04 clear.

### DBC decoding (SavvyCAN / opendbc)

`DbcDecoder.from_file("engine.dbc")` decodes frames against any DBC database
via `cantools`, as an alternative/complement to the built-in J1939 table.

### UDS read services

`UdsReadClient` exposes only `read_data_by_identifier` (0x22), `read_dtcs`
(0x19), and `tester_present` (0x3E) over a caller-supplied ISO-TP transceiver.
There is intentionally no write/unlock/transfer method.

## What this does **not** do

By design, there is no support for SecurityAccess (0x27), programming sessions,
RequestDownload/Upload/TransferData (0x34–0x37), WriteDataByIdentifier/
WriteMemoryByAddress, ClearDTC, flash erase/write, or derate/inducement reset.
This is a diagnostics-and-telemetry tool, not a flasher/tuner.

## Develop

```bash
pip install -e ".[dev]"
pytest
```

## License

Apache-2.0. See [LICENSE](LICENSE).
