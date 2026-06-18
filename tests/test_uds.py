"""Tests for the read-only UDS helpers."""

import pytest

from mcm_d5 import (
    UdsReadClient,
    build_read_data_by_identifier,
    build_read_dtc_by_status_mask,
    build_tester_present,
)
from mcm_d5.uds import NegativeResponse, parse_read_data_by_identifier


def test_build_read_data_by_identifier():
    assert build_read_data_by_identifier(0xF190) == bytes([0x22, 0xF1, 0x90])


def test_build_read_dtc_and_tester_present():
    assert build_read_dtc_by_status_mask(0xFF) == bytes([0x19, 0x02, 0xFF])
    assert build_tester_present() == bytes([0x3E, 0x00])


def test_parse_read_data_by_identifier_positive():
    resp = bytes([0x62, 0xF1, 0x90]) + b"VIN1234567890"
    parsed = parse_read_data_by_identifier(resp)
    assert parsed.did == 0xF190
    assert parsed.data == b"VIN1234567890"


def test_negative_response_raises():
    with pytest.raises(NegativeResponse):
        parse_read_data_by_identifier(bytes([0x7F, 0x22, 0x31]))


class FakeTransceiver:
    """Records requests and returns a canned response."""

    def __init__(self, response):
        self.response = response
        self.sent = []

    def request(self, payload, timeout=2.0):
        self.sent.append(payload)
        return self.response


def test_client_read_data_by_identifier():
    tx = FakeTransceiver(bytes([0x62, 0xF1, 0x90, 0x01, 0x02]))
    client = UdsReadClient(tx)
    result = client.read_data_by_identifier(0xF190)
    assert tx.sent == [bytes([0x22, 0xF1, 0x90])]
    assert result.data == bytes([0x01, 0x02])


def test_client_read_dtcs_parses_records():
    # status availability 0xFF, one DTC 0x010203 status 0x09.
    tx = FakeTransceiver(bytes([0x59, 0x02, 0xFF, 0x01, 0x02, 0x03, 0x09]))
    client = UdsReadClient(tx)
    report = client.read_dtcs()
    assert report.dtcs[0].dtc == 0x010203
    assert report.dtcs[0].status == 0x09


def test_client_exposes_only_read_methods():
    # Guard against accidentally adding write/unlock methods.
    methods = {m for m in dir(UdsReadClient) if not m.startswith("_")}
    assert methods == {"read_data_by_identifier", "read_dtcs", "tester_present"}
