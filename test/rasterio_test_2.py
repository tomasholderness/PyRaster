"""Unit tests for rasterio"""
import sys
#from pyraster import rasterio as rio
import unittest
import pyraster2
from mock import MagicMock, patch
import osgeo

class open(unittest.TestCase):
    '''Test error catching of open method'''

    def testOpen(self):
        '''Test ability to parse file name'''

        def new_open(filename, GA_ReadOnly):
            return filename

        with patch('osgeo.gdal.Open', new_open):
            self.assertEquals('foo', pyraster2.RasterIO().open('foo'))

    def testIOError(self):
        '''Test ability to catch erroneous file name '''

        def null_open(self, file):
            return None

        with patch('osgeo.gdal.Open', null_open):
            self.assertRaises(IOError, pyraster2.RasterIO().open, 'foo')

class read_metadata(unittest.TestCase):
    '''Test values returned from RasterIO.read_metadata with mock dataset'''

    def setUp(self):
        '''Setup mock dataset'''
        self.dataset = MagicMock()
        self.dataset.GetDriver().ShortName = 'short name'
        self.dataset.GetDriver().LongName = 'long name'
        self.dataset.GetProjection = MagicMock(return_value='projection')
        self.dataset.GetGeoTransform = MagicMock(return_value='geotransformation')
        self.dataset.RasterXSize = 1
        self.dataset.RasterYSize = 1
        self.dataset.RasterCount = 1


    def testReturns(self):
        '''Test returned values against expected'''
        expected = {'driver': 'short name',
                'xsize': 1,
                'ysize': 1,
                'num_bands': 1,
                'projection': 'projection',
                'geotranslation': 'geotransformation'
                }

        self.assertDictEqual(expected,pyraster2.RasterIO().read_metadata(self.dataset))

class read_band(unittest.TestCase):

    def setUp(self):
        '''Setup mock dataset'''
        self.dataset = MagicMock()
        self.dataset.RasterCount = 1

    def testCheckNumBands(self):
        self.assertRaises(ValueError, pyraster2.RasterIO().read_band, self.dataset, 2)


        #pass
        # test error of passing band number greater than dataset
        # test no data value
        # test mask function here also


if __name__ == "__main__":
    unittest.main()
