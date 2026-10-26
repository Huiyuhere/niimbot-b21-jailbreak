import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'tools'))
from b21_probe import frame, take_packets, decode_version

class ProbeTests(unittest.TestCase):
    def test_c2b_version_encoding(self):
        self.assertEqual(decode_version(bytes.fromhex('2824')), '40.36')
        self.assertEqual(decode_version(bytes.fromhex('280a')), '40.10')
        with self.assertRaises(ValueError): decode_version(b'')

    def test_expected_info_frame(self):
        self.assertEqual(frame(0x40,b'\x08').hex(),'555540010849aaaa')

    def test_write_and_identifying_commands_rejected(self):
        for cmd,data in [(0xF5,b'\x01'),(0x21,b'\x05'),(0x23,b'\x02'),
                         (0x01,b'\x01'),(0x40,b'\x0b'),(0x40,b'\x0d'),(0x1A,b'\x01')]:
            with self.assertRaises(ValueError): frame(cmd,data)

    def test_parser_handles_fragmented_and_corrupt_packets(self):
        # Response to model request: model 775 = 0x0307.
        good=bytes.fromhex('5555480203074eaaaa')
        bad=bytearray(good); bad[-3]^=1
        stream=bytearray(b'noise'+bad+good[:5])
        self.assertEqual(take_packets(stream),[])
        stream.extend(good[5:])
        self.assertEqual(take_packets(stream),[(0x48,b'\x03\x07')])

if __name__ == '__main__': unittest.main()
