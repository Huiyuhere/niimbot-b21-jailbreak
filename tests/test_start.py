import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from b21_start_test import packet, exchange, decode_print_status

class FakePort:
    def __init__(self, reply): self.reply = reply
    def write(self, data): self.sent = data
    def read(self, count):
        reply, self.reply = self.reply, b''
        return reply

class StartTests(unittest.TestCase):
    def test_c2b_eight_byte_status_error_is_not_ignored(self):
        self.assertEqual(decode_print_status(bytes.fromhex('00016464031e1401'))['error'], 20)
        self.assertEqual(decode_print_status(bytes.fromhex('00016464031e0001')),
                         {'page':1,'print_percent':100,'feed_percent':100,'error':0})
        with self.assertRaises(ValueError): decode_print_status(bytes.fromhex('00016564031e0001'))

    def test_b21_two_byte_page_size_ack(self):
        port = FakePort(bytes.fromhex('55551402010017aaaa'))
        self.assertEqual(exchange(port, [], 'size', 0x13, bytes.fromhex('028001800001'), 0x14), b'\x01\x00')

    def test_error_preserves_stage(self):
        port = FakePort(bytes.fromhex('5555db0114ceaaaa'))
        with self.assertRaisesRegex(RuntimeError, 'start: printer error 14.*WriteRfidFail'):
            exchange(port, [], 'start', 1, bytes.fromhex('00010000000000'), 2)

    def test_zero_ack_is_not_success(self):
        port = FakePort(bytes.fromhex('555502010003aaaa'))
        with self.assertRaisesRegex(RuntimeError, 'unexpected acknowledgement 00'):
            exchange(port, [], 'start', 1, bytes.fromhex('00010000000000'), 2)

    def test_rejects_unbounded_rows_and_firmware_commands(self):
        for command, data in [(0x85, (640).to_bytes(2,'big') + bytes([0,0,0,1]) + bytes(48)),
                              (0x85, bytes([0,0,128,128,128,1]) + bytes([255])*48),
                              (0xF5, b'\x01'), (0x8e, b'\x01')]:
            with self.assertRaises(ValueError): packet(command,data)
