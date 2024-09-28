#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import unittest
from unittest.mock import patch, mock_open, MagicMock
from aztec_code_generator import (
    Mode,
    Latch,
    Shift,
    Misc,
    reed_solomon,
    find_optimal_sequence,
    optimal_sequence_to_bits,
    get_data_codewords,
    encoding_to_eci,
    SvgFactory,
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
            'A', 'B', 'C', Latch.LOWER, 'a', 'b', 'c', Shift.BINARY, 6, '1', 'a', '2', 'b', '3', 'e', Latch.DIGIT, Latch.UPPER, 'B', 'C'))
        self.assertEqual(find_optimal_sequence('abcABC'), b(
            Latch.LOWER, 'a', 'b', 'c', Latch.DIGIT, Latch.UPPER, 'A', 'B', 'C'))
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
        """ Test find_optimal_sequence function for non-ASCII strings"""

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
            Latch.LOWER, 'a', 'b', 'c', Shift.BINARY, 0, 1) + [0xff] * 32 + b(Latch.DIGIT, Latch.UPPER, 'A'))
        self.assertEqual(find_optimal_sequence(b'abc' + b'\xff' * 31 + b'@\\\\'), b(
            Latch.LOWER, 'a', 'b', 'c', Shift.BINARY, 31) + [0xff] * 31 + b(Latch.MIXED, '@', '\\', '\\'))
        self.assertEqual(find_optimal_sequence(b'!#$%&?\xff'), b(
            Latch.MIXED, Latch.PUNCT, '!', '#', '$', '%', '&', '?', Latch.UPPER, Shift.BINARY, 1, '\xff'))
        self.assertEqual(find_optimal_sequence(b'!#$%&\xff'), b(Shift.BINARY, 6, '!', '#', '$', '%', '&', '\xff'))
        self.assertEqual(find_optimal_sequence(b'@\xff'), b(Shift.BINARY, 2, '@', '\xff'))
        self.assertEqual(find_optimal_sequence(b'. @\xff'), b(Shift.PUNCT, '. ', Shift.BINARY, 2, '@', '\xff'))

    @unittest.expectedFailure
    def test_find_optimal_sequence_CRLF_bug(self):
        """ Demonstrate a known bug in find_optimal_sequence.

        This is a much more minimal example of https://github.com/delimitry/aztec_code_generator/issues/7

        The string '\t<\r\n':
          SHOULD be sequenced as:          Latch.MIXED '\t' < '\r' '\n'
          but is incorrectly sequenced as: Latch.MIXED '\t' < '\r\n'

        ... which is impossible since no encoding of the 2 byte sequence b'\r\n' exists in MIXED mode. """

        self.assertEqual(find_optimal_sequence(b'\t<\r\n'), b(
            Latch.MIXED, '\t', Shift.PUNCT, '<', '\r', '\n'
        ))

    def test_optimal_sequence_to_bits(self):
        """ Test optimal_sequence_to_bits function """
        self.assertEqual(optimal_sequence_to_bits(b()), '')
        self.assertEqual(optimal_sequence_to_bits(b(Shift.PUNCT)), '00000')
        self.assertEqual(optimal_sequence_to_bits(b('A')), '00010')
        self.assertEqual(optimal_sequence_to_bits(b(Shift.BINARY, 1, '\xff')), '111110000111111111')
        self.assertEqual(optimal_sequence_to_bits(b(Shift.BINARY, 0, 1) + [0xff] * 32), '111110000000000000001' + '11111111'*32)
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

        # FIXME: ZXing command-line runner tries to coerce everything to UTF-8, at least on Linux,
        # so we can only reliably encode and decode characters that are in the intersection of utf-8
        # and iso8559-1 (though with ZXing >=3.5, the iso8559-1 requirement is relaxed; see below).
        #
        # More discussion at: https://github.com/dlenski/python-zxing/issues/17#issuecomment-905728212
        # Proposed solution: https://github.com/dlenski/python-zxing/issues/19
        self._encode_and_decode(r, 'Wikipedia, the free encyclopedia', ec_percent=0)
        self._encode_and_decode(r, 'Wow. Much error. Very correction. Amaze', ec_percent=95)
        self._encode_and_decode(r, '¿Cuánto cuesta?')

    @unittest.skipUnless(zxing, reason='Python module zxing cannot be imported; cannot test decoding.')
    def test_barcode_readability_eci(self):
        r = zxing.BarCodeReader()

        # ZXing <=3.4.1 doesn't correctly decode ECI or FNC1 in Aztec (https://github.com/zxing/zxing/issues/1327),
        # so we don't have a way to test readability of barcodes containing characters not in iso8559-1.
        # ZXing 3.5.0 includes my contribution to decode Aztec codes with non-default charsets (https://github.com/zxing/zxing/pull/1328)
        if r.zxing_version_info < (3, 5):
            raise unittest.SkipTest("Running with ZXing v{}. In order to decode non-iso8859-1 charsets in Aztec Code, we need v3.5+".format(r.zxing_version))

        self._encode_and_decode(r, 'The price is €4', encoding='utf-8')
        self._encode_and_decode(r, 'אין לי מושג', encoding='iso8859-8')

class TestSvgFactory(unittest.TestCase):
    def test_init(self):
        data = '<svg><text>example svg data</text></svg>'
        instance = SvgFactory(data)
        self.assertEqual(instance.svg_str, data)
    
    @patch('builtins.open', new_callable=mock_open)
    def test_save(self, mock):
        data = '<svg></svg>'
        filename = 'example_filename.svg'
        instance = SvgFactory(data)
        mock.reset_mock()
        instance.save(filename)
        mock.assert_called_once_with(filename, "w")
        mock().write.assert_called_once_with(data)

    def test_save_with_provided_file_handler(self):
        data = '<svg></svg>'
        with NamedTemporaryFile(mode='w+') as fp:
            instance = SvgFactory(data)
            instance.save(fp)
            fp.flush()
            fp.seek(0)
            saved_content = fp.read()
            self.assertEqual(saved_content, data)

    def test_create_svg(self):
        CASES = [
            dict(
                matrix = [[1, 1, 1], [0 ,0 ,0 ], [1, 1, 1]],
                snapshot = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 5 5"><rect x="0" y="0" width="5" height="5" fill="white" /><path d="M1 1 h3 M1 3 h3 Z" stroke="black" stroke-width="1" transform="translate(0,0.5)" /></svg>',
            ),
            dict(
                matrix = [[1, 0, 0], [0, 1, 0], [0, 0 ,1]],
                snapshot = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 5 5"><rect x="0" y="0" width="5" height="5" fill="white" /><path d="M1 1 h1 M2 2 h1 M3 3 h1 Z" stroke="black" stroke-width="1" transform="translate(0,0.5)" /></svg>',
            ),
            dict(
                matrix = [[1, 0], [0, 1]],
                snapshot = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4 4"><rect x="0" y="0" width="4" height="4" fill="white" /><path d="M1 1 h1 M2 2 h1 Z" stroke="black" stroke-width="1" transform="translate(0,0.5)" /></svg>'
            ),
            dict(
                matrix = [[1, 0], [0, 1]],
                border = 3,
                snapshot = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8"><rect x="0" y="0" width="8" height="8" fill="white" /><path d="M3 3 h1 M4 4 h1 Z" stroke="black" stroke-width="1" transform="translate(0,0.5)" /></svg>'
            ),
            dict(
                matrix = [['#', ' '], [' ', '#']],
                matching_fn = lambda x: x == '#',
                snapshot = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4 4"><rect x="0" y="0" width="4" height="4" fill="white" /><path d="M1 1 h1 M2 2 h1 Z" stroke="black" stroke-width="1" transform="translate(0,0.5)" /></svg>'
            ),
        ]
        for case in CASES:
            if "border" in case:
                instance = SvgFactory.create_svg(case["matrix"], border=case["border"])
            elif "matching_fn" in case:
                instance = SvgFactory.create_svg(case["matrix"], matching_fn=case["matching_fn"])
            else:
                instance = SvgFactory.create_svg(case["matrix"])
            self.assertIsInstance(instance, SvgFactory)
            self.assertEqual(
                instance.svg_str,
                case["snapshot"],
                'should match snapshot'
            )

class TestAztecCode(unittest.TestCase):
    def test_save_should_use_PIL_if_not_SVG(self):
        aztec_code = AztecCode('example data')
        class Image:
            def save():
                pass
        image_mock = Image()
        image_mock.save = MagicMock()
        with patch.object(aztec_code, 'image', return_value=image_mock):
            # filename .png, format None
            aztec_code.save('image.png')
            image_mock.save.assert_called_once()
            image_mock.save.reset_mock()
            
            # filename .jpg, format None
            aztec_code.save('image.jpg')
            image_mock.save.assert_called_once()
            image_mock.save.reset_mock()

            # filename .svg, format 'PNG'
            aztec_code.save('image.svg', format='PNG')
            image_mock.save.assert_called_once()
        
    def test_save_should_support_SVG(self):
        """ Should call SvgFactory.save for SVG files """
        mock_svg_factory_save = MagicMock()
        SvgFactory.save = mock_svg_factory_save
        aztec_code = AztecCode('example data')

        # filename .svg, format None
        filename = 'file.svg'
        aztec_code.save(filename)
        mock_svg_factory_save.assert_called_once_with(filename)
        mock_svg_factory_save.reset_mock()

        # filename != .svg, format 'SVG'
        filename = 'file.png'
        aztec_code.save(filename, format='SVG')
        mock_svg_factory_save.assert_called_once_with(filename)
        mock_svg_factory_save.reset_mock()

        # filename is a file object, format 'svg'
        with NamedTemporaryFile() as fp:
            aztec_code.save(fp, format='svg')
            mock_svg_factory_save.assert_called_once_with(fp)


if __name__ == '__main__':
    unittest.main(verbosity=2)
