import os 
import struct
import socket
from typing import Tuple

from config import (
    SERVER_ROOT, BLOCK_SIZE,TIMEOUT, MAX_RETRIES,
    OP_ACK, OP_DATA, OP_ERROR,
    ERR_UNKNOWN_TRANSFER_ID, ERR_NOT_DEFINED,
)

from utils import (
    build_data, parse_ack,build_error,
    PacketFormatError,
)

def handle_rrq(session_sock, client_addr: tuple[str, int], basename:str, mode: str = "octet"):
    path = os.path.join(SERVER_ROOT, basename)
    try:
        with open(path, 'rb') as f:
            block = 1
            session_sock.settimeout(TIMEOUT)

            while True:
                chunk = f.read(BLOCK_SIZE)
                data_pkt = build_data(block, chunk)

                attempts = 0
                while True:
                    attempts += 1
                    session_sock.sendto(data_pkt, client_addr)
                    try:
                        ack_pkt, addr = session_sock.recvfrom(4 + 32)
                    except socket.timeout:# 捕获超时错误
                        if attempts >= MAX_RETRIES:
                            print(f"[RRQ] abort block={block} retries={attempts}")
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
                if len(chunk) < BLOCK_SIZE:
                    print(f"[RRQ] Done file='{basename}' last_block={block}")
                    return

                block = (block + 1) & 0xFFFF
    finally:
        session_sock.close()