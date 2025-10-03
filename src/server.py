import socket
import os
import sys
import traceback
from typing import Tuple
from handlers import handle_rrq, handle_wrq
from config import (
    HOST, PORT, 
    BLOCK_SIZE,
    OP_RRQ, OP_WRQ, OP_ERROR, 
    ERR_ILLEGAL_TFTP_OPERATION, ERR_FILE_NOT_FOUND, ERR_ACCESS_DENIED
)

from utils import (
    parse_opcode, parse_rrq_wrq,
    build_error,
    sanitize_filename, is_supported_mode,
    PacketFormatError, UnsupportedModeError, InvalidFilenameError
)

def serve_forever():
        # 创建UDP套接字（IPv4）
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 操作套接字通用层；
        # 允许重新绑定一个处于某些中间状态或刚刚释放的本地地址/端口，
        # 防止程序重启时“Address already in use”
    sock.bind((HOST, PORT))
    print(f"[MAIN] TFTP server is listening on {HOST}:{PORT}")

    while True:
        try:
            data, client_addr = sock.recvfrom(1000)
            if not data:
                continue
            try:
                opcode, filename, mode = parse_rrq_wrq(data)
                basename = sanitize_filename(filename)
                print( f"[MAIN] {client_addr} ->"
                        f"{"RRQ" if opcode == OP_RRQ else "WRQ"} filename = '{filename}' "
                        f"mode= '{mode}' santized= '{basename}' ")
                
                session_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                session_sock.bind((HOST, 0))

                if opcode == OP_RRQ:
                    handle_rrq(session_sock, client_addr, basename, mode)
                else:
                    handle_wrq(session_sock, client_addr, basename, mode)

            except FileNotFoundError:
                err = build_error(ERR_FILE_NOT_FOUND, "File Not Found")
                sock.sendto(err, client_addr)
            except UnsupportedModeError as e:
                err = build_error(ERR_ILLEGAL_TFTP_OPERATION, str(e))
                sock.sendto(err, client_addr)
            except InvalidFilenameError as e:
                err = build_error(ERR_ACCESS_DENIED, str(e))
                sock.sendto(err, client_addr)
            except PacketFormatError as e:
                err = build_error(ERR_ILLEGAL_TFTP_OPERATION, f"Bad Request: {e}")
                sock.sendto(err, client_addr)
            except Exception as e:
                err = build_error(ERR_ILLEGAL_TFTP_OPERATION, f"Internal Error: {e}")
                sock.sendto(err, client_addr)
                traceback.print_exc()
        except KeyboardInterrupt:
            print("\n[MAIN] Shutdown Requested")
            break
        except Exception as e:
            print(f"[MAIN] Loop Error: {e}")
            traceback.print_exc()
    print("[MAIN] Server Exiting")


if __name__ == "__main__":
    serve_forever()