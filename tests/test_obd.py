"""Tests for the read-only OBD-II / J1979 helpers."""

import pytest

from mcm_d5.obd import (
    ObdReadClient,
    build_pid_request,
    build_read_stored_dtcs,
    decode_dtc,
    parse_pid_response,
    parse_stored_dtcs,
)


def test_build_requests():
    assert build_pid_request(0x0C) == bytes([0x01, 0x0C])
    assert build_read_stored_dtcs() == bytes([0x03])


def test_parse_rpm():
    # 0x41 0x0C, raw (0x1A, 0xF8) -> (0x1AF8)/4 = 1726.0 rpm.
    pv = parse_pid_response(bytes([0x41, 0x0C, 0x1A, 0xF8]))
    assert pv.name == "Engine RPM"
    assert pv.value == 1726.0
    assert pv.unit == "rpm"


def test_parse_coolant_temp():
    pv = parse_pid_response(bytes([0x41, 0x05, 130]))  # 130 - 40 = 90
    assert pv.value == 90.0


def test_decode_dtc():
    assert decode_dtc(0x03, 0x01) == "P0301"
    assert decode_dtc(0x43, 0x20) == "C0320"


def test_parse_stored_dtcs():
    resp = bytes([0x43, 0x03, 0x01, 0x00, 0x00, 0xC1, 0x33])
    assert parse_stored_dtcs(resp) == ["P0301", "U0133"]


def test_unsupported_pid_raises():
    with pytest.raises(Exception):
        parse_pid_response(bytes([0x41, 0xAB, 0x00]))


class FakeTransceiver:
    def __init__(self, response):
        self.response = response
        self.sent = []

    def request(self, payload, timeout=2.0):
        self.sent.append(payload)
        return self.response


def test_client_read_pid():
    tx = FakeTransceiver(bytes([0x41, 0x0D, 100]))
    assert ObdReadClient(tx).read_pid(0x0D).value == 100.0


def test_client_exposes_only_read_methods():
    methods = {m for m in dir(ObdReadClient) if not m.startswith("_")}
    assert methods == {"read_pid", "read_stored_dtcs"}
