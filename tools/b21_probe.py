#!/usr/bin/env python3
"""Read-only USB identity/status probe. No flash, erase, RFID write or print commands."""
import argparse
from datetime import datetime, timezone
from functools import reduce
import json
from operator import xor
from pathlib import Path
import time

# Explicit allowlist: handshake, non-identifying info fields, heartbeat status.
ALLOWED = {0xC1: {b'\x01'}, 0x40: {bytes([n]) for n in (1, 3, 8, 9, 10, 12)},
           0xDC: {b'\x01', b'\x03'}}

def frame(command, data):
    if command not in ALLOWED or data not in ALLOWED[command]:
        raise ValueError('Command/payload is not in the read-only allowlist')
    checksum = reduce(xor, data, command ^ len(data))
    return bytes([0x55, 0x55, command, len(data)]) + data + bytes([checksum, 0xAA, 0xAA])

def take_packets(buffer):
    packets = []
    while len(buffer) >= 7:
        start = buffer.find(b'\x55\x55')
        if start < 0:
            buffer[:] = buffer[-1:] if buffer[-1] == 0x55 else b''
            break
        del buffer[:start]
        if len(buffer) < 7:
            break
        size = buffer[3] + 7
        if len(buffer) < size:
            break
        raw = bytes(buffer[:size])
        valid = raw[-2:] == b'\xaa\xaa' and reduce(xor, raw[2:-3], 0) == raw[-3]
        if not valid:
            del buffer[0]
            continue
        packets.append((raw[2], raw[4:-3]))
        del buffer[:size]
    return packets

class ReadOnlyProbe:
    def __init__(self, port):
        self.port, self.buffer, self.trace = port, bytearray(), []

    def query(self, command, data, response):
        packet = frame(command, data)  # validate BEFORE any device write
        self.port.write(packet)
        self.trace.append({'direction':'tx', 'hex':packet.hex()})
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            self.buffer.extend(self.port.read(512))
            for code, payload in take_packets(self.buffer):
                # No serial, Bluetooth-address, RFID or factory-data requests are issued.
                self.trace.append({'direction':'rx', 'command':hex(code), 'data':payload.hex()})
                if code == 0xDB:
                    raise RuntimeError('Printer error: ' + payload.hex())
                if code in (response if isinstance(response, tuple) else (response,)):
                    return payload
        raise TimeoutError(f'No response {response} to {command:#x}')

def decode_version(raw):
    if len(raw) != 2:
        raise ValueError('Version must contain two bytes')
    # B21 C2B 40.x: major/minor bytes; cross-check against heartbeat identity.
    return f'{raw[0]}.{raw[1]:02d}'

def collect(probe):
    result = {'captured_at':datetime.now(timezone.utc).isoformat(), 'transport':'USB serial',
              'firmware_written':False, 'labels_requested':0}
    result['handshake'] = probe.query(0xC1, b'\x01', 0xC2).hex()
    for name, key in [('model_id',8), ('firmware_version',9), ('hardware_version',12),
                      ('density',1), ('label_type',3), ('battery_level',10)]:
        try:
            raw = probe.query(0x40, bytes([key]), 0x40 + key)
            value = int.from_bytes(raw, 'big')
            if key == 8 and len(raw) == 1:
                value <<= 8
            result[name] = decode_version(raw) if key in (9,12) else value
        except (TimeoutError, RuntimeError) as error:
            result[name + '_error'] = str(error)
    try:
        raw = probe.query(0xDC, b'\x03', (0xDE, 0xDF))
        if len(raw) == 10:
            result['heartbeat_identity'] = {
                'hardware_version':f'{raw[0]}.{raw[1]:02d}',
                'firmware_version':f'{raw[2]}.{raw[3]:02d}',
                'printhead_width_dots':int.from_bytes(raw[4:6],'big'),
                'resolution_class':raw[6], 'printhead_alignment':raw[7],
                'supports_rfid':bool(raw[8]), 'supports_write_rfid':bool(raw[9])}
        else:
            result['heartbeat_identity_unparsed'] = raw.hex()
    except (TimeoutError, RuntimeError) as error:
        result['heartbeat_identity_error'] = str(error)
    try:
        raw = probe.query(0xDC, b'\x01', 0xDD)
        if len(raw) in (13,19):
            offset = 9 if len(raw) == 13 else 15
            result['paper_status'] = {'lid_closed':raw[offset] == 0,
                'battery_percent':raw[offset+1] * 25 if raw[offset+1] <= 4 else raw[offset+1], 'paper_inserted':raw[offset+2] == 0,
                'rfid_recognized':raw[offset+3] != 0}
        else:
            result['paper_status_unparsed'] = raw.hex()
    except (TimeoutError, RuntimeError) as error:
        result['paper_status_error'] = str(error)
    result['trace'] = probe.trace
    return result

def main():
    import serial
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--port', required=True)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    if args.output.exists():
        ap.error('Output already exists; use a new filename to preserve evidence')
    with serial.Serial(args.port,115200,timeout=0.1,write_timeout=2,exclusive=True) as port:
        result = collect(ReadOnlyProbe(port))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key != 'trace'},indent=2))

if __name__ == '__main__':
    main()
