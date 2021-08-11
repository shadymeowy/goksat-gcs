from enum import Enum


class FrameType(Enum):
    TRANSMIT = 0x10
    RECEIVE = 0x90
    STATUS = 0x8B
    INVALID = 0x0
    UNKNOWN = 0x1


def read_packet(it):
    count = 0
    buffer = []
    while it() != 0x7e:
        pass
    length = it() << 8 | it()
    frame_type = it()
    count = ((count+frame_type) & 0xff)
    for _ in range(length-1):
        byt = it()
        buffer.append(byt)
        count = ((count+byt) & 0xff)
    check = it()
    if check != 0xff - count:
        return (FrameType.INVALID,)
    elif frame_type == FrameType.TRANSMIT.value:
        return (
            FrameType.TRANSMIT,
            buffer[0],  # Id
            hex(int.from_bytes(buffer[1:9], 'big')),  # 64 bit address
            hex(int.from_bytes(buffer[9:11], 'big')),  # 16 bit address
            bytes(buffer[13:])  # Data
        )
    elif frame_type == FrameType.RECEIVE.value:
        return (
            FrameType.RECEIVE,
            hex(int.from_bytes(buffer[0:8], 'big')),  # 64 bit address
            hex(int.from_bytes(buffer[8:10], 'big')),  # 16 bit address
            buffer[10],  # Receive option
            bytes(buffer[11:])  # Data
        )
    elif frame_type == FrameType.STATUS.value:
        return (
            FrameType.STATUS,
            buffer[0],
            buffer[4]
        )
    else:
        return (FrameType.UNKNOWN, frame_type)


def create_transmit_packet(data, id=0, addr64=0xFFFFFFFFFFFFFFFF, addr16=0xFFFE, ack=True):
    l = len(data)
    r = [
        0x7e,
        *(14 + len(data)).to_bytes(2, 'big'),
        0x10,
        id,
        *addr64.to_bytes(8, 'big'),
        *addr16.to_bytes(2, 'big'),
        0,
        ack & 1,
        *data,
        0
    ]
    count = 0
    for i in range(3, 17 + l):
        count += r[i]
    r[17 + len(data)] = 0xff - count & 0xff
    return bytes(r)
