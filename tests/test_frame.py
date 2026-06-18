"""Tests for J1939 CAN identifier parsing."""

from mcm_d5 import J1939Frame


def test_pdu2_broadcast_eec1():
    # EEC1, PGN 61444 (0xF004), priority 3, source 0x00 -> CAN id 0x0CF00400
    frame = J1939Frame.from_can_id(0x0CF00400, bytes(8))
    assert frame.pgn == 61444
    assert frame.priority == 3
    assert frame.source == 0x00
    assert frame.destination is None  # PDU2 is broadcast


def test_pdu1_destination_specific_request():
    # Request PGN 59904 (0xEA00), prio 6, dest 0x00, source 0xF9 -> 0x18EA00F9
    frame = J1939Frame.from_can_id(0x18EA00F9, b"\x00\xee\x00")
    assert frame.pgn == 59904
    assert frame.source == 0xF9
    assert frame.destination == 0x00


def test_masks_to_29_bits():
    frame = J1939Frame.from_can_id(0xFFFFFFFF, b"")
    assert frame.can_id == 0x1FFFFFFF
