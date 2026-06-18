"""Tests for J1939 Transport Protocol reassembly and multi-DTC DM1."""

from mcm_d5 import J1939Frame, J1939Monitor, ReplayLink
from mcm_d5.tp import TransportProtocolReassembler


def _bam_cm(source, total, num_packets, pgn):
    data = bytes(
        [
            0x20,
            total & 0xFF,
            (total >> 8) & 0xFF,
            num_packets,
            0xFF,
            pgn & 0xFF,
            (pgn >> 8) & 0xFF,
            (pgn >> 16) & 0xFF,
        ]
    )
    # TP.CM PGN 60416 (0xEC00), broadcast destination 0xFF
    return J1939Frame.from_can_id(0x1CECFF00 | source, data)


def _dt(source, seq, payload):
    data = bytes([seq]) + payload + b"\xff" * (7 - len(payload))
    return J1939Frame.from_can_id(0x1CEBFF00 | source, data)


def test_bam_reassembly_returns_full_payload():
    tp = TransportProtocolReassembler()
    # Two-packet BAM carrying 9 bytes for PGN 65226 (DM1).
    assert tp.observe(_bam_cm(0x00, total=9, num_packets=2, pgn=65226)) is None
    assert tp.observe(_dt(0x00, 1, bytes([0x00, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05]))) is None
    out = tp.observe(_dt(0x00, 2, bytes([0x06, 0x07])))
    assert out is not None
    assert out.pgn == 65226
    assert out.source == 0x00
    assert len(out.data) == 9
    assert out.data[:3] == bytes([0x00, 0x00, 0x01])


def test_monitor_decodes_multi_dtc_dm1_over_bam():
    # DM1 payload: lamps + two DTCs (8 bytes of DTC data -> needs 10 bytes total).
    lamp = bytes([0x40, 0x00])
    dtc1 = bytes([0x64, 0x00, 0x01, 0x05])  # SPN 100 FMI 1
    dtc2 = bytes([0x90, 0x00, 0x03, 0x02])  # SPN 144 FMI 3
    payload = lamp + dtc1 + dtc2  # 10 bytes -> 2 packets

    frames = [_bam_cm(0x00, total=10, num_packets=2, pgn=65226)]
    frames.append(_dt(0x00, 1, payload[0:7]))
    frames.append(_dt(0x00, 2, payload[7:10]))

    captured = []
    mon = J1939Monitor(ReplayLink(frames))
    mon.on_diagnostic(lambda diag, frame: captured.append(diag))
    mon.pump()

    assert len(captured) == 1
    spns = {d.spn for d in captured[0].dtcs}
    assert spns == {100, 144}
