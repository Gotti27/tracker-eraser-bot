import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from bot import clean_url 

class TestURLCleaning(unittest.TestCase):

    def test_trivial(self):
        self.assertEqual(0, 0)
    
    def test_no_removal(self):
        url = 'https://www.example.com/path?safe=value&second=second_value#frag'
        self.assertEqual(url, clean_url(url))

    def test_front_removal(self):
        url = 'https://www.example.com/path?ref=value&second=second_value#frag'
        cleaned = 'https://www.example.com/path?second=second_value#frag'
        self.assertEqual(cleaned, clean_url(url))

    def test_mid_removal(self):
        url = 'https://www.example.com/path?first=foobar&ref=value&second=second_value#frag'
        cleaned = 'https://www.example.com/path?first=foobar&second=second_value#frag'
        self.assertEqual(cleaned, clean_url(url))
    
    def test_tail_removal(self):
        url = 'https://www.example.com/path?first=value&second=second_value&ref=tail#frag'
        cleaned = 'https://www.example.com/path?first=value&second=second_value#frag'
        self.assertEqual(cleaned, clean_url(url))

