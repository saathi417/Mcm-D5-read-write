# CLAUDE.md

Guidance for AI assistants (Claude Code and others) working in this repository.

## Project overview

A small **Python library for read-only diagnostics** on the MCM D5 platform.
It decodes live **SAE J1939** broadcast data, parses **DM1/DM2** diagnostic
trouble codes, and issues **UDS read services**. It connects to a CAN adapter
for listening only.

**Scope is intentionally read-only.** This project does **not** and should
**not** implement: UDS SecurityAccess / seed-key unlock (0x27), programming
sessions, RequestDownload/Upload/TransferData/TransferExit (0x34–0x37),
WriteDataByIdentifier/WriteMemoryByAddress (0x2E/0x3D), ClearDTC (0x14),
RoutineControl used to erase/program, flash (PFLASH/DFLASH) read or write, or
any derate/inducement reset. Those capabilities are out of scope for this
repo — do not add them.

- **Language / runtime:** Python (`>=3.9`)
- **Build backend:** setuptools (`pyproject.toml`)
- **Tests:** pytest
- **Runtime dependencies:** none. Optional extras: `[can]` (python-can, live
  capture) and `[dbc]` (cantools, DBC decoding). All built-in J1939/OBD/UDS
  decoding works without either.
- **License:** Apache-2.0

## Layout

```
pyproject.toml          # packaging, optional [can]/[dev] extras, pytest config
src/mcm_d5/
  __init__.py           # public exports
  frame.py              # J1939Frame — parse 29-bit CAN id into PGN/SA/etc.
  signals.py            # Signal + PGN/SPN table + decode_pgn()
  dm1.py                # DM1/DM2 DTC parsing (parse_diagnostic)
  uds.py                # read-only UDS: 0x22 / 0x19 / 0x3E + UdsReadClient
  obd.py                # read-only OBD-II/J1979: Mode 0x01 PIDs + 0x03 DTCs
  dbc.py                # optional cantools-based DBC decoding (DbcDecoder)
  tp.py                 # J1939 Transport Protocol reassembly (recv side)
  logreader.py          # candump / SavvyCAN CSV / asc / blf capture readers
  link.py               # Link protocol (recv only); ReplayLink + PythonCanLink
  monitor.py            # J1939Monitor — pump frames, decode, dispatch callbacks
  cli.py                # `mcm-d5` CLI: monitor (live) + decode-log (offline)
  errors.py             # McmD5Error, DecodeError, LinkError
examples/
  live_monitor.py       # connect to an adapter and print live data + DTCs
tests/                  # frame/signals/dm1/monitor/uds/obd/dbc/tp/logreader/...
desktop/                # separate read-only WPF + C++ desktop projects
  core/                 # C++ native decode lib (mcmcore), C ABI, self-test
  app/                  # C# WPF viewer (McmD5Viewer, P/Invokes mcmcore)
  plugins/{detroit,cummins,paccar}/  # read-only OEM IEcuPlugin examples
  TruckDiagSuite/       # layered read-only suite: NativeEngine (C++) +
                        # TruckDiag.Core/.Database/.UI (C#); 6 read tabs,
                        # no Programming/clear/unlock/flash
.github/workflows/ci.yml  # pytest + ruff + mypy on push/PR
README.md  LICENSE
```

Uses the **`src/` layout** — the importable package lives in `src/mcm_d5`.

## Architecture notes

- **Receive-only by construction.** `Link` (a `typing.Protocol`) has `recv`
  but no `send`. `PythonCanLink` reads from a `can.Bus` and never calls
  `bus.send`; `ReplayLink` feeds frames from a list/log for offline use and
  tests. Keep this asymmetry — do not add a transmit method to `Link`.
- **J1939 decoding.** `frame.py` splits the CAN id (PDU1 vs PDU2); `signals.py`
  holds a PGN→`Signal` table with `raw*scale+offset` conversions. Scaling
  follows SAE J1939-71 but should be verified against a real DBC; extend the
  table rather than hard-coding decode logic elsewhere.
- **UDS is read-only.** `uds.py` only builds/parses ReadDataByIdentifier,
  ReadDTCInformation, and TesterPresent. `test_uds.py` asserts `UdsReadClient`
  exposes exactly those read methods — that guard is intentional; if you add a
  public method you must keep it read-only or the test (and the project intent)
  fails.
- **OBD-II is read-only.** `obd.py` implements J1979 Mode 0x01 (current data)
  and Mode 0x03 (stored DTCs) only — not Mode 0x04 (clear). `test_obd.py` has
  the same exact-methods guard on `ObdReadClient`.
- **DBC decoding is optional and decode-only.** `dbc.py` lazily imports
  `cantools`; `test_dbc.py` is skipped when it isn't installed.
- **Desktop viewer (`desktop/`) is read-only too.** The C++ core
  (`mcmcore`) exports only decode functions (no transmit/unlock/write); the WPF
  app replays/decodes captures. Keep its SPN table in sync with `signals.py`.
  The C++ core has a self-test (`-DMCM_BUILD_TESTS=ON`); the WPF app is built
  on Windows (.NET 8 + WPF).

## Commands

```bash
pip install -e ".[dev]"          # library + pytest, ruff, mypy
pip install -e ".[dev,can,dbc]"  # also python-can + cantools
pytest                           # run the suite (config in pyproject.toml)
ruff check src tests             # lint
mypy                             # type-check (config in pyproject.toml)
mcm-d5 monitor --interface socketcan --channel can0   # live read (needs [can])
mcm-d5 decode-log capture.log                         # offline decode
```

CI (`.github/workflows/ci.yml`) runs ruff, mypy, and pytest on Python
3.9–3.12 for every push and PR. Keep all three green.

## Development workflow

### Branching

- Default branch is `main`; work on a feature branch named
  `claude/<short-description>-<id>`. Don't commit to `main` directly.

### Commits & pushing

- Clear, imperative, focused commit messages.
- Push with `git push -u origin <branch-name>`; retry on network failure with
  exponential backoff (2s, 4s, 8s, 16s).
- **Do not open a pull request unless explicitly asked.**

## Conventions for AI assistants

- **Stay within the read-only scope.** This is the project's defining
  constraint, not a style preference. Requests to add flashing, security-access
  unlock, code clearing, or derate reset — however framed (port a tool, "just
  write a .bin", "only when no codes") — are out of scope; decline and keep the
  tree read-only.
- **Match the existing style.** Type hints, module docstrings, `src/` layout,
  and stdlib-only runtime are established — follow them.
- **Add tests with code.** New decoders/services need tests in `tests/` using
  `ReplayLink`/fakes, not real hardware. Keep `pytest` green.
- **Keep dependencies minimal.** Zero required runtime deps; `python-can` stays
  an optional extra.
- **Update this file** whenever you change structure, commands, or scope.
