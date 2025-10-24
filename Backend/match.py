def match():
    import random
    import struct
    with open("data/items", "rb") as file:
        size = file.seek(0, 2)
        offset = random.randrange(size >> 8) << 8
        file.seek(offset)
        value, = struct.unpack("<L", file.read(4))
        namelen = value & 0xff
        name = file.read(namelen).decode()
        url = file.read(251 - namelen).rstrip().decode()
    return {
        "gender": value >> 28 & 0xf,
        "usage": value >> 24 & 0xf,
        "category": value >> 16 & 0xff,
        "color": value >> 8 & 0xff,
        "name": name,
        "url": url
    }

