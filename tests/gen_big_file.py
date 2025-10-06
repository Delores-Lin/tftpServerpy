#!/usr/bin/env python3
"""Generate a big test file for TFTP loss / retransmission testing.

Features:
- Specify total size in MiB OR number of 512‑byte blocks.
- Each 512‑byte block begins with an ASCII header:  BEGIN:<block_number>:<hex(block_number)>\n
- The remainder of the block is filled with a deterministic repeating pattern so that
  corruption / mis‑ordering can be spotted with a hex viewer or diff tool.
- Final block is trimmed to exact requested size (not padded) unless --align512 given.

Examples:
  1 MiB (default) into tftp_root/big.bin:
      python tests/gen_big_file.py --out tftp_root/big.bin

  5 MiB file:
      python tests/gen_big_file.py --mib 5 --out tftp_root/big_5m.bin

  Exactly 2048 blocks (== 1 MiB) and force last block to length 512:
      python tests/gen_big_file.py --blocks 2048 --align512 --out tftp_root/big_exact.bin

  Custom pattern seed (changes filler bytes):
      python tests/gen_big_file.py --mib 2 --seed 123 --out tftp_root/big_seed123.bin

Integrity quick check in Python:
>>> import hashlib;print(hashlib.sha256(open('tftp_root/big.bin','rb').read()).hexdigest())

Author: generated helper script.
"""
from __future__ import annotations
import argparse, os, math, random, sys, hashlib

BLOCK_SIZE = 512
HEADER_TEMPLATE = b"BEGIN:{num:08d}:{hexnum:08X}\n"


def build_block(block_num: int, filler_cycle: bytes) -> bytes:
    header = HEADER_TEMPLATE.replace(b"{num:08d}", f"{block_num:08d}".encode())  # not used (leftover)
    # simpler: format directly
    header = f"BEGIN:{block_num:08d}:{block_num:08X}\n".encode()
    if len(header) >= BLOCK_SIZE:
        raise ValueError("Header too long for block")
    remain = BLOCK_SIZE - len(header)
    # repeat filler_cycle until fill
    reps = (remain // len(filler_cycle)) + 1
    body = (filler_cycle * reps)[:remain]
    return header + body


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Generate large patterned test file")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--mib", type=float, default=1.0, help="Total size in MiB (default 1.0)")
    g.add_argument("--blocks", type=int, help="Total 512-byte blocks (overrides --mib)")
    p.add_argument("--out", required=True, help="Output file path")
    p.add_argument("--seed", type=int, default=0xC0FFEE, help="PRNG seed for filler pattern")
    p.add_argument("--align512", action="store_true", help="Force final size to be multiple of 512 (pad by trimming)")
    p.add_argument("--hash", action="store_true", help="Print SHA256 after generation")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    random.seed(args.seed)
    if args.blocks is not None:
        total_blocks = args.blocks
        target_bytes = total_blocks * BLOCK_SIZE
    else:
        target_bytes = int(args.mib * 1024 * 1024)
        total_blocks = math.ceil(target_bytes / BLOCK_SIZE)
    # base filler pattern (64 bytes) derived from seed
    base = bytes((random.randint(0,255) for _ in range(64)))
    filler_cycle = base + hashlib.sha1(base).digest()  # 64 + 20 = 84 bytes cycle

    written = 0
    with open(args.out, 'wb') as f:
        for b in range(1, total_blocks + 1):
            block_bytes = build_block(b, filler_cycle)
            if not args.align512 and written + BLOCK_SIZE > target_bytes:
                # trim last block to exact target size
                need = target_bytes - written
                f.write(block_bytes[:need])
                written += need
                break
            f.write(block_bytes)
            written += BLOCK_SIZE
            if b % 500 == 0:
                print(f".. wrote {b} blocks ({written/1024:.1f} KiB)")
    print(f"Done: {args.out} size={written} bytes blocks={total_blocks}")
    if args.hash:
        h = hashlib.sha256(open(args.out,'rb').read()).hexdigest()
        print("SHA256:", h)

if __name__ == "__main__":
    sys.exit(main())
