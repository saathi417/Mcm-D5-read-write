"""Tests for capture-file readers."""

from mcm_d5.logreader import open_log, read_candump, read_savvycan_csv


def test_read_candump(tmp_path):
    p = tmp_path / "cap.log"
    p.write_text(
        "(1500000000.000000) can0 0CF00400#FFFF7DE02EFFFFFF\n"
        "(1500000000.001000) can0 18FECA00#4000640001050000\n"
        "garbage line without frame\n"
    )
    frames = list(read_candump(str(p)))
    assert len(frames) == 2
    assert frames[0].pgn == 61444
    assert frames[1].pgn == 65226


def test_read_savvycan_csv(tmp_path):
    p = tmp_path / "cap.csv"
    p.write_text(
        "Time Stamp,ID,Extended,Dir,Bus,LEN,D1,D2,D3,D4,D5,D6,D7,D8\n"
        "1000,0CF00400,true,Rx,0,8,FF,FF,7D,E0,2E,FF,FF,FF\n"
    )
    frames = list(read_savvycan_csv(str(p)))
    assert len(frames) == 1
    assert frames[0].pgn == 61444
    assert frames[0].data[3] == 0xE0


def test_open_log_dispatch(tmp_path):
    p = tmp_path / "cap.log"
    p.write_text("(0.0) can0 0CF00400#FFFF7DE02EFFFFFF\n")
    link = open_log(str(p))
    assert link.recv().pgn == 61444
