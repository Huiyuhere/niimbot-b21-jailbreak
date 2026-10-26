#!/usr/bin/env python3
"""One bounded B1 diagnostic; optional sparse page, never firmware/tag/calibration writes."""
import argparse
from datetime import datetime, timezone
from functools import reduce
import json
from operator import xor
from pathlib import Path
import time
from b21_probe import ReadOnlyProbe, collect, take_packets

def decode_print_status(payload):
    if len(payload) not in (4, 8, 10):
        raise ValueError(f'Unknown print-status length {len(payload)}')
    page = int.from_bytes(payload[:2], 'big')
    printed, fed = payload[2:4]
    if printed > 100 or fed > 100:
        raise ValueError('Invalid print/feed percentage')
    # Stock 40.36 handler 0x0800c466 emits eight bytes; error is byte 6.
    # Bytes 4-5 are not a measured physical feed distance.
    error = payload[6] if len(payload) in (8, 10) else 0
    return {'page': page, 'print_percent': printed, 'feed_percent': fed, 'error': error}

def packet(command, data):
    # Only bounded normal settings and a single 80 or 86 mm page are allowed.
    allowed = {0x21: {bytes([v]) for v in range(1, 6)},
               0x23: {bytes([v]) for v in (1, 2, 3, 5)},
               0x01: {bytes.fromhex('00010000000000')}, 0xF3: {b'\x01'},
               0x03: {b'\x01'}, 0x13: {bytes.fromhex('028001800001'), bytes.fromhex('02b001800001')},
               0xE3: {b'\x01'}, 0xA3: {b'\x01'}}
    row_ok = (command == 0x85 and len(data) == 54 and int.from_bytes(data[:2], 'big') < 688
              and data[5] == 1 and sum(x.bit_count() for x in data[6:]) <= 64
              and list(data[2:5]) == [sum(x.bit_count() for x in data[6+i*16:22+i*16]) for i in range(3)])
    if not row_ok and data not in allowed.get(command, set()):
        raise ValueError('Not an allowed diagnostic packet')
    return bytes([85, 85, command, len(data)]) + data + bytes([
        reduce(xor, data, command ^ len(data)), 170, 170])

def exchange(port, trace, stage, command, data, response):
    raw = packet(command, data)
    trace.append(dict(time=datetime.now(timezone.utc).isoformat(), stage=stage,
                      direction='tx', hex=raw.hex()))
    port.write(raw)
    if not hasattr(port, '_diagnostic_rx_buffer'):
        port._diagnostic_rx_buffer = bytearray()
    buf = port._diagnostic_rx_buffer
    deadline = time.monotonic() + (.02 if response is None else 3)
    while time.monotonic() < deadline:
        buf.extend(port.read(512))
        for code, payload in take_packets(buf):
            trace.append(dict(time=datetime.now(timezone.utc).isoformat(), stage=stage,
                              direction='rx', command=hex(code), data=payload.hex()))
            if code == 0xDB:
                name = 'WriteRfidFail' if payload == b'\x14' else 'unmapped'
                raise RuntimeError(f'{stage}: printer error {payload.hex()} ({name})')
            if code == response:
                valid_ack = payload == b'\x01' or (command == 0x13 and payload == b'\x01\x00')
                if command != 0xA3 and not valid_ack:
                    raise RuntimeError(f'{stage}: unexpected acknowledgement {payload.hex()}')
                return payload
    if response is None:
        return
    raise TimeoutError(f'{stage}: no response {response:#x}')

def main():
    import serial
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--port', required=True)
    ap.add_argument('--output', required=True, type=Path)
    ap.add_argument('--label-type', type=int, choices=(1, 3), default=1,
                    help='1 gap or 3 continuous; original gap setting restored afterwards')
    ap.add_argument('--print-page', action='store_true', help='Send one sparse page after accepted start')
    ap.add_argument('--alignment-86mm', action='store_true', help='86 mm pitch, short interior marks; one page only')
    args = ap.parse_args()
    # Reserve evidence file before opening the device; never overwrite a result.
    with args.output.open('x') as evidence:
        result = dict(time=datetime.now(timezone.utc).isoformat(), firmware_written=False,
                      image_rows_sent=0, print_start_attempts=0, trace=[], requested_label_type=args.label_type)
        result['raster_height'] = 688 if args.alignment_86mm else 640
        result['pattern'] = 'interior-10-to-50mm' if args.alignment_86mm else 'original-sparse'
        try:
            with serial.Serial(args.port, 115200, timeout=.02, write_timeout=2, exclusive=True) as port:
                before = collect(ReadOnlyProbe(port))
                result['before'] = before
                if (before.get('model_id'), before.get('firmware_version'), before.get('hardware_version')) != (775, '40.36', '40.10'):
                    raise RuntimeError('Identity differs from tested target; stopping')
                status = before.get('paper_status', {})
                if not status.get('lid_closed') or not status.get('paper_inserted'):
                    raise RuntimeError('Lid/paper preflight failed')
                density, label = before.get('density'), before.get('label_type')
                if density != 3 or label != 1:
                    raise RuntimeError('Expected unchanged density 3 / gap label 1; stopping')
                started = False
                label_attempted = False
                try:
                    exchange(port, result['trace'], 'set-existing-density', 0x21, bytes([density]), 0x31)
                    label_attempted = True
                    exchange(port, result['trace'], 'set-test-label-type', 0x23, bytes([args.label_type]), 0x33)
                    started = True
                    result['print_start_attempts'] = 1
                    exchange(port, result['trace'], 'print-start', 1, bytes.fromhex('00010000000000'), 2)
                    result['outcome'] = 'Job start accepted; no image transmitted. Later stages untested.'
                    if args.print_page:
                        exchange(port, result['trace'], 'page-start', 3, b'\x01', 4)
                        size = result['raster_height'].to_bytes(2,'big') + bytes.fromhex('01800001')
                        exchange(port, result['trace'], 'page-size', 0x13, size, 0x14)
                        for row in range(result['raster_height']):
                            bitmap = bytearray(48)
                            # Two thin vertical marks, short bars near top and bottom.
                            top, bottom = (80, 400) if args.alignment_86mm else (60, 578)
                            pixels = [80, 303] if top <= row < bottom + 2 else []
                            if row in (top, top + 1, bottom, bottom + 1):
                                pixels += list(range(176, 208))
                            for pixel in pixels:
                                bitmap[pixel // 8] |= 1 << (7 - pixel % 8)
                            counts = bytes(sum(x.bit_count() for x in bitmap[i*16:(i+1)*16]) for i in range(3))
                            data = row.to_bytes(2, 'big') + counts + b'\x01' + bitmap
                            exchange(port, result['trace'], f'row-{row}', 0x85, data, None)
                            result['image_rows_sent'] += 1
                        exchange(port, result['trace'], 'page-end', 0xE3, b'\x01', 0xE4)
                        result['outcome'] = 'Page sent; completion unconfirmed'
                        deadline = time.monotonic() + 15
                        while time.monotonic() < deadline:
                            status = exchange(port, result['trace'], 'print-status', 0xA3, b'\x01', 0xB3)
                            parsed = decode_print_status(status)
                            if parsed['error']:
                                raise RuntimeError(f"print-status error {parsed['error']}")
                            if parsed['page'] >= 1 and parsed['print_percent'] == 100 and parsed['feed_percent'] == 100:
                                result['outcome'] = 'Device reports page completed; physical confirmation required'
                                break
                            time.sleep(.25)
                except Exception as error:
                    result['error'] = str(error)
                    result['outcome'] = 'Stopped; see exact stage/error and transmitted row count'
                finally:
                    if started:
                        try:
                            exchange(port, result['trace'], 'print-end-cleanup', 0xF3, b'\x01', 0xF4)
                        except Exception as error:
                            result['cleanup_error'] = str(error)
                    if label_attempted and args.label_type != label:
                        result['restore_attempts'] = []
                        for attempt in range(3):
                            try:
                                exchange(port, result['trace'], f'restore-label-type-{attempt+1}', 0x23, bytes([label]), 0x33)
                                result['restore_attempts'].append('acknowledged')
                                break
                            except Exception as error:
                                result['restore_attempts'].append(str(error))
                                if attempt == 2:
                                    result['restore_error'] = str(error)
                                else:
                                    time.sleep(1)
                    result['after'] = collect(ReadOnlyProbe(port))
                    result['settings_unchanged'] = all(result['after'].get(k) == before.get(k)
                                                       for k in ('density', 'label_type', 'firmware_version'))
        except Exception as error:
            result['error'] = str(error)
        finally:
            evidence.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('before','after','trace')}, indent=2))

if __name__ == '__main__':
    main()
