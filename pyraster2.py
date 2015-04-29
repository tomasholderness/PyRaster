#pyraster dev-2.0

import os
import sys
import struct
import numpy as np
import numpy.ma as ma
import osgeo.gdal as gdal
import osgeo.osr as osr
from osgeo.gdalconst import GA_ReadOnly

class RasterIO:
    '''class docstring'''

    def __init__(self):

        #Data type dictionaries - references from GDT's to other Python types.
        #GDT -> Numpy
        self.gdt2npy = {
            1: 'uint8',
            2: 'uint16',
            3: 'int16',
            4: 'uint32',
            5: 'int32',
            6: 'float32',
            7: 'float64'
        }
        #Numpy -> GDT
        self.npy2gdt = {
            'uint8': 1,
            'uint16': 2,
            'int16': 3,
            'uint32': 4,
            'int32': 5,
            'float32': 6,
            'float64': 7
        }

        #GDT -> Struct
        self.gdt2struct = {
            1: 'B',
            2: 'H',
            3: 'h',
            4: 'I',
            5: 'i',
            6: 'f',
            7: 'd'
        }

    def open(self, file_name):
        '''Accepts gdal compatible file on disk and returns gdal pointer.'''

        dataset = gdal.Open(file_name, GA_ReadOnly)
        #check if something returned
        if dataset is not None:
            return dataset
        else:
            raise IOError

    def read_metadata(self, dataset):
        '''Accepts GDAL dataset, returns metadata dict {gdal_driver, XSize, YSize,
        num_bands, projection, geotranslation}

        Variables for geotranslation metadata are as follows:
        geotransform[0] = top left x
        geotransform[1] = w-e pixel resolution
        geotransform[2] = rotation, 0 if image is "north up"
        geotransform[3] = top left y
        geotransform[4] = rotation, 0 if image is "north up"
        geotransform[5] = n-s picel resolution
        '''
        #get GDAL driver
        driver_short = dataset.GetDriver().ShortName
        driver_long = dataset.GetDriver().LongName
        #get projection
        proj_wkt = dataset.GetProjection()
        #get geotransforamtion parameters
        geotransform = dataset.GetGeoTransform()
        #number of rows and columns of data
        xsize = dataset.RasterXSize
        ysize = dataset.RasterYSize
        #number of bands is useful
        nbands = dataset.RasterCount
        # return values as dictionary
        return {'driver': driver_short,
                'xsize': xsize,
                'ysize': ysize,
                'num_bands': nbands,
                'projection': proj_wkt,
                'geotranslation': geotransform
                }

    def mask_band(s):
        #helper function to mask an array based on a particular value
        #here...
        pass

        """
        #check if data type int or float using dictionary for numeric test
        if npy2gdt[datarray.dtype.name] <= 5:
            #data is integer use masked_equal
            #apply NoDataValue masking.
            dataraster = ma.masked_equal(datarray, NoDataVal, copy=False)
            #apply invalid data masking
            dataraster = ma.masked_invalid(dataraster, copy=False)
            return dataraster
        else:
            #data is float use masked_values
            dataraster = ma.masked_values(datarray, NoDataVal, copy=False)
            #finaly apply mask for NaN values
            dataraster = ma.masked_invalid(dataraster, copy=False)
            #return array (raster)
            return dataraster
        """

    #function to read a band from data and apply NoDataValue masking
    def read_band(self, dataset, band_num, NoDataVal=None, masked=True):
        '''Accepts GDAL raster dataset and band number, returns Numpy 2D-array
        representing pixel values'''

        if dataset.RasterCount >= band_num:
            #Get one band
            band = dataset.GetRasterBand(aband)
            #test for user specified input NoDataValue
            if NoDataVal is None:
                #test for band specified NoDataValue
                if band.GetNoDataValue() is not None:
                    NoDataVal = band.GetNoDataValue()
                #	print NoData
                else:
                    #else set NoDataValue to be 9999.
                    NoDataVal = 9999
            #set NoDataVal for the band (good practice if we call the band later)
            band.SetNoDataValue(NoDataVal)
            #create blank array to hold data [note Y,X format]
            #get data type from dictionary
            datarray = np.zeros((band.YSize, band.XSize), gdt2npy[band.DataType])
            #create loop based on YAxis (i.e. num rows)
            for i in range(band.YSize):
                #read lines of band
                scanline = band.ReadRaster(0, i, band.XSize, 1, band.XSize, 1,
                                           band.DataType)
                #unpack from binary representation
                tuple_of_vals = struct.unpack(gdt2struct[band.DataType]
                                              * band.XSize,
                                              scanline)
                #tuple_of_floats = struct.unpack('f' * band.XSize, scanline)
                #add tuple to image array line by line
                datarray[i, :] = tuple_of_vals

            #check if masked=True
            if masked is True:
                return mask_band(datarray)
            else:
                #user wants numpy array, no masking.
                return datarray
        else:
            raise ValueError("read_band: Band number exceeeds number of bands "
                            +"available in dataset")
