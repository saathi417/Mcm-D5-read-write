"""Tests for the passive J1939 monitor using a ReplayLink."""

from mcm_d5 import J1939Frame, J1939Monitor, ReplayLink


def _eec1(rpm):
    raw = int(rpm / 0.125)
    data = bytes([0xFF, 0xFF, 0x7D, raw & 0xFF, (raw >> 8) & 0xFF, 0xFF, 0xFF, 0xFF])
    return J1939Frame.from_can_id(0x0CF00400, data)


def _dm1_one_fault():
    return J1939Frame.from_can_id(0x18FECA00, bytes([0x40, 0x00, 0x64, 0x00, 0x01, 0x02]))


def test_pump_decodes_signals_and_tracks_latest():
    link = ReplayLink([_eec1(800), _eec1(1500)])
    mon = J1939Monitor(link)
    seen = []
    mon.on_signal(lambda name, value, frame: seen.append((name, value)))

    processed = mon.pump()

    assert processed == 2
    assert mon.latest["Engine Speed"] == 1500.0
    assert ("Engine Speed", 800.0) in seen


def test_pump_dispatches_diagnostics():
    link = ReplayLink([_dm1_one_fault()])
    mon = J1939Monitor(link)
    captured = []
    mon.on_diagnostic(lambda diag, frame: captured.append(diag))

    mon.pump()

    assert len(captured) == 1
    assert captured[0].malfunction_indicator_lamp is True
    assert captured[0].dtcs[0].spn == 100


def test_pump_stops_at_max_frames():
    link = ReplayLink([_eec1(800), _eec1(900), _eec1(1000)])
    mon = J1939Monitor(link)
    assert mon.pump(max_frames=2) == 2
