"""
###Python Geospatial Image Processing

http://github.com/talltom/pyraster](http://github.com/talltom/pyraster

version 2.0"""
__version__ = "2.0.0"  # module version

import struct
import numpy as np
import numpy.ma as ma
import osgeo.gdal as gdal
import osgeo.osr as osr
from osgeo.gdalconst import GA_ReadOnly

class RasterIO:
    """A high-level API for Python software to process large suites of
    geospatial rasters, with a particular focus on satellite imagery.

      The RasterIO class uses the Geospatial Data Abstraction Library
      ([GDAL](http://gdal.org)) to read and write images and their geospatial
      metadata to and from NumPy arrays."""

    def __init__(self):
        """Create an instance of a RasterIO interface"""
        #Data type dictionaries - references from GDT's to other Python types.
        #GDT -> Numpy
        self.gdt_to_npy = {
            1: 'uint8',
            2: 'uint16',
            3: 'int16',
            4: 'uint32',
            5: 'int32',
            6: 'float32',
            7: 'float64'
        }
        '''Dictionary of GDAL to NumPy data type mappings'''

        #Numpy -> GDT
        self.npy_to_gdt = {
            'uint8': 1,
            'uint16': 2,
            'int16': 3,
            'uint32': 4,
            'int32': 5,
            'float32': 6,
            'float64': 7
        }
        '''Dictionary of NumPy to GDAL data type mappings'''


        #GDT -> Struct
        self.gdt_to_struct = {
            1: 'B',
            2: 'H',
            3: 'h',
            4: 'I',
            5: 'i',
            6: 'f',
            7: 'd'
        }
        '''Dictionary of GDAL to struct module data type mappings'''

    def open(self, file_name):
        """Accepts a GDAL compatible file on disk and returns GDAL dataset"""

        dataset = gdal.Open(file_name, GA_ReadOnly)
        #check if something returned
        if dataset is not None:
            return dataset
        else:
            raise IOError

    def read_metadata(self, dataset):
        """Accepts GDAL dataset, returns metadata dict
        {gdal_driver,
        xsize,
        ysize,
        num_bands,
        projection,
        geotranslation}

        Variables for geotranslation metadata are as follows:

        - geotransform[0] = top left x
        - geotransform[1] = west to east pixel resolution
        - geotransform[2] = rotation, 0 if image is "north up"
        - geotransform[3] = top left y
        - geotransform[4] = rotation, 0 if image is "north up"
        - geotransform[5] = north to south pixel resolution
        """
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

    def mask_band(self, array, NoDataVal):
        """Accepts NumPy array, mask value and returns masked array"""

        #check if data type int or float using dictionary for numeric test
        if self.npy_to_gdt[array.dtype.name] <= 5:
            #data is integer use masked_equal
            #apply NoDataValue masking.
            dataraster = ma.masked_equal(array, NoDataVal, copy=False)
            #apply invalid data masking
            dataraster = ma.masked_invalid(dataraster, copy=False)
            return dataraster
        else:
            #data is float use masked_values
            dataraster = ma.masked_values(array, NoDataVal, copy=False)
            #finaly apply mask for NaN values
            dataraster = ma.masked_invalid(dataraster, copy=False)
            #return array (raster)
            return dataraster

    #function to read a band from data and apply NoDataValue masking
    def read_band(self, dataset, band_num, NoDataVal=None, masked=True):
        """Accepts GDAL raster dataset and band number, returns Numpy 2D-array
        representing pixel values"""

        if dataset.RasterCount >= band_num:
            #Get one band
            band = dataset.GetRasterBand(band_num)
            #test for user specified input NoDataValue
            if NoDataVal is None:
                #test for band specified NoDataValue
                if band.GetNoDataValue() is not None:
                    NoDataVal = band.GetNoDataValue()
                else:
                    #else set NoDataValue to be 9999.
                    NoDataVal = 9999
            #set NoDataVal for the band (good practice if we call the band later)
            band.SetNoDataValue(NoDataVal)
            #create blank array to hold data [note Y,X format]
            #get data type from dictionary
            datarray = np.zeros((band.YSize, band.XSize), self.gdt_to_npy[band.DataType])
            #create loop based on YAxis (i.e. num rows)
            for i in range(band.YSize):
                #read lines of band
                scanline = band.ReadRaster(0, i, band.XSize, 1, band.XSize, 1,
                                           band.DataType)
                #unpack from binary representation
                tuple_of_vals = struct.unpack(self.gdt_to_struct[band.DataType]
                                              * band.XSize,
                                              scanline)
                #tuple_of_floats = struct.unpack('f' * band.XSize, scanline)
                #add tuple to image array line by line
                datarray[i, :] = tuple_of_vals

            #check if masked=True
            if masked is True:
                return self.mask_band(datarray, NoDataVal)
            else:
                #user wants numpy array, no masking.
                return datarray
        else:
            raise ValueError("read_band: Band number exceeeds number of bands "
                            +"available in dataset")

    #function to create new (empty) raster file on disk.
    def new_raster(self, outfile, format, xsize, ysize, geotranslation, epsg,
    num_bands, gdal_dtype):
        """Accepts file_path, format, X, Y, geotransformation, epsg,
        number_of_bands, gdal_datatype and returns gdal pointer to new file.

        This is a lower level function that allows users to control data output
        stream directly, use for specialist cases (e.g. varying band data types)
        or memory limited read-write situations.
        Note that users should not forget to close file once data output is
        complete (dataset = None)."""
        #get driver and driver properties
        driver = gdal.GetDriverByName(format)
        metadata = driver.GetMetadata()
        #check that specified driver has gdal create method and go create
        if gdal.DCAP_CREATE in metadata and metadata[gdal.DCAP_CREATE] == 'YES':
            #Create file
            dst_ds = driver.Create(outfile, xsize, ysize, num_bands, gdal_dtype)
            #define "srs" as a home for coordinate system parameters
            srs = osr.SpatialReference()
            #import the standard EPSG ProjCRS
            srs.ImportFromEPSG(epsg)
            #apply the geotransformation parameters
            dst_ds.SetGeoTransform(geotranslation)
            #export these features to embedded well Known Text in the GeoTiff
            dst_ds.SetProjection(srs.ExportToWkt())
            return dst_ds
        #catch error if no write method for format specified
        else:
            raise IOError('Specified format not writeable by GDAL')

    def new_band(self, dataset, array, band_num, NoDataVal=None):
        """Accepts a GDAL dataset, rasterarray, band number, [NoDataValue],
        and creates new band in file."""
        #first check whether array is masked
        if ma.isMaskedArray(array) is True:
            if NoDataVal is None:
                if npy_to_gdt[array[0].dtype.name] == 1:
                    NoDataVal = 0
                else:
                    NoDataVal = 9999
            dst_ds.GetRasterBand(band_num).SetNoDataValue(NoDataVal)
            #create a numpy view on the masked array
            output = np.array(array, copy=False)
            #check if maskedarray has valid mask and apply to numpy array using
            # binary indexing.
            if array.mask is not ma.nomask:
                output[array.mask] = NoDataVal
            #write out numpy array with masking
            dst_ds.GetRasterBand(band_num).WriteArray(output)
        else:
            #input array is numpy already, write array to band in file
            dst_ds.GetRasterBand(band_num).WriteArray(array)

    #create function to write GeoTiff raster from NumPy n-dimensional array
    def write_bands(self, outfile, format, xsize, ysize, geotranslation, epsg,
                         NoDataVal=None, *arrays):
        """ Accepts raster(s) in Numpy 2D-array, outputfile string, format and
        geotranslation metadata and writes to file on disk."""
        #get number of bands
        num_bands = len(arrays)
        #create new raster
        dst_ds = new_raster(outfile, format, xsize, ysize, geotranslation,
                            epsg, num_bands, npy_to_gdt[arrays[0].dtype.name])
        #add raster data from raster arrays
        band_num = 1  # band counter
        for band in arrays:
            new_band(dst_ds, band, band_num, NoDataVal)
            band_num += 1
        #close output and flush cache to disk
        dst_ds = None

    #function to get Authority (e.g. EPSG) code from well known text
    def wkt_to_epsg(self, wkt):
        """Accepts well known text of Projection/Coordinate Reference System and
        generates EPSG code."""
        if wkt is not None:
            if wkt == '':
                return 0
            else:
                srs = osr.SpatialReference(wkt)
                if (srs.IsProjected()):
                    return int(srs.GetAuthorityCode("PROJCS"))
                elif (srs.IsLocal()):
                    return 0
                else:
                    return int(srs.GetAuthorityCode("GEOGCS"))
        else:
            raise TypeError

    def band_to_txt(self, band, outfile):
        """Accepts numpy array writes to specified text file on disk."""
        if ma.isMaskedArray(band) is True:
            outraster = ma.compressed(band)
        else:
            outraster = band
        np.savetxt(outfile, outraster, fmt='%f')
