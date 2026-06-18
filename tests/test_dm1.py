"""Tests for DM1/DM2 diagnostic trouble code parsing."""

import pytest

from mcm_d5 import parse_diagnostic
from mcm_d5.errors import DecodeError


def test_single_active_dtc_with_mil_on():
    # Lamp byte 0x40 -> MIL on. DTC: SPN 100, FMI 1, OC 5.
    # SPN 100 = 0x64 (low byte), mid 0x00, high 0; b2 = (0<<5)|FMI = 0x01; b3 = OC.
    payload = bytes([0x40, 0x00, 0x64, 0x00, 0x01, 0x05])
    msg = parse_diagnostic(payload)
    assert msg.malfunction_indicator_lamp is True
    assert msg.red_stop_lamp is False
    assert len(msg.dtcs) == 1
    dtc = msg.dtcs[0]
    assert dtc.spn == 100
    assert dtc.fmi == 1
    assert dtc.occurrence_count == 5


def test_no_active_faults_padding_ignored():
    # Lamps off, single all-zero DTC slot -> treated as "no fault".
    payload = bytes([0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    msg = parse_diagnostic(payload)
    assert msg.dtcs == []
    assert msg.malfunction_indicator_lamp is False


def test_high_spn_bits():
    # b2=0xE3 -> high 3 bits = 0b111 -> SPN high = 7<<16 = 0x70000; FMI = 0xE3 & 0x1F = 3.
    payload = bytes([0x00, 0x00, 0x00, 0x00, 0xE3, 0x01])
    msg = parse_diagnostic(payload)
    assert msg.dtcs[0].spn == 0x70000
    assert msg.dtcs[0].fmi == 3


def test_too_short_raises():
    with pytest.raises(DecodeError):
        parse_diagnostic(b"\x00")
