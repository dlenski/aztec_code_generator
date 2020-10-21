#!/usr/bin/env python
#-*- coding: utf-8 -*-

import unittest
from aztec_code_generator import (
    reed_solomon, find_optimal_sequence, optimal_sequence_to_bits, get_data_codewords,
    Mode, Latch, Shift,
)


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

    def test_find_optimal_sequence(self):
        """ Test find_optimal_sequence function """
        self.assertEqual(find_optimal_sequence(''), [])
        self.assertEqual(find_optimal_sequence('ABC'), ['A', 'B', 'C'])
        self.assertEqual(find_optimal_sequence('abc'), [Latch.LOWER, 'a', 'b', 'c'])
        self.assertEqual(find_optimal_sequence('Wikipedia, the free encyclopedia'), [
            'W', Latch.LOWER, 'i', 'k', 'i', 'p', 'e', 'd', 'i', 'a', Shift.PUNCT, ', ', 't', 'h', 'e',
            ' ', 'f', 'r', 'e', 'e', ' ', 'e', 'n', 'c', 'y', 'c', 'l', 'o', 'p', 'e', 'd', 'i', 'a'])
        self.assertEqual(find_optimal_sequence('Code 2D!'), [
            'C', Latch.LOWER, 'o', 'd', 'e', Latch.DIGIT, ' ', '2', Shift.UPPER, 'D', Shift.PUNCT, '!'])
        self.assertEqual(find_optimal_sequence('a\xff'), [Shift.BINARY, 2, 'a', '\xff'])
        self.assertEqual(find_optimal_sequence('a' + '\xff' * 30), [Shift.BINARY, 31, 'a'] + ['\xff'] * 30)
        self.assertEqual(find_optimal_sequence('a' + '\xff' * 31), [Shift.BINARY, 0, 1, 'a'] + ['\xff'] * 31)
        self.assertEqual(find_optimal_sequence('!#$%&?'), [Latch.MIXED, Latch.PUNCT, '!', '#', '$', '%', '&', '?'])
        self.assertEqual(find_optimal_sequence('!#$%&?\xff'), [
            Latch.MIXED, Latch.PUNCT, '!', '#', '$', '%', '&', '?', Latch.UPPER, Shift.BINARY, 1, '\xff'])
        self.assertEqual(find_optimal_sequence('!#$%&\xff'), [Shift.BINARY, 6, '!', '#', '$', '%', '&', '\xff'])
        self.assertEqual(find_optimal_sequence('@\xff'), [Shift.BINARY, 2, '@', '\xff'])
        self.assertEqual(find_optimal_sequence('. @\xff'), [Shift.PUNCT, '. ', Shift.BINARY, 2, '@', '\xff'])
        self.assertIn(find_optimal_sequence('. : '), [[Shift.PUNCT, '. ', Shift.PUNCT, ': '], [Latch.MIXED, Latch.PUNCT, '. ', ': ']])
        self.assertEqual(find_optimal_sequence('\r\n\r\n\r\n'), [Latch.MIXED, Latch.PUNCT, '\r\n', '\r\n', '\r\n'])
        self.assertEqual(find_optimal_sequence('Code 2D!'), [
            'C', Latch.LOWER, 'o', 'd', 'e', Latch.DIGIT, ' ', '2', Shift.UPPER, 'D', Shift.PUNCT, '!'])
        self.assertEqual(find_optimal_sequence('test 1!test 2!'), [
            Latch.LOWER, 't', 'e', 's', 't', Latch.DIGIT, ' ', '1', Shift.PUNCT, '!', Latch.UPPER,
            Latch.LOWER, 't', 'e', 's', 't', Latch.DIGIT, ' ', '2', Shift.PUNCT, '!'])
        self.assertEqual(find_optimal_sequence('Abc-123X!Abc-123X!'), [
            'A', Latch.LOWER, 'b', 'c', Latch.DIGIT, Shift.PUNCT, '-', '1', '2', '3', Latch.UPPER, 'X', Shift.PUNCT, '!',
            'A', Latch.LOWER, 'b', 'c', Latch.DIGIT, Shift.PUNCT, '-', '1', '2', '3', Shift.UPPER, 'X', Shift.PUNCT, '!'])
        self.assertEqual(find_optimal_sequence('ABCabc1a2b3e'), [
            'A', 'B', 'C', Latch.LOWER, 'a', 'b', 'c', Shift.BINARY, 5, '1', 'a', '2', 'b', '3', 'e'])
        self.assertEqual(find_optimal_sequence('ABCabc1a2b3eBC'), [
            'A', 'B', 'C', Latch.LOWER, 'a', 'b', 'c', Shift.BINARY, 6, '1', 'a', '2', 'b', '3', 'e', Latch.MIXED, Latch.UPPER, 'B', 'C'])
        self.assertEqual(find_optimal_sequence('0a|5Tf.l'), [
            Shift.BINARY, 5, '0', 'a', '|', '5', 'T', Latch.LOWER, 'f', Shift.PUNCT, '.', 'l'])
        self.assertEqual(find_optimal_sequence('*V1\x0c {Pa'), [
            Shift.PUNCT, '*', 'V', Shift.BINARY, 5, '1', '\x0c', ' ', '{', 'P', Latch.LOWER, 'a'])
        self.assertEqual(find_optimal_sequence('~Fxlb"I4'), [
            Shift.BINARY, 7, '~', 'F', 'x', 'l', 'b', '"', 'I', Latch.DIGIT, '4'])
        self.assertEqual(find_optimal_sequence('\\+=R?1'), [
            Latch.MIXED, '\\', Latch.PUNCT, '+', '=', Latch.UPPER, 'R', Latch.DIGIT, Shift.PUNCT, '?', '1'])

    def test_optimal_sequence_to_bits(self):
        """ Test optimal_sequence_to_bits function """
        self.assertEqual(optimal_sequence_to_bits([]), '')
        self.assertEqual(optimal_sequence_to_bits([Shift.PUNCT]), '00000')
        self.assertEqual(optimal_sequence_to_bits(['A']), '00010')
        self.assertEqual(optimal_sequence_to_bits([Shift.BINARY, 1, '\xff']), '111110000111111111')
        self.assertEqual(optimal_sequence_to_bits([Shift.BINARY, 0, 1, '\xff']), '11111000000000000000111111111')
        self.assertEqual(optimal_sequence_to_bits(['A']), '00010')

    def test_get_data_codewords(self):
        """ Test get_data_codewords function """
        self.assertEqual(get_data_codewords('000010', 6), [0b000010])
        self.assertEqual(get_data_codewords('111100', 6), [0b111100])
        self.assertEqual(get_data_codewords('111110', 6), [0b111110, 0b011111])
        self.assertEqual(get_data_codewords('000000', 6), [0b000001, 0b011111])
        self.assertEqual(get_data_codewords('111111', 6), [0b111110, 0b111110])
        self.assertEqual(get_data_codewords('111101111101', 6), [0b111101, 0b111101])


if __name__ == '__main__':
    unittest.main(verbosity=2)
