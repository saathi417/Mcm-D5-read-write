"""Tests for DM5 readiness parsing and extra DTC message PGNs."""

from mcm_d5 import J1939Frame, J1939Monitor, ReplayLink
from mcm_d5.dm1 import DTC_DIAGNOSTIC_PGNS, parse_readiness


def test_parse_readiness():
    r = parse_readiness(bytes([2, 1, 0x05, 0x00, 0x00]))
    assert r.active_trouble_codes == 2
    assert r.previously_active_trouble_codes == 1
    assert r.obd_compliance == 0x05


def test_extra_dtc_pgns_recognized():
    # DM27 (64898) and DM28 (64896) use the lamp + DTC layout.
    assert 64898 in DTC_DIAGNOSTIC_PGNS
    assert 64896 in DTC_DIAGNOSTIC_PGNS


def test_monitor_dispatches_dm5_readiness():
    # DM5 PGN 65230 (0xFECE), PDU2 broadcast.
    frame = J1939Frame.from_can_id(0x18FECE00, bytes([1, 0, 0x05, 0, 0]))
    captured = []
    mon = J1939Monitor(ReplayLink([frame]))
    mon.on_readiness(lambda r, f: captured.append(r))
    mon.pump()
    assert captured[0].active_trouble_codes == 1


def test_monitor_dispatches_dm28_permanent_dtc():
    # DM28 PGN 64896 (0xFD80), one permanent DTC.
    frame = J1939Frame.from_can_id(0x18FD8000, bytes([0x40, 0x00, 0x64, 0x00, 0x01, 0x03]))
    captured = []
    mon = J1939Monitor(ReplayLink([frame]))
    mon.on_diagnostic(lambda diag, f: captured.append(diag))
    mon.pump()
    assert captured[0].dtcs[0].spn == 100
