#!/usr/bin/env python3
"""Offline, hash-locked stock disassembly. Never opens a printer or edits an image."""
import argparse
import hashlib
from pathlib import Path
from capstone import Cs, CS_ARCH_ARM, CS_MODE_THUMB, CS_MODE_LITTLE_ENDIAN

SHA256 = '25c9ba099339b482b6ba1b515fbf9bdfb32969abf38d6712be39c7c4b294d1a0'
BASE = 0x08002000
REGIONS = {
    'print-status-eight-byte-payload': (0x0800c466, 0x0800c4f4),
    'error-code-mapping': (0x0800e350, 0x0800e43e),
    'rfid-periodic-mode': (0x08015a58, 0x08015ad4),
    'debug-mode-handler': (0x0801795a, 0x08017996),
    'rfid-read-diagnostic': (0x0801800a, 0x08018058),
    'rfid-retry-error': (0x08015a22, 0x08015a40),
}

def inspect(path):
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != SHA256:
        raise ValueError('Unknown firmware hash; these addresses do not apply')
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
    lines = ['Stock 40.36 SHA256 ' + SHA256, 'Offline analysis; no device access.']
    for name, (start, end) in REGIONS.items():
        lines.append('\n' + name)
        for instruction in decoder.disasm(data[start-BASE:end-BASE], start):
            lines.append(f'{instruction.address:08x}: {instruction.bytes.hex():12} '
                         f'{instruction.mnemonic} {instruction.op_str}')
    return '\n'.join(lines) + '\n'

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('image', type=Path)
    args = ap.parse_args()
    print(inspect(args.image), end='')
