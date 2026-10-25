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
    """Block for decompress(), greedy: at each byte the one-byte command covering the most output (zero run 0,
    byte/word/dword repeat 1-3, copy from one or two strides back 8/9, counting-up words C), else a literal (4/5).
    shortcut: no stream replays (E/F) or delta bytes (6/7), so output is a little larger than the game's."""
    out = bytearray(len(data).to_bytes(2, "little") + stride.to_bytes(2, "little"))
    lit = bytearray()
    size = len(data)

    def flush():
        while lit:
            chunk = lit[:32]
            del lit[:32]
            out.append(0x50 | len(chunk) - 17 if len(chunk) > 16 else 0x40 | len(chunk) - 1)
            out.extend(chunk)

    def match(i, back, unit, cap):
        """Bytes from i equal to the bytes `back` earlier, rounded down to whole units, at most cap units."""
        n = 0
        while n < cap * unit and i + n < size and data[i + n] == data[i + n - back]:
            n += 1
        return n - n % unit

    def best(i):
        cands = []
        z = 0
        while z < 16 and i + z < size and data[i + z] == 0:
            z += 1
        cands.append((z, z - 1))
        if i >= 1:
            n = match(i, 1, 1, 16)
            cands.append((n, 0x10 | n - 1))
        if i >= 2:
            n = match(i, 2, 2, 16)
            cands.append((n, 0x20 | n // 2 - 1))
            w, n = data[i - 2] | data[i - 1] << 8, 0
            while n < 16 and i + 2 * n + 1 < size:
                w = w + 1 & 0xFFFF
                if data[i + 2 * n] | data[i + 2 * n + 1] << 8 != w:
                    break
                n += 1
            cands.append((2 * n, 0xC0 | n - 1))
        if i >= 4:
            n = match(i, 4, 4, 16)
            cands.append((n, 0x30 | n // 4 - 1))
        for k, op in ((1, 0x80), (2, 0x90)):
            if stride and i >= k * stride:
                n = match(i, k * stride, 1, 16)
                cands.append((n, op | n - 1))
        return max(cands, key=lambda c: c[0])

    i = 0
    while i < size:
        n, cmd = best(i)
        if n >= 2:
            flush()
            out.append(cmd)
            i += n
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
