# Mcm-D5-read-write

A small Python client for **reading from and writing to the MCM D5 API
service**.

> **Status:** skeleton. The public `read()` / `write()` interface and project
> structure are in place and tested, but the wire contract (paths, auth,
> request/response shape) is a placeholder pending the real service spec.

## Install

```bash
pip install -e ".[dev]"
```

## Usage

```python
from mcm_d5 import McmD5Client

client = McmD5Client(base_url="https://example.com/api")

client.write("temperature", 21)
value = client.read("temperature")
```

The HTTP layer is pluggable via the `Transport` protocol, so the client can be
tested without a live service (see `tests/test_client.py`).

## Develop

```bash
pip install -e ".[dev]"
pytest
```

## License

Apache-2.0. See [LICENSE](LICENSE).
