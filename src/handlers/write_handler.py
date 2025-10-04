import os
import socket
import errno

from config import (
    SERVER_ROOT, BLOCK_SIZE, TIMEOUT, MAX_RETRIES, 
    ERR_ACCESS_DENIED, ERR_DISK_FULL, ERR_FILE_ALREADY_EXISTS, ERR_UNKNOWN_TRANSFER_ID, ERR_NOT_DEFINED
)

from utils import (
    build_ack, build_error, parse_data,
    PacketFormatError,
)

def handle_wrq(session_sock:socket.socket, client_addr: tuple[str, int], 
                basename: str, mode: str = "octet", 
                allow_overwrite:bool = False):
    final_path = os.path.join(SERVER_ROOT, basename)
    tmp_path = final_path + ".part"

        # 不允许覆写时，直接返回ERROR
    if not allow_overwrite and os.path.exists(final_path):
        err = build_error(ERR_FILE_ALREADY_EXISTS, "File Already Exists")
        session_sock.sendto(err, client_addr)
        session_sock.close()
        return
    
    try:
        f = open(tmp_path, "wb")# 打开临时文件
    except OSError as e:# 系统级错误时直接退出，并关闭socket
        session_sock.sendto(
            build_error(ERR_ACCESS_DENIED, f"Cannot Open: {e}"),
            client_addr
        )
        session_sock.close()
        return
    
    try:# 处理收到的包
        session_sock.settimeout(TIMEOUT)# 设置计时器
        expected_block = 1
        last_acked = 0# 初始化ACK

        session_sock.sendto(build_ack(last_acked), client_addr)
        attempts = 0# 初始化尝试次数
        total = 0# 计算字节数
        success = False

        while True:
            try:# 尝试接收包，处理超时情况
                pkt, addr = session_sock.recvfrom(4 + BLOCK_SIZE)
            except socket.timeout:
                attempts += 1
                if attempts > MAX_RETRIES:
                    print(f"[WRQ] Timeout exceeded, abort file='{basename}'")
                    session_sock.sendto(build_error(ERR_NOT_DEFINED, "Timeout"), client_addr)
                    return
                session_sock.sendto(build_ack(last_acked), client_addr)
                continue
            except OSError as e :# 处理系统级ERROR
                print(f"[WRQ] Socket error: {e}")
                return 
            
            attempts = 0# 如果到达这一步，说明没出错，接收到数据，因此重置attempts

            if addr != client_addr:# addr不一致
                session_sock.sendto(
                    build_error(ERR_UNKNOWN_TRANSFER_ID, "Unknown Transfer ID"), 
                    addr
                )
                continue

            try:
                block, data = parse_data(pkt)
            except PacketFormatError as e:
                print(f"[WRQ] Bad DATA packet: {e}")
                continue
                
            if block == expected_block:
                # 正常收到expected_block，尝试写入
                try:
                    f.write(data)
                except OSError as e:
                    if e.errno == errno.ENOSPC:
                        # 磁盘已满
                        session_sock.sendto(
                            build_error(ERR_DISK_FULL, "Disk Full"), 
                            client_addr
                        )
                    else:
                        session_sock.sendto(
                            build_error(ERR_ACCESS_DENIED, "Write Failed"),
                            client_addr
                        )
                    return
                
                total += len(data)
                session_sock.sendto(
                    build_ack(block),
                    client_addr
                )
                last_acked = block
                expected_block = (expected_block + 1) & 0xFFFF

                if len(data) < BLOCK_SIZE:
                    success = True
                    print(f"[WRQ] Done file='{basename}' blocks={block} bytes={total}")
                    break
            elif block == last_acked:
                # 与上一次ACK的block一致
                # 可能是ACK丢失，重发ACK
                session_sock.sendto(
                    build_ack(block),
                    client_addr
                )
                continue
            else:
                # 其余情况忽略该块
                print(f"[WRQ] Unexpected block={block} expected={expected_block}")
                continue
    finally:
        f.close()
        if success:
            try:
                os.replace(tmp_path, final_path)
            except Exception as e:
                print(f"[WRQ] rename failed: {e}")
        else:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        session_sock.close()