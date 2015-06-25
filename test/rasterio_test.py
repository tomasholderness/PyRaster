"""Unit tests for pyraster.RasterIO module

reference: https://docs.python.org/3.3/library/unittest.html
"""

import sys
import struct
import unittest
import pyraster
from mock import MagicMock, patch
import osgeo
import numpy.ma as ma

class test_open(unittest.TestCase):
    '''Test error catching of open method'''

    def testOpen(self):
        '''Test ability to parse file name'''

        def new_open(filename, GA_ReadOnly):
            return filename

        with patch('osgeo.gdal.Open', new_open):
            self.assertEquals('foo', pyraster.RasterIO().open('foo'))

    def testIOError(self):
        '''Test ability to catch erroneous file name '''

        def null_open(self, file):
            return None

        with patch('osgeo.gdal.Open', null_open):
            self.assertRaises(IOError, pyraster.RasterIO().open, 'foo')

class test_read_metadata(unittest.TestCase):
    '''Test values returned from RasterIO.read_metadata with mock dataset'''

    def setUp(self):
        '''Setup mock dataset'''
        self.dataset = MagicMock()
        self.dataset.GetDriver().ShortName = 'short name'
        self.dataset.GetDriver().LongName = 'long name'
        self.dataset.GetProjection = MagicMock(return_value='projection')
        self.dataset.GetGeoTransform = MagicMock(
                                        return_value='geotransformation')
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

        self.assertDictEqual(expected,
                             pyraster.RasterIO().read_metadata(self.dataset))

class test_mask_band(unittest.TestCase):
    '''Test NumPy masking'''

    def testIntegerCheck(self):
        #setup mocked data
        self.datarray = MagicMock()
        self.datarray.dtype.name = 'int32'
        #setup mocked functions
        ma.masked_equal = MagicMock(return_value=1)
        ma.masked_invalid = MagicMock(return_value=2)
        #check correct value returned
        self.assertEqual(2, pyraster.RasterIO().mask_band(self.datarray, 9999))
        #check masked_equal called
        ma.masked_equal.assert_called_with(self.datarray, 9999, copy=False)
        #check masked_invalid called with output from masked_equal
        ma.masked_invalid.assert_called_with(1, copy=False)

class test_read_band(unittest.TestCase):
    '''Test read_band method'''

    def setUp(self):
        '''Setup mock dataset'''
        self.band = MagicMock()
        self.band.DataType = 1
        self.band.SetNoDataValue = MagicMock(return_value=1)

        self.dataset = MagicMock()
        self.dataset.RasterCount = 1
        self.dataset.GetRasterBand = MagicMock(return_value=self.band)

        struct.unpack = MagicMock(return_value=(1))

    def testCheckNumBands(self):
        self.assertRaises(ValueError, pyraster.RasterIO().read_band,
                          self.dataset, 2)

    def testSetNoDataValue(self):
        #test read with NoDataVal set
        pyraster.RasterIO().read_band(self.dataset, 1, NoDataVal=9991)
        self.band.SetNoDataValue.assert_called_with(9991)

        #test read with NoDataVal not set
        self.band.GetNoDataValue = MagicMock(return_value=None)
        pyraster.RasterIO().read_band(self.dataset, 1)
        self.band.SetNoDataValue.assert_called_with(9999)

        #test read with NoDataVal set in band
        self.band.GetNoDataValue = MagicMock(return_value=1234)
        pyraster.RasterIO().read_band(self.dataset, 1)
        self.band.SetNoDataValue.assert_called_with(1234)

    def testMaskedOutput(self):

        def null_mask(self, array, NoDataVal):
            return 0
        #test with mask flag
        with patch('pyraster.RasterIO.mask_band', null_mask):
            self.assertEqual(0, pyraster.RasterIO().read_band(self.dataset,
                                                              1,
                                                              masked=True))

        #test without mask flag
        self.assertEqual([[1]], pyraster.RasterIO().read_band(self.dataset,
                                                              1,
                                                              masked=False))

    def testFloatCheck(self):
        #setup mocked data
        self.datarray = MagicMock()
        self.datarray.dtype.name = 'float32'
        #setup mocked functions
        ma.masked_values = MagicMock(return_value=3)
        ma.masked_invalid = MagicMock(return_value=4)
        #check correct value returned
        self.assertEqual(4, pyraster.RasterIO().mask_band(self.datarray, 9999))
        #check masked_equal called
        ma.masked_values.assert_called_with(self.datarray, 9999, copy=False)
        #check masked_invalid called with output from masked_equal
        ma.masked_invalid.assert_called_with(3, copy=False)

class test_new_raster(unittest.TestCase):
    '''Test raster creation method'''

    def setUp(self):
        #input mocks
        self.outfile = MagicMock()
        self.format = MagicMock()
        self.xsize = MagicMock()
        self.ysize = MagicMock()
        self.geotranslation = MagicMock()
        self.epsg = 4326
        self.num_bands = MagicMock()
        self.gdal_dtype = MagicMock()
        #driver object mocks
        self.driver = MagicMock()

    def testCreateError(self):
        '''Test IOError raised if GDAL can't write to that datatype'''

        def null_metadata(format):
            return self.driver

        with patch('osgeo.gdal.GetDriverByName', null_metadata):
            self.assertRaises(IOError,
                              pyraster.RasterIO().new_raster,
                              self.outfile,
                              self.format,
                              self.xsize,
                              self.ysize,
                              self.geotranslation,
                              self.epsg,
                              self.num_bands,
                              self.gdal_dtype)

    def testMetadataCheck(self):
        '''Test metadata check and output creation'''

        def null_create(self, *args):
            #empty creation method
            ds = MagicMock(return_value=1)
            return ds

        with patch('osgeo._gdal.Driver_Create', null_create):
            #swap out creation method
            output = pyraster.RasterIO().new_raster(self.outfile,
                                                    'GTIFF',
                                                    self.xsize,
                                                    self.ysize,
                                                    self.geotranslation,
                                                    self.epsg,
                                                    self.num_bands,
                                                    self.gdal_dtype)
            #check that output matches expected (mocked) value
            self.assertEqual(1,output())

class test_wkt_to_epsg(unittest.TestCase):
    '''Test EPSG extraction from WKT projection string'''

    def testNoneInput(self):
        '''Test error handling of empty input'''

        self.assertRaises(ValueError, pyraster.RasterIO().wkt_to_epsg, None)

    def testNullInput(self):
        '''Test error handling of null input'''

        self.assertRaises(ValueError, pyraster.RasterIO().wkt_to_epsg, '')

    def testEPSGreturn(self):
        '''Test expected EPSG returned'''

        sample = 'PROJCS["WGS 84 / UTM zone 31N",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563,AUTHORITY["EPSG","7030"]],AUTHORITY["EPSG","6326"]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433],AUTHORITY["EPSG","4326"]],PROJECTION["Transverse_Mercator"],PARAMETER["latitude_of_origin",0],PARAMETER["central_meridian",3],PARAMETER["scale_factor",0.9996],PARAMETER["false_easting",500000],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AUTHORITY["EPSG","32631"]]'

        self.assertEquals(32631, pyraster.RasterIO().wkt_to_epsg(sample))

class test_band_to_text(unittest.TestCase):
    '''Test text output function'''

    def testNoMask(self):
        ''' Test method handles arrays with no mask'''

        self.val = 0

        def null_save(file, raster, fmt):
            self.val = 1

        with patch('numpy.savetxt', null_save):
            pyraster.RasterIO().band_to_txt(1, None)
            self.assertEqual(1, self.val)

class test_new_band(unittest.TestCase):
    '''Test creation of new band'''

    def setUp(self):
        '''Setup mock dataset'''
        self.dataset = MagicMock()
        self.array = ma.array([1, 2, 3], mask = [0, 1, 0], dtype='int32')
        self.band_num = 1
        self.object = MagicMock()

        ma.isMaskedArray = MagicMock(return_value=True)
        osgeo.gdal.Band.SetNoDataValue = MagicMock()

    def testMaskValue(self):
        '''Test correct mask value is applied if none supplied'''
        pyraster.RasterIO().new_band(self.dataset, self.array, self.band_num, NoDataVal=None)

        self.dataset.GetRasterBand.assert_called_with(1)
        self.dataset.GetRasterBand().SetNoDataValue.assert_called_with(9999)

class test_write_bands(unittest.TestCase):
    '''Testing write bands method'''

    def setUp(self):
        pyraster.RasterIO.new_raster= MagicMock()
        self.outfile = MagicMock(return_value='foo')
        self.format = MagicMock(return_value='a')
        self.xsize = MagicMock(return_value=100)
        self.ysize = MagicMock(return_value=100)
        self.geotranslation = MagicMock(return_value=1)
        self.epsg = MagicMock(return_value=2)
        self.nodata = MagicMock(return_value=678)
        #self.array = ma.array([1, 2, 3], mask = [0, 9999, 0], dtype='int32')
        #print self.array.mask
        self.array = MagicMock()
        self.array.dtype.name = 'int32'
        self.array.mask = [1]

    def testWriteBands(self):
        '''Test correct values are passed to new_raster method'''
        pyraster.RasterIO().write_bands(self.outfile, self.format, self.xsize, self.ysize, self.geotranslation, self.epsg, self.nodata, self.array)
        pyraster.RasterIO.new_raster.assert_called_with(self.outfile, self.format, self.xsize, self.ysize, self.geotranslation, self.epsg, 1, pyraster.RasterIO().npy_to_gdt['int32'])


if __name__ == "__main__":
    unittest.main()
