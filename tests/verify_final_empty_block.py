#!/usr/bin/env python3
"""TFTP 终止空块 (final empty DATA) 校验脚本

用途:
  1. 验证普通文件（最后一块 < BLOCK_SIZE）终止条件是否正确。
  2. 验证精确为 BLOCK_SIZE * N 大小文件是否发送额外的终止空 DATA 块 (长度 0)。
  3. 可选择丢弃某个指定块的前若干个 ACK 以观测服务器重传（特别是终止空块）。

使用示例:
  python tests/verify_final_empty_block.py --host 127.0.0.1 --port 69 --file f512.bin
  python tests/verify_final_empty_block.py --file big8m.bin
  python tests/verify_final_empty_block.py --file f512.bin --drop-block last --drop-count 1
  python tests/verify_final_empty_block.py --file f1024.bin --verbose

说明:
  --drop-block last  表示只对“终止空块”丢弃 ACK（模拟 ACK 丢失重传）。
  --drop-block <n>   表示对块号 n 丢弃前 --drop-count 次 ACK。

退出码: 0 = 通过; 1 = 协议/终止逻辑异常; 2 = 参数问题; 3 = 网络错误
"""
from __future__ import annotations
import argparse
import os
import socket
import struct
import sys
import time
from typing import Dict, List, Tuple

# 允许脚本在 tests 目录中运行时找到上级 src 模块
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
if PARENT not in sys.path:
    sys.path.insert(0, PARENT)

try:
    from config import BLOCK_SIZE
except Exception:
    BLOCK_SIZE = 512  # 回退

OP_RRQ = 1
OP_DATA = 3
OP_ACK = 4


def build_rrq(filename: str, mode: str = "octet") -> bytes:
    return struct.pack('!H', OP_RRQ) + filename.encode() + b'\x00' + mode.encode() + b'\x00'


def build_ack(block: int) -> bytes:
    return struct.pack('!HH', OP_ACK, block & 0xFFFF)


def parse_data(pkt: bytes) -> Tuple[int, bytes]:
    if len(pkt) < 4:
        raise ValueError("DATA packet too short")
    op, block = struct.unpack('!HH', pkt[:4])
    if op != OP_DATA:
        raise ValueError(f"Unexpected opcode {op}, not DATA")
    return block, pkt[4:]


def human_size(n: int) -> str:
    for unit in ['B','KB','MB','GB']:
        if n < 1024 or unit == 'GB':
            return f"{n:.2f}{unit}"
        n /= 1024
    return f"{n}B"


def run(args: argparse.Namespace) -> int:
    server = (args.host, args.port)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(args.timeout)

    rrq = build_rrq(args.file, args.mode)
    start_ts = time.time()
    s.sendto(rrq, server)

    blocks: Dict[int, int] = {}  # block -> recv count
    ordered: List[int] = []
    total_bytes = 0
    last_data_time = start_ts
    final_block = None
    final_empty = False

    drop_block_number: int | None = None
    if args.drop_block:
        if args.drop_block == 'last':
            drop_block_number = -1  # sentinel, resolve later
        else:
            try:
                drop_block_number = int(args.drop_block)
            except ValueError:
                print("[ERR] --drop-block 只能是整数或 'last'")
                return 2

    # 对指定块丢弃 ACK 的次数计数
    drop_sent = 0

    while True:
        try:
            pkt, addr = s.recvfrom(4 + BLOCK_SIZE + 32)
        except socket.timeout:
            now = time.time()
            if final_block is not None and now - last_data_time >= args.post_wait:
                # 终止后等待没有新数据 -> 结束
                break
            print("[WARN] 超时等待数据，继续 (可能在重传期)")
            continue
        except OSError as e:
            print(f"[ERR] Socket error: {e}")
            return 3

        last_data_time = time.time()
        try:
            block, data = parse_data(pkt)
        except ValueError as e:
            print(f"[IGN] 非 DATA 包/格式错误: {e}")
            continue

        blocks[block] = blocks.get(block, 0) + 1
        if block not in ordered:
            ordered.append(block)
        is_dup = blocks[block] > 1

        if args.verbose:
            print(f"[DATA] block={block:<5} len={len(data):<4} dup={is_dup}")

        # 计算 drop 块实际值
        if drop_block_number == -1 and final_block is not None:
            # 如果 sentinel 并且已经知道 final_block，就解析具体 block
            drop_block_number = final_block

        # 发送 ACK 逻辑 (可能有意丢弃)
        should_drop = False
        if drop_block_number is not None and block == drop_block_number and drop_sent < args.drop_count:
            should_drop = True
            drop_sent += 1
            if args.verbose:
                print(f"[TEST] 丢弃 ACK block={block} 第 {drop_sent}/{args.drop_count} 次 (模拟丢包)")

        if not should_drop:
            s.sendto(build_ack(block), addr)

        total_bytes += len(data)

        if len(data) < BLOCK_SIZE:
            # 文件完成条件
            final_block = block
            if len(data) == 0:
                final_empty = True
            # 等待可能的重传 / 额外包 (post_wait 秒)
            continue

        # 尚未结束，继续循环

        # 安全退出：防过大 (避免无限环)
        if len(ordered) > 70000:
            print("[ERR] 收到块数超过 70000，疑似异常循环，终止")
            return 1

    elapsed = time.time() - start_ts

    # 分析终止逻辑
    status_ok = True
    anomalies: List[str] = []

    if final_block is None:
        anomalies.append("未检测到终止块 (final_block is None)")
        status_ok = False
    else:
        # 判断是否应当出现 final empty
        if final_empty:
            # 判断其前一块长度是否为 BLOCK_SIZE (若存在前一块)
            if len(ordered) >= 2:
                prev_block = ordered[-2]
                # 如果之前块号和 final_block 不是连续（考虑回绕），给出提示
                expected_prev = (final_block - 1) & 0xFFFF or 0xFFFF
                if prev_block != expected_prev:
                    anomalies.append(
                        f"终止空块前一块块号不连续 prev={prev_block} final={final_block}"
                    )
            # 如果只有一个块并且是空块 -> 空文件
        else:
            # 非空终止块
            if total_bytes % BLOCK_SIZE == 0:
                anomalies.append(
                    "文件大小是 BLOCK_SIZE 的整数倍，却没有收到终止空块 (len=0 的 DATA)"
                )
                status_ok = False

    # 检查是否有大量重复块 (提示可能 ACK 丢失较多)
    dups = {b: c for b, c in blocks.items() if c > 1}
    if dups and args.verbose:
        print(f"[INFO] 重传统计: {dups}")

    print("\n===== 结果汇总 =====")
    print(f"文件: {args.file}")
    print(f"块总数: {len(ordered)}")
    print(f"最终块号: {final_block}")
    print(f"终止块是否空: {final_empty}")
    print(f"总数据: {total_bytes} 字节 (~{human_size(total_bytes)})")
    print(f"耗时: {elapsed:.3f} s  速度: {human_size(total_bytes/elapsed)}/s" if elapsed > 0 else "耗时: <0")

    if anomalies:
        print("[ANOMALY]")
        for a in anomalies:
            print("  - " + a)
    else:
        print("无协议异常")

    if status_ok:
        print("[OK] 终止逻辑校验通过")
        return 0
    else:
        print("[FAIL] 终止逻辑存在问题")
        return 1


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="TFTP 终止空块验证工具")
    p.add_argument('--host', default='127.0.0.1')
    p.add_argument('--port', type=int, default=69)
    p.add_argument('--file', required=True, help='请求的文件名 (服务端根目录下)')
    p.add_argument('--mode', default='octet')
    p.add_argument('--timeout', type=float, default=3.0, help='recv 超时秒数')
    p.add_argument('--post-wait', type=float, default=1.0, help='收到终止块后继续等待可能重传的秒数')
    p.add_argument('--drop-block', default=None, help="丢弃该块 ACK，可用 'last' 或具体块号")
    p.add_argument('--drop-count', type=int, default=1, help='对指定块前多少次不发 ACK')
    p.add_argument('--verbose', action='store_true')
    return p.parse_args(argv)


if __name__ == '__main__':
    ns = parse_args(sys.argv[1:])
    try:
        code = run(ns)
    except KeyboardInterrupt:
        print("\n[INTERRUPT] 用户中断")
        code = 130
    sys.exit(code)
