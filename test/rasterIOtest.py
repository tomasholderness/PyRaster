"""Unit tests for rasterIO.py"""
import sys
import rasterIO as rio
import unittest

class opengdalraster(unittest.TestCase):

    def testIOError(self):
        self.assertRaises(IOError, rio.opengdalraster, 'foo')

class wkt2epsg(unittest.TestCase):

    def testStringError(self):
        result = rio.wkt2epsg('')
        self.assertEqual(0, result)

    def testTypeError(self):
        self.assertRaises(TypeError, rio.wkt2epsg, 'foo')

if __name__ == "__main__":
    unittest.main()
