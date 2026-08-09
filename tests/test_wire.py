import pytest

from total_awareness.wire import HEADER, MAGIC, VERSION, pack, unpack


def test_wire_round_trip():
    packet = pack(7, b"sensor bytes")
    assert unpack(packet) == (7, b"sensor bytes")


def test_wire_header_is_six_bytes():
    packet = pack(3, b"abc")
    assert HEADER.size == 6
    assert packet[:6] == HEADER.pack(MAGIC, VERSION, 3, 3)


def test_wire_rejects_bad_length():
    with pytest.raises(ValueError):
        unpack(HEADER.pack(MAGIC, VERSION, 1, 99) + b"short")
