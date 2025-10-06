import os 
import struct
import socket
from typing import Tuple

from config import (
    SERVER_ROOT, BLOCK_SIZE,TIMEOUT, MAX_RETRIES,
    OP_ACK, OP_DATA, OP_ERROR,
    ERR_UNKNOWN_TRANSFER_ID, ERR_NOT_DEFINED,ERR_FILE_NOT_FOUND
)

from utils import (
    build_data, parse_ack, build_error,
    PacketFormatError,
)

def handle_rrq(session_sock, client_addr: tuple[str, int], basename:str, mode: str = "octet"):
    path = os.path.join(SERVER_ROOT, basename)

    if not os.path.exists(path):
        session_sock.sendto(
            build_error(ERR_FILE_NOT_FOUND, "File Doesn't Exist"),
            client_addr
        )
        session_sock.close()
        return
    try:
        with open(path, 'rb') as f:
            chunk = f.read(BLOCK_SIZE)
            # 处理空文件
            if chunk == b'':
                block = 1
                session_sock.settimeout(TIMEOUT)
                empty_pkt = build_data(block, b'')
                attempts = 0
                while True:
                    attempts += 1
                    session_sock.sendto(empty_pkt, client_addr)
                    try:
                        ack_pkt, addr = session_sock.recvfrom(4 + 32)
                    except socket.timeout :
                        if attempts >= MAX_RETRIES :
                            print("[RRQ] Abort empty-file retries exceeded")
                            session_sock.sendto(
                                build_error(ERR_NOT_DEFINED, "Timeout"),
                                client_addr
                            )
                            return
                        print(f"[RRQ] Timeout block={block} retry={attempts}")
                        continue
                    except OSError as e :
                        print(f"[RRQ] Socket error block={block}: {e}")
                        return
                    if addr != client_addr :
                        session_sock.sendto(
                            build_error(ERR_UNKNOWN_TRANSFER_ID, "Unknown Transfer ID"),
                            addr
                        )
                        continue
                    try:
                        ack_block = parse_ack(ack_pkt)
                    except PacketFormatError as e:
                        print(f"[RRQ] {e} Ignore")
                        continue
                    if ack_block != block:
                        continue
                    if ack_block == block and addr == client_addr:
                        print("[RRQ] Done empty file")
                        return
                    
            # 不是空文件，则需要将read的第一块回退，重新进入原始循环处理
            f.seek(-len(chunk), 1)
            block = 1
            session_sock.settimeout(TIMEOUT)

            while True:
                chunk = f.read(BLOCK_SIZE)
                data_pkt = build_data(block, chunk)

                attempts = 0
                    # 重传逻辑
                while True:
                    attempts += 1
                    session_sock.sendto(data_pkt, client_addr)
                    try:
                        ack_pkt, addr = session_sock.recvfrom(4 + 32)
                    except socket.timeout:# 捕获超时错误
                        if attempts >= MAX_RETRIES:
                            print(f"[RRQ] abort block={block} retries={attempts}")
                            # 发送超时错误便于客户端快速结束
                            try:
                                session_sock.sendto(
                                    build_error(ERR_NOT_DEFINED, "Timeout"),
                                    client_addr
                                )
                            except OSError:
                                pass
                            return
                        print(f"[RRQ] time out block={block} retries={attempts}")
                        continue
                    except OSError as e:# 仅在系统层IO问题时终止
                        print(f"[RRQ] Socket Error Block={block}: {e}")
                        return

                    if addr != client_addr:
                        print(f"[RRQ] Ignore foreign addr {addr}")
                        err = build_error(ERR_UNKNOWN_TRANSFER_ID, "Unknown transfer ID")
                        session_sock.sendto(err, addr)
                        continue

                    try:
                        ack_block = parse_ack(ack_pkt)
                    except PacketFormatError as e:
                        print(f"[RRQ] {e} Ignore")
                        continue
                    
                    if ack_block != block:
                        print(f"[RRQ] Wrong ACK block={ack_block} expect={block}")
                        continue
                    break

                # 如果最后一块小于BLOCK_SIZE，说明传输完成，因此退出
                if len(chunk) < BLOCK_SIZE:
                    print(f"[RRQ] Done file='{basename}' last_block={block}")
                    return
                
                nextb = f.read(1)
                if nextb == b'':# 下一个字节是空，说明传输完成
                    next_block = (block + 1) & 0xFFFF
                    if next_block == 0:
                        next_block = 1
                    empty_pkt = build_data(next_block, b'')
                    attempts = 0
                    while True :
                        attempts += 1
                        session_sock.sendto(empty_pkt, client_addr)
                        try:
                            ack_pkt, addr = session_sock.recvfrom(4 + 32)
                        except socket.timeout:
                            if attempts >= MAX_RETRIES:
                                print(f"[RRQ] Abort final-empty block={next_block} retry={attempts}")
                                return
                            print(f"[RRQ] Timeout final-empty block={next_block} retry={attempts}")
                            continue
                        if addr != client_addr:
                            # 忽略陌生 TID, 继续等待正确 ACK
                            session_sock.sendto(
                                build_error(ERR_UNKNOWN_TRANSFER_ID, "Unknown Transfer ID"),
                                addr
                            )
                            continue
                        try:
                            ack_block = parse_ack(ack_pkt)
                        except PacketFormatError as e:
                            print(f"[RRQ] {e} Ignore")
                            continue
                        if ack_block == next_block :
                            print(f"[RRQ] Done file='{basename}' final-empty block={next_block}")
                            return
                else:
                    f.seek(-1,1)

                block = (block + 1) & 0xFFFF
                if block == 0:
                    block = 1
    finally:
        session_sock.close()