"""Tests for DBC decoding (skipped if cantools is not installed)."""

import textwrap

import pytest

cantools = pytest.importorskip("cantools")

from mcm_d5.dbc import DbcDecoder  # noqa: E402


_DBC = textwrap.dedent(
    """\
    VERSION ""
    BS_:
    BU_: ECU
    BO_ 256 Status: 2 ECU
     SG_ Speed : 0|16@1+ (1,0) [0|65535] "km/h" ECU
    """
)


def test_decode_known_message(tmp_path):
    path = tmp_path / "test.dbc"
    path.write_text(_DBC)
    decoder = DbcDecoder.from_file(str(path))
    decoded = decoder.decode(256, bytes([0x10, 0x00]))
    assert decoded["Speed"] == 16


def test_unknown_id_returns_empty(tmp_path):
    path = tmp_path / "test.dbc"
    path.write_text(_DBC)
    decoder = DbcDecoder.from_file(str(path))
    assert decoder.decode(999, bytes(2)) == {}
