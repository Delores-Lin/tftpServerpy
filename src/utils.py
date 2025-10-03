import struct
import os
import re
from config import (OP_ACK,OP_DATA,OP_ERROR,OP_RRQ,OP_WRQ,BLOCK_SIZE)
from config import (MODE_OCTET)

# error
class PacketFormatError(Exception):
    pass
class UnsupportedModeError(Exception):
    pass
class InvalidFilenameError(Exception):
    pass



# build
def build_ack(block_num:int):
    if not(0 <= block_num <= 0xFFFF):
        raise ValueError("Block Num Out of Range")
    opcode = OP_ACK
    header = struct.pack('!HH',opcode,block_num)
    return header

def build_data(block_num:int, data):
    if not(0 <= block_num <= 0xFFFF):
        raise ValueError("Block Num Out of Range")
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("Data Must Be Bytes")
    if len(data) > BLOCK_SIZE:
        raise ValueError(f"Data Length Exceeds BLOCK_SIZE({BLOCK_SIZE})")
    opcode = OP_DATA
    header = opcode.to_bytes(2,'big') + block_num.to_bytes(2, 'big')
    packet = header + data
    return packet

def build_error(code:int, message:str):
    opcode = OP_ERROR
    err_code = code
    err_message = message.encode('ascii', 'replace')
    header = struct.pack("!HH", opcode, err_code)
    return header + err_message + b'\x00'


# parse
def parse_opcode(packet:bytes):
    if len(packet) < 2 :
        raise PacketFormatError("Opcode Length Too Short")
    opcode = struct.unpack('!H', packet[0:2])[0]
    return opcode

def parse_ack(packet:bytes):
    if len(packet) < 4:
        raise PacketFormatError("ACK Length Too Short")
    opcode = struct.unpack('!H', packet[0:2])[0]
    if int(opcode) != OP_ACK:
        raise PacketFormatError("Not an ACK")
    block_num = struct.unpack('!H', packet[2:4])[0]
    return block_num

def parse_data(packet:bytes):
    if len(packet) < 4 :
        raise PacketFormatError("Data Length Too Short")
    opcode = struct.unpack('!H', packet[0:2])[0]
    if opcode != OP_DATA :
        raise PacketFormatError("Not a Data")
    block_num = struct.unpack('!H', packet[2:4])[0]
    data = packet[4:]
    return block_num, data

def parse_rrq_wrq(packet:bytes):
    if len(packet) < 4:
        raise PacketFormatError("Request Length Too Short")
    opcode = struct.unpack('!H', packet[0:2])[0]
    if opcode not in (OP_RRQ, OP_WRQ) :
        raise PacketFormatError("Not a RRQ or WRQ")
    body = packet[2:]
    parts = body.split(b'\x00')
    if len(parts) < 3:
        raise PacketFormatError("Missing Filename/Mode Terminator")
    filename = parts[0]
    transfer_mode = parts[1]
    filename = filename.decode('ascii','ignore')
    if not filename :
        raise InvalidFilenameError("Filename Is Empty")
    transfer_mode = transfer_mode.decode('ascii','ignore').lower()
    if not transfer_mode:
        raise UnsupportedModeError("Empty Mode Field")
    if not is_supported_mode(transfer_mode):
        raise UnsupportedModeError(f"Unsupported mode: {transfer_mode}")
    return opcode, filename, transfer_mode

def parse_error(packet:bytes):
    if len(packet) < 5:
        raise PacketFormatError("Error Length Too Short")
    opcode = struct.unpack('!H', packet[0:2])[0]
    if opcode != OP_ERROR:
        raise PacketFormatError("Not an Error")
    err_code = struct.unpack('!H', packet[2:4])[0]
    if not(0 <= err_code <= 7):
        raise PacketFormatError("Wrong Error Code")
    err_message = packet[4:].rstrip(b'\x00').decode('ascii', 'ignore')
    return err_code, err_message


def sanitize_filename(filename:str):
    filename = filename.strip()
    basename = os.path.basename(filename)
    if not basename:
        raise InvalidFilenameError("Filename Empty")
    if ".." in basename :
        raise InvalidFilenameError("Path Traversal Not Allowed")
    if any(c in basename for c in ('\\','/')):
        raise InvalidFilenameError("Path Separator Not Allowed")
    if not re.match(r'^[A-Za-z0-9._-]+$', basename):
        raise InvalidFilenameError("Illegal characters in filename")
    return basename

def is_supported_mode(mode:str):
    return mode.lower() == MODE_OCTET