import unittest
import random

from .common import *
from dataclasses import dataclass


@dataclass
class CommonTest(unittest.TestCase):
    random_num = random.uniform(1, 100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.str_random_num = str(self.random_num)

    def test_convert_num_float(self):
        self.assertEqual(convert_num(self.str_random_num, float), self.random_num)

    def test_convert_num_str(self):
        self.assertEqual(convert_num(self.str_random_num, str), self.str_random_num)

    def test_convert_num_int(self):
        self.assertEqual(convert_num(self.str_random_num, int), int(self.random_num))

    def test_convert_num_wrong_data(self):
        self.assertEqual(convert_num("dasdsada"), "0")

    def test_random_key(self):
        random_length = random.randint(1, 100)
        self.assertEqual(len(random_key(random_length)), random_length)


if __name__ == "__main__":
    unittest.main()