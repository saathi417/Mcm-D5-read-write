# CLAUDE.md

Guidance for AI assistants (Claude Code and others) working in this repository.

## Project overview

A small **Python client** for **reading from and writing to the MCM D5 API
service**. The public surface is two operations — `read(key)` and
`write(key, value)` — exposed by `McmD5Client`.

**Current status: skeleton.** The package layout, the `read`/`write` interface,
a pluggable transport, and tests are in place and passing. The actual wire
contract (service paths, auth, request/response shape) is a **placeholder** and
should be finalized once the real MCM D5 service spec is known. Inspect the code
before relying on details; this file may lag behind the repo.

- **Language / runtime:** Python (`>=3.9`)
- **Build backend:** setuptools (`pyproject.toml`)
- **Tests:** pytest
- **Runtime dependencies:** none (transport uses the stdlib `urllib`)
- **License:** Apache-2.0

## Layout

```
pyproject.toml          # packaging, deps, pytest config
src/mcm_d5/
  __init__.py           # public exports (McmD5Client, errors, transport types)
  client.py             # McmD5Client: read()/write() — the main interface
  transport.py          # Transport protocol + HttpTransport + Response
  errors.py             # McmD5Error, TransportError, NotFoundError
tests/
  test_client.py        # client tests using an in-memory FakeTransport
README.md
LICENSE
```

Uses the **`src/` layout** — the importable package lives in `src/mcm_d5`, not
at the repo root.

## Architecture notes

- **Transport is pluggable.** `McmD5Client` talks to the service through a
  `Transport` (a `typing.Protocol` with `get`/`put`). `HttpTransport` is the
  default `urllib`-based implementation; tests inject a fake. When wiring real
  behavior, prefer extending/replacing the transport over hard-coding HTTP in
  the client.
- **Placeholder wire format.** `client.py` maps a key to the path `d5/<key>`
  and uses a JSON `{"value": ...}` envelope. These are guesses — update
  `_path`, `read`, and `write` together when the spec lands, and adjust the
  tests to match.
- **Errors:** raise `NotFoundError` for missing keys (HTTP 404),
  `TransportError` for transport/other failures. Both derive from `McmD5Error`.

## Commands

```bash
pip install -e ".[dev]"   # install package + dev deps (pytest)
pytest                    # run the test suite (config in pyproject.toml)
```

There is no linter/formatter or CI configured yet. If you add one, document the
command here.

## Development workflow

### Branching

- Default branch is `main`; do all work on a feature branch (don't commit to
  `main` directly).
- Branch names use the form `claude/<short-description>-<id>`.

### Commits & pushing

- Clear, imperative, focused commit messages (e.g. "Add MCM D5 read/write
  client skeleton").
- Push with `git push -u origin <branch-name>`; retry on network failure with
  exponential backoff (2s, 4s, 8s, 16s).
- **Do not open a pull request unless explicitly asked.**

## Conventions for AI assistants

- **Match the existing style.** Type hints, module-level docstrings, and the
  `src/` layout are already established — follow them.
- **Add tests with code.** New behavior in `client.py`/`transport.py` should
  come with a test in `tests/`, using `FakeTransport` rather than real network
  calls. Keep `pytest` green.
- **Keep dependencies minimal.** The package currently has zero runtime deps.
  Don't add one (e.g. `requests`/`httpx`) without a reason; if you do, record
  it in `pyproject.toml` and here.
- **Don't fabricate the service contract.** Where paths/payloads are
  placeholders, treat them as such — confirm against the real spec before
  presenting them as settled.
- **Update this file** whenever you change structure, commands, or conventions
  so future sessions stay accurate.
