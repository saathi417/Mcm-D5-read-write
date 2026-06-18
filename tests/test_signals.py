"""Tests for SPN signal decoding."""

from mcm_d5 import decode_pgn
from mcm_d5.signals import Signal


def test_eec1_engine_speed_and_torque():
    # SPN 190 engine speed at bytes 4-5: 1500 rpm -> raw 12000 (0x2EE0) LE.
    # SPN 513 percent torque at byte 3: 0% -> raw 125 (0x7D).
    data = bytes([0xFF, 0xFF, 0x7D, 0xE0, 0x2E, 0xFF, 0xFF, 0xFF])
    decoded = decode_pgn(61444, data)
    assert decoded["Engine Speed"] == 1500.0
    assert decoded["Actual Engine - Percent Torque"] == 0.0


def test_coolant_temperature():
    # SPN 110 at byte 1: 90 degC -> raw 130 (0x82).
    data = bytes([0x82, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    decoded = decode_pgn(65262, data)
    assert decoded["Engine Coolant Temperature"] == 90.0


def test_def_tank_volume():
    # SPN 1761 at byte 1: 50% -> raw 125 (0.4%/bit).
    data = bytes([125, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    decoded = decode_pgn(65110, data)
    assert decoded["Aftertreatment 1 DEF Tank Volume"] == 50.0


def test_not_available_is_omitted():
    # All 0xFF -> every signal reads "not available" and is dropped.
    assert decode_pgn(61444, bytes([0xFF] * 8)) == {}


def test_unknown_pgn_returns_empty():
    assert decode_pgn(0x1234, bytes(8)) == {}


def test_signal_decode_short_data_returns_none():
    sig = Signal(190, "Engine Speed", 3, 2, 0.125, 0.0, "rpm")
    assert sig.decode(b"\x00\x00") is None
