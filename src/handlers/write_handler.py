def handle_wrq(session_sock, client_addr, basename: str, mode: str = "octet"):
    print(f"[WRQ] (TODO) start write session -> {client_addr} file='{basename}'")
    # 后续实现：先发送 ACK(0) 再循环收 DATA 块并写入