#!/usr/bin/env python3
"""One B1 job-start diagnostic; no image, firmware, tag or calibration writes."""
import argparse
from datetime import datetime, timezone
from functools import reduce
import json
from operator import xor
from pathlib import Path
import time
from b21_probe import ReadOnlyProbe, collect, take_packets

def packet(command, data):
    # Only unchanged normal settings and one-page B1 start/end are allowed.
    allowed = {0x21: {bytes([v]) for v in range(1, 6)},
               0x23: {bytes([v]) for v in (1, 2, 3, 5)},
               0x01: {bytes.fromhex('00010000000000')}, 0xF3: {b'\x01'}}
    if data not in allowed.get(command, set()):
        raise ValueError('Not an allowed diagnostic packet')
    return bytes([85, 85, command, len(data)]) + data + bytes([
        reduce(xor, data, command ^ len(data)), 170, 170])

def exchange(port, trace, stage, command, data, response):
    raw = packet(command, data)
    trace.append(dict(time=datetime.now(timezone.utc).isoformat(), stage=stage,
                      direction='tx', hex=raw.hex()))
    port.write(raw)
    buf = bytearray()
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline:
        buf.extend(port.read(512))
        for code, payload in take_packets(buf):
            trace.append(dict(time=datetime.now(timezone.utc).isoformat(), stage=stage,
                              direction='rx', command=hex(code), data=payload.hex()))
            if code == 0xDB:
                name = 'WriteRfidFail' if payload == b'\x14' else 'unmapped'
                raise RuntimeError(f'{stage}: printer error {payload.hex()} ({name})')
            if code == response:
                if payload != b'\x01':
                    raise RuntimeError(f'{stage}: unexpected acknowledgement {payload.hex()}')
                return
    raise TimeoutError(f'{stage}: no response {response:#x}')

def main():
    import serial
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--port', required=True)
    ap.add_argument('--output', required=True, type=Path)
    args = ap.parse_args()
    # Reserve evidence file before opening the device; never overwrite a result.
    with args.output.open('x') as evidence:
        result = dict(time=datetime.now(timezone.utc).isoformat(), firmware_written=False,
                      image_rows_sent=0, print_start_attempts=0, trace=[])
        try:
            with serial.Serial(args.port, 115200, timeout=.1, write_timeout=2, exclusive=True) as port:
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
                try:
                    exchange(port, result['trace'], 'set-existing-density', 0x21, bytes([density]), 0x31)
                    exchange(port, result['trace'], 'set-existing-label-type', 0x23, bytes([label]), 0x33)
                    started = True
                    result['print_start_attempts'] = 1
                    exchange(port, result['trace'], 'print-start', 1, bytes.fromhex('00010000000000'), 2)
                    result['outcome'] = 'Job start accepted; no image transmitted. Later stages untested.'
                except Exception as error:
                    result['error'] = str(error)
                finally:
                    if started:
                        try:
                            exchange(port, result['trace'], 'print-end-cleanup', 0xF3, b'\x01', 0xF4)
                        except Exception as error:
                            result['cleanup_error'] = str(error)
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
