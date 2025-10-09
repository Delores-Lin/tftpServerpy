import socket
import os
import sys
import traceback
import threading

from typing import Tuple
from handlers import handle_rrq, handle_wrq
from config import (
    HOST, PORT, 
    BLOCK_SIZE,MAX_SESSIONS,
    OP_RRQ, OP_WRQ, OP_ERROR, 
    ERR_ILLEGAL_TFTP_OPERATION, ERR_FILE_NOT_FOUND, ERR_ACCESS_DENIED
)

from utils import (
    parse_opcode, parse_rrq_wrq,
    build_error,
    sanitize_filename, is_supported_mode,
    PacketFormatError, UnsupportedModeError, InvalidFilenameError
)

from logger_setup import logger

# 精确控制并发，精确限制线程数
_session_sem = threading.BoundedSemaphore(MAX_SESSIONS)
_active_lock = threading.Lock()
_active_count = 0
_shutdown = False

def _run_session(opcode:int, session_sock:socket.socket, client_addr, basename:str, mode:str):
    global _active_count
    with _active_lock:
        _active_count +=1
    try:
        if opcode == OP_RRQ:
            handle_rrq(session_sock, client_addr, basename, mode)
        else:
            handle_wrq(session_sock, client_addr, basename, mode)
    except Exception as e:
        logger.exception(f"[SESSION] Error {client_addr} {basename}")
        # print(f"[SESSION] Error {client_addr} {basename}: {e!r}")
        try:
            session_sock.sendto(
                build_error(ERR_ILLEGAL_TFTP_OPERATION, "Session Error: {e}"),
                client_addr
            )
        except Exception as se:
            logger.exception(f"[SESSION] Send error packet failed: {se}")
            # print(f"[SESSION] Send error packet failed: {se}")
        traceback.print_exc()
    finally:
        with _active_lock:
            _active_count -=1
        _session_sem.release()# 减少并发数
        session_sock.close()

def serve_forever():
    global _shutdown
        # 创建UDP套接字（IPv4）
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # 操作套接字通用层；
        # 允许重新绑定一个处于某些中间状态或刚刚释放的本地地址/端口，
        # 防止程序重启时“Address already in use”
    sock.bind((HOST, PORT))
    sock.settimeout(1.0)
    logger.info(f"[MAIN] TFTP server is listening on {HOST}:{PORT}")
    # print(f"[MAIN] TFTP server is listening on {HOST}:{PORT}")

    while not _shutdown:
        try:
            try:
                data, client_addr = sock.recvfrom(1500)
            except socket.timeout:
                continue
            if not data:
                continue
            try:
                opcode, filename, mode = parse_rrq_wrq(data)
                basename = sanitize_filename(filename)
                logger.info(
                    f"[MAIN] {client_addr} ->"
                    f"{"RRQ" if opcode == OP_RRQ else "WRQ"} filename = '{filename}' "
                    f"mode= '{mode}' santized= '{basename}' "
                )
                # print( f"[MAIN] {client_addr} ->"
                #         f"{"RRQ" if opcode == OP_RRQ else "WRQ"} filename = '{filename}' "
                #         f"mode= '{mode}' santized= '{basename}' ")
                
                # 设置并发上限
                if not _session_sem.acquire(blocking=False):
                    # 获取许可，判断当前会话数，小于并发上限则返回True
                    sock.sendto(
                        build_error(ERR_ACCESS_DENIED, "Server Busy"),
                        client_addr
                    )
                    continue

                session_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                try:
                    session_sock.bind((HOST, 0))
                except Exception as e:
                    sock.sendto(
                        build_error(ERR_ILLEGAL_TFTP_OPERATION, f"Session Bind Fail"),
                        client_addr
                    )
                    logger.exception("[MAIN] Session Bind Fail")
                    _session_sem.release()
                    session_sock.close()
                    continue
                    
                    # 创建线程
                t = threading.Thread(
                    target= _run_session, 
                    args=(opcode, session_sock, client_addr, basename, mode),
                    name=f"TFTP-{ 'RRQ' if opcode==OP_RRQ else 'WRQ'}-{client_addr}"
                )
                t.daemon = True# 守护线程，主进程推出后强制终止
                try:
                    t.start()
                    with _active_lock :
                        approx = _active_count + 1
                    logger.info(f"[MAIN] Spawned {t.name} (approx active={approx})")
                    # print(f"[MAIN] Spawned {t.name} (approx active={approx})")
                except RuntimeError as e:
                    sock.sendto(
                        build_error(ERR_ACCESS_DENIED, "Server Cannot Create"),
                        client_addr
                    )
                    logger.info("[MAIN] Server Cannot Create")
                    _session_sem.release()
                    session_sock.close()
                    continue

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
            logger.exception("\n[MAIN] Shutdown Requested")
            # print("\n[MAIN] Shutdown Requested")
            break
        except Exception as e:
            logger.exception(f"[MAIN] Loop Error")
            # print(f"[MAIN] Loop Error: {e}")
            traceback.print_exc()
    logger.info("[MAIN] Server Exiting")
    # print("[MAIN] Server Exiting")


if __name__ == "__main__":
    serve_forever()