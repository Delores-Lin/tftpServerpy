import os 
import struct
from typing import Tuple

from config import (
    SERVER_ROOT, BLOCK_SIZE,TIMEOUT, MAX_RETRIES,
    OP_ACK, OP_DATA, OP_ERROR,
    ERR_UNKNOWN_TRANSFER_ID, ERR_NOT_DEFINED,
)

from utils import (
    build_data, parse_ack,
    PacketFormatError,
)

def handle_rrq(session_sock, client_addr: tuple[str, int], basename:str, mode: str = "octet"):
    path = os.path.join(SERVER_ROOT, basename)
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
                except Exception:
                    if attempts >= MAX_RETRIES:
                        print(f"[RRQ] abort block={block} retires={attempts}")
                        return
                    print(f"[RRQ] time out block={block} retry={attempts}")
                    continue

                if addr != client_addr:
                    print(f"[RRQ] Ignore foreign addr {addr}")
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