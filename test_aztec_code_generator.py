#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import unittest
from aztec_code_generator import (
    reed_solomon, find_optimal_sequence, optimal_sequence_to_bits, get_data_codewords, encoding_to_eci,
    Mode, Latch, Shift, Misc,
    AztecCode,
)

import codecs
from tempfile import NamedTemporaryFile

try:
    import zxing
except ImportError:
    zxing = None

def b(*l):
    return [(ord(c) if len(c)==1 else c.encode()) if isinstance(c, str) else c for c in l]

class Test(unittest.TestCase):
    """
    Test aztec_code_generator module
    """

    def test_reed_solomon(self):
        """ Test reed_solomon function """
        cw = []
        reed_solomon(cw, 0, 0, 0, 0)
        self.assertEqual(cw, [])
        cw = [0, 0] + [0, 0]
        reed_solomon(cw, 2, 2, 16, 19)
        self.assertEqual(cw, [0, 0, 0, 0])
        cw = [9, 50, 1, 41, 47, 2, 39, 37, 1, 27] + [0, 0, 0, 0, 0, 0, 0]
        reed_solomon(cw, 10, 7, 64, 67)
        self.assertEqual(cw, [9, 50, 1, 41, 47, 2, 39, 37, 1, 27, 38, 50, 8, 16, 10, 20, 40])
        cw = [0, 9] + [0, 0, 0, 0, 0]
        reed_solomon(cw, 2, 5, 16, 19)
        self.assertEqual(cw, [0, 9, 12, 2, 3, 1, 9])

    def test_find_optimal_sequence_ascii_strings(self):
        """ Test find_optimal_sequence function for ASCII strings """
        self.assertEqual(find_optimal_sequence(''), b())
        self.assertEqual(find_optimal_sequence('ABC'), b('A', 'B', 'C'))
        self.assertEqual(find_optimal_sequence('abc'), b(Latch.LOWER, 'a', 'b', 'c'))
        self.assertEqual(find_optimal_sequence('Wikipedia, the free encyclopedia'), b(
            'W', Latch.LOWER, 'i', 'k', 'i', 'p', 'e', 'd', 'i', 'a', Shift.PUNCT, ', ', 't', 'h', 'e',
            ' ', 'f', 'r', 'e', 'e', ' ', 'e', 'n', 'c', 'y', 'c', 'l', 'o', 'p', 'e', 'd', 'i', 'a'))
        self.assertEqual(find_optimal_sequence('Code 2D!'), b(
            'C', Latch.LOWER, 'o', 'd', 'e', Latch.DIGIT, ' ', '2', Shift.UPPER, 'D', Shift.PUNCT, '!'))
        self.assertEqual(find_optimal_sequence('!#$%&?'), b(Latch.MIXED, Latch.PUNCT, '!', '#', '$', '%', '&', '?'))

        self.assertIn(find_optimal_sequence('. : '), (
            b(Shift.PUNCT, '. ', Shift.PUNCT, ': '),
            b(Latch.MIXED, Latch.PUNCT, '. ', ': ') ))
        self.assertEqual(find_optimal_sequence('\r\n\r\n\r\n'), b(Latch.MIXED, Latch.PUNCT, '\r\n', '\r\n', '\r\n'))
        self.assertEqual(find_optimal_sequence('Code 2D!'), b(
            'C', Latch.LOWER, 'o', 'd', 'e', Latch.DIGIT, ' ', '2', Shift.UPPER, 'D', Shift.PUNCT, '!'))
        self.assertEqual(find_optimal_sequence('test 1!test 2!'), b(
            Latch.LOWER, 't', 'e', 's', 't', Latch.DIGIT, ' ', '1', Shift.PUNCT, '!', Latch.UPPER,
            Latch.LOWER, 't', 'e', 's', 't', Latch.DIGIT, ' ', '2', Shift.PUNCT, '!'))
        self.assertEqual(find_optimal_sequence('Abc-123X!Abc-123X!'), b(
            'A', Latch.LOWER, 'b', 'c', Latch.DIGIT, Shift.PUNCT, '-', '1', '2', '3', Latch.UPPER, 'X', Shift.PUNCT, '!',
            'A', Latch.LOWER, 'b', 'c', Latch.DIGIT, Shift.PUNCT, '-', '1', '2', '3', Shift.UPPER, 'X', Shift.PUNCT, '!'))
        self.assertEqual(find_optimal_sequence('ABCabc1a2b3e'), b(
            'A', 'B', 'C', Latch.LOWER, 'a', 'b', 'c', Shift.BINARY, 5, '1', 'a', '2', 'b', '3', 'e'))
        self.assertEqual(find_optimal_sequence('ABCabc1a2b3eBC'), b(
            'A', 'B', 'C', Latch.LOWER, 'a', 'b', 'c', Shift.BINARY, 6, '1', 'a', '2', 'b', '3', 'e', Latch.MIXED, Latch.UPPER, 'B', 'C'))
        self.assertEqual(find_optimal_sequence('0a|5Tf.l'), b(
            Shift.BINARY, 5, '0', 'a', '|', '5', 'T', Latch.LOWER, 'f', Shift.PUNCT, '.', 'l'))
        self.assertEqual(find_optimal_sequence('*V1\x0c {Pa'), b(
            Shift.PUNCT, '*', 'V', Shift.BINARY, 5, '1', '\x0c', ' ', '{', 'P', Latch.LOWER, 'a'))
        self.assertEqual(find_optimal_sequence('~Fxlb"I4'), b(
            Shift.BINARY, 7, '~', 'F', 'x', 'l', 'b', '"', 'I', Latch.DIGIT, '4'))
        self.assertEqual(find_optimal_sequence('\\+=R?1'), b(
            Latch.MIXED, '\\', Latch.PUNCT, '+', '=', Latch.UPPER, 'R', Latch.DIGIT, Shift.PUNCT, '?', '1'))
        self.assertEqual(find_optimal_sequence('0123456789:;<=>'), b(
            Latch.DIGIT, '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', Latch.UPPER, Latch.MIXED, Latch.PUNCT, ':', ';', '<', '=', '>'))

    def test_encodings_canonical(self):
        for encoding in encoding_to_eci:
            self.assertEqual(encoding, codecs.lookup(encoding).name)

    def _optimal_eci_sequence(self, charset):
        eci = encoding_to_eci[charset]
        ecis = str(eci)
        return [ Shift.PUNCT, Misc.FLG, len(ecis), eci ]

    def test_find_optimal_sequence_non_ASCII_strings(self):
        """ Test find_optimal_sequence function for non-ASCII strings (currently only iso-8859-1) """

        # Implicit iso8559-1 without ECI:
        self.assertEqual(find_optimal_sequence('Français'), b(
            'F', Latch.LOWER, 'r', 'a', 'n', Shift.BINARY, 1, 0xe7, 'a', 'i', 's'))

        # ECI: explicit iso8859-1, cp1252 (Windows-1252), and utf-8
        self.assertEqual(find_optimal_sequence('Français', 'iso8859-1'), self._optimal_eci_sequence('iso8859-1') + b(
            'F', Latch.LOWER, 'r', 'a', 'n', Shift.BINARY, 1, 0xe7, 'a', 'i', 's'))
        self.assertEqual(find_optimal_sequence('€800', 'cp1252'), self._optimal_eci_sequence('cp1252') + b(
            Shift.BINARY, 1, 0x80, Latch.DIGIT, '8', '0', '0'))
        self.assertEqual(find_optimal_sequence('Français', 'utf-8'), self._optimal_eci_sequence('utf-8') + b(
            'F', Latch.LOWER, 'r', 'a', 'n', Shift.BINARY, 2, 0xc3, 0xa7, 'a', 'i', 's'))

    def test_find_optimal_sequence_bytes(self):
        """ Test find_optimal_sequence function for byte strings """

        self.assertEqual(find_optimal_sequence(b'a' + b'\xff' * 31 + b'A'), b(
            Shift.BINARY, 0, 1, 'a') + [0xff] * 31 + b('A'))
        self.assertEqual(find_optimal_sequence(b'abc' + b'\xff' * 32 + b'A'), b(
            Latch.LOWER, 'a', 'b', 'c', Shift.BINARY, 0, 1) + [0xff] * 32 + b(Latch.MIXED, Latch.UPPER, 'A'))
        self.assertEqual(find_optimal_sequence(b'abc' + b'\xff' * 31 + b'@\\\\'), b(
            Latch.LOWER, 'a', 'b', 'c', Shift.BINARY, 31) + [0xff] * 31 + b(Latch.MIXED, '@', '\\', '\\'))
        self.assertEqual(find_optimal_sequence(b'!#$%&?\xff'), b(
            Latch.MIXED, Latch.PUNCT, '!', '#', '$', '%', '&', '?', Latch.UPPER, Shift.BINARY, 1, '\xff'))
        self.assertEqual(find_optimal_sequence(b'!#$%&\xff'), b(Shift.BINARY, 6, '!', '#', '$', '%', '&', '\xff'))
        self.assertEqual(find_optimal_sequence(b'@\xff'), b(Shift.BINARY, 2, '@', '\xff'))
        self.assertEqual(find_optimal_sequence(b'. @\xff'), b(Shift.PUNCT, '. ', Shift.BINARY, 2, '@', '\xff'))

    def test_optimal_sequence_to_bits(self):
        """ Test optimal_sequence_to_bits function """
        self.assertEqual(optimal_sequence_to_bits(b()), '')
        self.assertEqual(optimal_sequence_to_bits(b(Shift.PUNCT)), '00000')
        self.assertEqual(optimal_sequence_to_bits(b('A')), '00010')
        self.assertEqual(optimal_sequence_to_bits(b(Shift.BINARY, 1, '\xff')), '111110000111111111')
        self.assertEqual(optimal_sequence_to_bits(b(Shift.BINARY, 0, 1) + [0xff] * 32), '111110000000000000001' + '11111111'*32)
        self.assertEqual(optimal_sequence_to_bits(b('A')), '00010')
        self.assertEqual(optimal_sequence_to_bits(b(Shift.PUNCT, Misc.FLG, 0, 'A')), '000000000000000010')
        self.assertEqual(optimal_sequence_to_bits(b(Shift.PUNCT, Misc.FLG, 1, 3, 'A')), '0000000000001' + '0101' + '00010') # FLG(1) '3'
        self.assertEqual(optimal_sequence_to_bits(b(Shift.PUNCT, Misc.FLG, 6, 3, 'A')), '0000000000110' + '0010'*5 + '0101' + '00010') # FLG(6) '000003'

    def test_get_data_codewords(self):
        """ Test get_data_codewords function """
        self.assertEqual(get_data_codewords('000010', 6), [0b000010])
        self.assertEqual(get_data_codewords('111100', 6), [0b111100])
        self.assertEqual(get_data_codewords('111110', 6), [0b111110, 0b011111])
        self.assertEqual(get_data_codewords('000000', 6), [0b000001, 0b011111])
        self.assertEqual(get_data_codewords('111111', 6), [0b111110, 0b111110])
        self.assertEqual(get_data_codewords('111101111101', 6), [0b111101, 0b111101])

    def _encode_and_decode(self, reader, data, *args, **kwargs):
        with NamedTemporaryFile(suffix='.png') as f:
            code = AztecCode(data, *args, **kwargs)
            code.save(f, module_size=5)
            result = reader.decode(f.name, **(dict(encoding=None) if isinstance(data, bytes) else {}))
            assert result is not None
            self.assertEqual(data, result.raw)

    @unittest.skipUnless(zxing, reason='Python module zxing cannot be imported; cannot test decoding.')
    def test_barcode_readability(self):
        r = zxing.BarCodeReader()
        # FIXME: ZXing command-line runner tries to coerce everything to UTF-8, so we can only reliably
        # encode and decode characters in the intersection of utf-8 and iso8559-1.
        self._encode_and_decode(r, 'Wikipedia, the free encyclopedia', ec_percent=0)
        self._encode_and_decode(r, 'Wow. Much error. Very correction. Amaze', ec_percent=95)
        self._encode_and_decode(r, '¿Cuánto cuesta?')

        # FIXME: Released versions of ZXing don't correctly decode ECI or FNC1 in Aztec (https://github.com/zxing/zxing/issues/1327),
        # so we don't currently have a way to test readability of barcodes containing characters not in iso8559-1.
        #
        # Uncomment once https://github.com/zxing/zxing/pull/1328 is merged:
        #self._encode_and_decode(r, 'The price is €4', encoding='utf-8')


if __name__ == '__main__':
    unittest.main(verbosity=2)
