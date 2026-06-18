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
- **Runtime dependencies:** none. `python-can` is an optional extra (`[can]`)
  used only for live capture; all decoding works without it.
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
  link.py               # Link protocol (recv only); ReplayLink + PythonCanLink
  monitor.py            # J1939Monitor — pump frames, decode, dispatch callbacks
  errors.py             # McmD5Error, DecodeError, LinkError
examples/
  live_monitor.py       # connect to an adapter and print live data + DTCs
tests/
  test_frame.py test_signals.py test_dm1.py test_monitor.py test_uds.py
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

## Commands

```bash
pip install -e ".[dev]"       # library + pytest
pip install -e ".[dev,can]"   # also python-can for live capture
pytest                        # run the suite (config in pyproject.toml)
python examples/live_monitor.py --interface socketcan --channel can0
```

No linter/formatter or CI is configured yet. If you add one, document it here.

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
