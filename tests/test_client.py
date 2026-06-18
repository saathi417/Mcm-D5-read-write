"""Tests for McmD5Client using a fake transport (no network)."""

import json

import pytest

from mcm_d5 import McmD5Client, NotFoundError, Response, TransportError


class FakeTransport:
    """In-memory transport recording calls, for testing the client."""

    def __init__(self, get_response=None):
        self.get_response = get_response
        self.put_calls = []

    def get(self, path):
        if self.get_response is None:
            return Response(status=404, body=b"")
        return self.get_response

    def put(self, path, body):
        self.put_calls.append((path, body))
        return Response(status=200, body=b"")


def test_read_returns_value():
    transport = FakeTransport(
        get_response=Response(status=200, body=json.dumps({"value": 42}).encode())
    )
    client = McmD5Client(transport=transport)
    assert client.read("temp") == 42


def test_read_missing_key_raises_not_found():
    client = McmD5Client(transport=FakeTransport(get_response=Response(404, b"")))
    with pytest.raises(NotFoundError):
        client.read("missing")


def test_read_error_status_raises_transport_error():
    client = McmD5Client(transport=FakeTransport(get_response=Response(500, b"")))
    with pytest.raises(TransportError):
        client.read("boom")


def test_write_sends_value_envelope():
    transport = FakeTransport()
    client = McmD5Client(transport=transport)
    client.write("temp", 21)

    assert len(transport.put_calls) == 1
    path, body = transport.put_calls[0]
    assert path == "d5/temp"
    assert json.loads(body) == {"value": 21}


def test_empty_key_rejected():
    client = McmD5Client(transport=FakeTransport())
    with pytest.raises(ValueError):
        client.read("")


def test_requires_base_url_or_transport():
    with pytest.raises(ValueError):
        McmD5Client()
