#!/usr/bin/env python3
"""
简易 TFTP 测试脚本（仅使用标准库），支持 RRQ(下载) 与 WRQ(上传) 基本功能验证。

使用方式示例：

1) 上传（WRQ）
   python tests/tftp_client_test.py wrq --host 127.0.0.1 --port 69 \
       --local README.md --remote readme_copy.md

2) 下载（RRQ）
   python tests/tftp_client_test.py rrq --host 127.0.0.1 --port 69 \
       --remote hello.txt --local hello_down.txt

3) 连续循环测试（下载 10 次）：
   python tests/tftp_client_test.py rrq --host 127.0.0.1 --port 69 \
       --remote hello.txt --local out.txt --loop 10

4) 指定超时与最大重试：
   python tests/tftp_client_test.py rrq --timeout 3 --retries 4 ...

脚本特点：
- 纯 Python socket 实现，不依赖外部库
- 可调超时、重试次数
- 简单 ERROR 包处理与日志输出
- 便于与你的服务器交叉验证上传/下载正确性

注意：
- 这里只实现 octet 模式
- 未实现窗口扩展、选项协商 (RFC 2347/2348/2349) 等
- 仅供教学/功能验证，不用于生产
"""
from __future__ import annotations
import argparse
import os
import socket
import sys
import time
from typing import Tuple

# TFTP 常量
OP_RRQ   = 1
OP_WRQ   = 2
OP_DATA  = 3
OP_ACK   = 4
OP_ERROR = 5
BLOCK_SIZE = 512
MODE = b"octet"

class TFTPError(Exception):
    pass

# ---------------- Packet Builders -----------------

def build_rrq(filename: str) -> bytes:
    return (OP_RRQ).to_bytes(2, 'big') + filename.encode('utf-8') + b'\0' + MODE + b'\0'

def build_wrq(filename: str) -> bytes:
    return (OP_WRQ).to_bytes(2, 'big') + filename.encode('utf-8') + b'\0' + MODE + b'\0'

def build_data(block: int, payload: bytes) -> bytes:
    return (OP_DATA).to_bytes(2, 'big') + block.to_bytes(2, 'big') + payload

def build_ack(block: int) -> bytes:
    return (OP_ACK).to_bytes(2, 'big') + block.to_bytes(2, 'big')

def parse_packet(data: bytes):
    if len(data) < 4:
        raise TFTPError("Packet too short")
    op = int.from_bytes(data[0:2], 'big')
    if op == OP_DATA:
        block = int.from_bytes(data[2:4], 'big')
        return op, block, data[4:]
    elif op == OP_ACK:
        block = int.from_bytes(data[2:4], 'big')
        return op, block, b''
    elif op == OP_ERROR:
        code = int.from_bytes(data[2:4], 'big')
        # error msg 以 0 结尾
        try:
            msg = data[4:-1].decode('utf-8', errors='replace')
        except Exception:
            msg = '<decode error>'
        return op, code, msg
    else:
        return op, None, data[2:]

# ---------------- Core Operations -----------------

def do_rrq(host: str, port: int, remote: str, local: str, timeout: float, retries: int, verbose: bool=False) -> None:
    """执行下载 (RRQ)"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    start = time.time()
    # 发送 RRQ 到 (host, port)
    sock.sendto(build_rrq(remote), (host, port))
    expected_block = 1
    received_bytes = 0
    last_data_time = start
    with open(local, 'wb') as f:
        while True:
            attempt = 0
            while True:
                try:
                    data, addr = sock.recvfrom(4 + BLOCK_SIZE + 4)
                    last_data_time = time.time()
                    break
                except socket.timeout:
                    attempt += 1
                    if attempt > retries:
                        raise TFTPError(f"RRQ timeout block={expected_block}")
                    if verbose:
                        print(f"[RRQ] Timeout waiting block {expected_block}, retry {attempt}/{retries}")
                    # 重发 RRQ 只在第一次块还没收到时合理；超过 block1 后重发上一个 ACK
                    if expected_block == 1:
                        sock.sendto(build_rrq(remote), (host, port))
                    else:
                        # 重发上一个 ACK 触发服务器重发下一块
                        sock.sendto(build_ack(expected_block - 1), addr)
            op, x, payload = parse_packet(data)
            if op == OP_ERROR:
                raise TFTPError(f"Server ERROR code={x} msg={payload}")
            if op != OP_DATA:
                if verbose:
                    print(f"[RRQ] Ignore unexpected op={op}")
                continue
            block = x
            if block == expected_block:
                f.write(payload)
                received_bytes += len(payload)
                if verbose:
                    print(f"[RRQ] Received block {block} size={len(payload)}")
                sock.sendto(build_ack(block), addr)
                expected_block += 1
                if len(payload) < BLOCK_SIZE:
                    # 最后一块
                    break
            elif block < expected_block:
                # 重复块 => 说明 ACK 丢了，再 ACK 一次
                if verbose:
                    print(f"[RRQ] Duplicate block {block}, re-ACK")
                sock.sendto(build_ack(block), addr)
            else:
                if verbose:
                    print(f"[RRQ] Future block {block} (expected {expected_block}), ignore")
    elapsed = time.time() - start
    if verbose:
        print(f"[RRQ] Done bytes={received_bytes} time={elapsed:.3f}s speed={received_bytes/1024/elapsed if elapsed>0 else 0:.2f} KB/s")


def do_wrq(host: str, port: int, local: str, remote: str, timeout: float, retries: int, verbose: bool=False) -> None:
    """执行上传 (WRQ)"""
    if not os.path.exists(local):
        raise TFTPError(f"Local file not found: {local}")
    size = os.path.getsize(local)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(timeout)
    start = time.time()
    sock.sendto(build_wrq(remote), (host, port))
    # 需要等待 ACK(0)
    attempt = 0
    server_addr = None
    while True:
        try:
            data, addr = sock.recvfrom(4 + 4)
            op, block, _ = parse_packet(data)
            if op == OP_ERROR:
                raise TFTPError(f"Server ERROR code={block}")
            if op == OP_ACK and block == 0:
                server_addr = addr
                break
        except socket.timeout:
            attempt += 1
            if attempt > retries:
                raise TFTPError("WRQ no ACK(0)")
            if verbose:
                print(f"[WRQ] Timeout waiting ACK(0), retry {attempt}/{retries}")
            sock.sendto(build_wrq(remote), (host, port))
    sent_bytes = 0
    block_num = 1
    with open(local, 'rb') as f:
        while True:
            chunk = f.read(BLOCK_SIZE)
            payload = chunk if chunk else b''
            packet = build_data(block_num, payload)
            attempt = 0
            while True:
                sock.sendto(packet, server_addr)
                try:
                    data, addr = sock.recvfrom(4 + 4)
                    op, b, _ = parse_packet(data)
                    if op == OP_ERROR:
                        raise TFTPError(f"Server ERROR code={b}")
                    if op == OP_ACK and b == block_num:
                        if verbose:
                            print(f"[WRQ] ACK {b}")
                        break
                    elif op == OP_ACK and b == block_num - 1:
                        # 服务器没收到上一 ACK（极少），忽略，它会继续重复请求
                        continue
                except socket.timeout:
                    attempt += 1
                    if attempt > retries:
                        raise TFTPError(f"WRQ block {block_num} exceed retries")
                    if verbose:
                        print(f"[WRQ] Timeout block {block_num}, retry {attempt}/{retries}")
                    continue
            sent_bytes += len(payload)
            if len(payload) < BLOCK_SIZE:
                break
            block_num = (block_num + 1) & 0xFFFF
            if block_num == 0:
                # TFTP 块号在 65535 后回绕到 0，再下一个是 1
                block_num = 1
    elapsed = time.time() - start
    if verbose:
        print(f"[WRQ] Done bytes={sent_bytes} file_size={size} time={elapsed:.3f}s speed={sent_bytes/1024/elapsed if elapsed>0 else 0:.2f} KB/s")

# ---------------- Argument Parsing -----------------

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="TFTP 功能测试脚本 (RRQ / WRQ)")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_rrq = sub.add_parser("rrq", help="下载远程文件")
    p_rrq.add_argument("--host", required=True)
    p_rrq.add_argument("--port", type=int, required=True)
    p_rrq.add_argument("--remote", required=True, help="服务器上的文件名")
    p_rrq.add_argument("--local", required=True, help="保存到本地的文件名")
    p_rrq.add_argument("--timeout", type=float, default=5.0)
    p_rrq.add_argument("--retries", type=int, default=5)
    p_rrq.add_argument("--loop", type=int, default=1, help="循环下载次数")
    p_rrq.add_argument("-v", "--verbose", action="store_true")

    p_wrq = sub.add_parser("wrq", help="上传本地文件")
    p_wrq.add_argument("--host", required=True)
    p_wrq.add_argument("--port", type=int, required=True)
    p_wrq.add_argument("--local", required=True, help="本地待上传文件")
    p_wrq.add_argument("--remote", required=True, help="服务器保存文件名")
    p_wrq.add_argument("--timeout", type=float, default=5.0)
    p_wrq.add_argument("--retries", type=int, default=5)
    p_wrq.add_argument("-v", "--verbose", action="store_true")

    return p.parse_args(argv)

# ---------------- Main -----------------

def main(argv=None):
    args = parse_args(argv)
    try:
        if args.cmd == 'rrq':
            for i in range(1, args.loop + 1):
                if args.loop > 1:
                    print(f"[RRQ] Round {i}/{args.loop}")
                do_rrq(args.host, args.port, args.remote, args.local if args.loop == 1 else f"{args.local}.{i}",
                       args.timeout, args.retries, args.verbose)
        elif args.cmd == 'wrq':
            do_wrq(args.host, args.port, args.local, args.remote, args.timeout, args.retries, args.verbose)
        print("OK")
    except TFTPError as e:
        print(f"ERROR: {e}")
        return 2
    except KeyboardInterrupt:
        print("Interrupted")
        return 130
    return 0

if __name__ == '__main__':
    sys.exit(main())
