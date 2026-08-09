from __future__ import annotations

import struct

MAGIC = 0x5441
VERSION = 1
HEADER = struct.Struct("<HBBH")  # magic, version, message type, payload length


def pack(message_type: int, payload: bytes) -> bytes:
    if not 0 <= message_type <= 0xFF:
        raise ValueError("message type must fit in one byte")
    if len(payload) > 0xFFFF:
        raise ValueError("payload is too large")
    return HEADER.pack(MAGIC, VERSION, message_type, len(payload)) + payload


def unpack(packet: bytes) -> tuple[int, bytes]:
    if len(packet) < HEADER.size:
        raise ValueError("packet is shorter than header")
    magic, version, message_type, length = HEADER.unpack_from(packet)
    payload = packet[HEADER.size:]
    if magic != MAGIC or version != VERSION:
        raise ValueError("invalid wire header")
    if len(payload) != length:
        raise ValueError("invalid payload length")
    return message_type, payload
