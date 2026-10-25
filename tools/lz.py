"""Decompressor for the game's graphics/tilemap codec ($82:D92C; docs/re/compression.md).

    python -X utf8 tools/lz.py OFFSET [--init N] [--out FILE]      # decompress one block (file offset, hex)
    python -X utf8 tools/lz.py --selftest

Block: u16 output size, u16 stride, then commands. Command byte: high nibble = op, n = low nibble + 1.
  0 n zero bytes            1 repeat last byte n times     2 repeat last word n times   3 repeat last dword n times
  4 n literal bytes         5 n+16 literal bytes           6 one byte: last += n-17     7 one byte: last += n-1
  8 copy n bytes from out-stride                           9 copy n bytes from out-2*stride
  A n words: word at out-stride, +0x10                     B same, -0x10
  C n words: previous word +1 each                         D previous word -1 each
  E read u16 off: the next n+3 stream bytes come from block_start+off
  F read u8 b, u16 off: the next ((n-1)<<8 | b) + 4 stream bytes come from block_start+off
"last" (for 6/7) starts as the caller's $43 byte (the asset directory's type byte) and is updated by 4-7 only.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Battle Zeque Den (Japan).sfc"


def decompress(data, off, init=0):
    """Return (output bytes, end) where end is one past the last byte read from the main stream."""
    size = data[off] | data[off + 1] << 8
    stride = data[off + 2] | data[off + 3] << 8
    pos, redirect, rcount = off + 4, 0, 0
    out, last = bytearray(), init

    def byte():
        nonlocal pos, redirect, rcount
        if rcount:
            rcount -= 1
            redirect += 1
            return data[redirect - 1]
        pos += 1
        return data[pos - 1]

    def word_at(i):
        return out[i] | out[i + 1] << 8

    def put_word(w):
        out.extend((w & 0xFF, w >> 8 & 0xFF))

    spins = 0  # E/F ops in a row with no output: a self-referencing redirect loops forever (only in garbage)
    while len(out) < size:
        c = byte()
        spins = spins + 1 if c >> 4 >= 14 else 0
        if spins > 64:
            raise ValueError(f"block {off:#x}: redirect loop")
        op, n = c >> 4, (c & 15) + 1
        if op == 0:
            out.extend(bytes(n))
        elif op == 1:
            for _ in range(n):
                out.append(out[-1])
        elif op == 2:
            for _ in range(n):
                put_word(word_at(len(out) - 2))
        elif op == 3:
            d = out[-4:]
            for _ in range(n):
                out.extend(d)
        elif op in (4, 5):
            for _ in range(n + (16 if op == 5 else 0)):
                last = byte()
                out.append(last)
        elif op in (6, 7):
            last = (last + n - (17 if op == 6 else 1)) & 0xFF
            out.append(last)
        elif op in (8, 9):
            src = len(out) - stride * (op - 7)
            if n & 1:
                out.append(out[src])
                src += 1
            for _ in range(n >> 1):
                w = word_at(src)
                src += 2
                put_word(w)
        elif op in (10, 11):
            for _ in range(n):
                put_word(word_at(len(out) - stride) + (0x10 if op == 10 else -0x10) & 0xFFFF)
        elif op in (12, 13):
            w = word_at(len(out) - 2)
            for _ in range(n):
                w = w + (1 if op == 12 else -1) & 0xFFFF
                put_word(w)
        elif op == 14:
            lo, hi = byte(), byte()
            redirect, rcount = off + (lo | hi << 8), n + 3
        else:
            b = byte()
            lo, hi = byte(), byte()
            redirect, rcount = off + (lo | hi << 8), ((n - 1) << 8 | b) + 4
    if len(out) != size:
        raise ValueError(f"block {off:#x}: wrote {len(out)} bytes, header says {size}")
    return bytes(out), pos


def compress(data, stride):
    """Block for decompress(): zero runs (op 0), byte repeats (op 1) and literals (ops 4/5).
    shortcut: no stride copies (8-B) or stream replays (E/F), so output is larger than the game's; add op 8/9
    matching if an edited block no longer fits its slot."""
    out = bytearray(len(data).to_bytes(2, "little") + stride.to_bytes(2, "little"))
    lit = bytearray()

    def flush():
        while lit:
            chunk = lit[:32]
            del lit[:32]
            out.append(0x50 | len(chunk) - 17 if len(chunk) > 16 else 0x40 | len(chunk) - 1)
            out.extend(chunk)

    def run(i, b):
        n = 0
        while n < 16 and i + n < len(data) and data[i + n] == b:
            n += 1
        return n

    i = 0
    while i < len(data):
        z = run(i, 0)
        r = run(i, data[i - 1]) if i else 0
        if max(z, r) >= 2:
            flush()
            out.append(z - 1 if z >= r else 0x10 | r - 1)
            i += max(z, r)
        else:
            lit.append(data[i])
            i += 1
    flush()
    return bytes(out)


def selftest():
    # 4: 2 literals; 1: repeat x2; 7: last+3; 0: 2 zeros; E: replay stream bytes 4..7 (41 AA BB 11); 1: repeat x1
    blk = bytes([12, 0, 2, 0, 0x41, 0xAA, 0xBB, 0x11, 0x73, 0x01, 0xE0, 4, 0, 0x10])
    out, end = decompress(blk, 0)
    assert out == bytes([0xAA, 0xBB, 0xBB, 0xBB, 0xBE, 0, 0, 0xAA, 0xBB, 0xBB, 0xBB, 0xBB]), out.hex()
    assert end == len(blk), end
    for raw in (b"", b"\x00" * 40, b"\x07" * 40 + bytes(range(70)) + b"\x00\x01\x01"):
        blk = compress(raw, 8)
        assert decompress(blk, 0) == (raw, len(blk)), raw.hex()
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("offset", nargs="?")
    ap.add_argument("--init", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    out, end = decompress(ROM.read_bytes(), int(a.offset, 16), a.init)
    print(f"{len(out)} bytes out, stream ends at {end:#x}")
    if a.out:
        Path(a.out).write_bytes(out)


if __name__ == "__main__":
    sys.exit(main())
