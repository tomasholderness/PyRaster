''' Library of Geospatial raster functions to convert OSGEO.GDAL formats to/from Numpy masked arrays.

rasterIO
========

This library contains wrapper functions for GDAL Python I/O bindings, converting data to Numerical Python 
multi-dimensional array's in memory for processing. Subsequent, generated array's can be written to disk
in the standard Geospatial GeoTiff format.

Notes
-----
	Error checking - rasterIO contains minimal user-level error checking.

Supported Formats
-----------------
	Input: rasterIO supports reading any GDAL supported raster format

	Output: rasterIO generates GeoTiff files by default (this can be modified in the code).
		GeoTiffs are created with embedded binary header files containing geo information

Supported Datatypes
-------------------
	Raster IO supports Float32 and Int16 data types.
	The default datatype is Float32. Boolean datasets use Int16 datatypes.
	
NoDataValue
-----------
	If the input data has no recognisable NoDataValue (readable by GDAL) then the input NoDataValue
	is assumed to be 9999. This can be changed by manually specifying an input NoDataVal when calling readrasterbands().
	In accordance with GDAL the output data NoDataValue is 9999 or 9999.0 or can be manually set by when writrasterbands().
	When using unsigned integer data types the default output NoDataValue will be 0.

How to use documentation
------------------------
Documentation for module functions is provided as Python docstrings, accessible from an interactive Python terminal.
Within docstrings examples from an interactive Python console are identified using '>>>'. 
Further information is given to developers within the source code using '#' comment strings.
To view this text and a list of available functions call the Python in-built help command, specifying module name.


	>>> import rasterIO
	>>> help(rasterIO)
	...this text...
	
For help on a specific function call the Python in-built help command, specifying module.function.

	>>> import rasterIO
	>>> help(rasterIO.wkt2epsg)
		
		Help on function wkt2epsg in module rasterIO:

	wkt2epsg(wkt)
    		Accepts well known text of Projection/Coordinate Reference System and generates
    		EPSG code
	(END) 

How to access functions
-----------------------
To access functions, import the module to Python and call the desired function, assigning the output to a named variable.
Note that the primary input datatype (default) for all functions is either a Numpy array or a Numpy masked array. 
Within this module the term "raster" is used to signify a Numpy/Numpy masked array of raster values.
Use the rasterIO module to convert Numpy arrays to/from Geospatial raster data formats.

	>>> import rasterIO
	>>> band_number = 1
	>>> rasterdata = rasterIO.readrasterband(gdal_file_pointer, band_number)

Optional function arguments are shown in document strings in brackets [argument].
	
Dependencies
------------
Python 2.5 or greater
Numerical python (Numpy) 1.2.1 or greater (1.4.1 recommended).
	- Note that due to bugs in Numpy.ma module, Numpy 1.4.1 or greater is required to support masked arrays of integer values. 
		* See comments in reasrasterband() for more information.

License & Authors
-----------------
Copyright: Tom Holderness
Released under the Simplified BSD License (see LICENSE.txt).
'''
__version__ = "1.1.1"
#!/usr/bin/env python
# raster.py - module of raster handling functions using GDAL and NUMPY

import os, sys, struct
import numpy as np
import numpy.ma as ma
import osgeo.osr as osr
import osgeo.gdal as gdal
from osgeo.gdalconst import *

# Data type dictionaries - references from GDT's to other Python types.
# GDT -> Numpy
gdt2npy	=	{
			1:'uint8',
			2:'uint16',
			3:'int16',
			4:'uint32',
			5:'int32',
			6:'float32',
			7:'float64'
		
		}	
# Numpy -> GDT
npy2gdt = 	{	
			'uint8':1,
			'uint16':2,
			'int16':3,
			'uint32':4,
			'int32':5,	
			'float32':6,
			'float64':7
			
		}
		
# GDT -> Struct
gdt2struct =	{	
			1:'B',
			2:'H',
			3:'h',
			4:'I',
			5:'i',
			6:'f',
			7:'d'
		}


# function to open GDAL raster dataset
def opengdalraster(fname):
	'''Accepts gdal compatible file on disk and returns gdal pointer.'''
	dataset = gdal.Open( fname, GA_ReadOnly)
	if dataset != None:
		return dataset
	else: 
		raise IOError
		
# function to read raster image metadata
def readrastermeta(dataset):
	'''Accepts GDAL raster dataset and returns, gdal_driver, XSize, YSize, projection info(well known text), geotranslation data.'''
		# get GDAL driver
	driver_short = dataset.GetDriver().ShortName
	driver_long = dataset.GetDriver().LongName
		# get projection	
	proj_wkt = dataset.GetProjection()
		# get geotransforamtion parameters
	geotransform = dataset.GetGeoTransform()
		# geotransform[0] = top left x
		# geotransform[1] = w-e pixel resolution
		# geotransform[2] = rotation, 0 if image is "north up"
		# geotransform[3] = top left y
		# geotransform[4] = rotation, 0 if image is "north up"
		# geotransform[5] = n-s picel resolution
	XSize = dataset.RasterXSize
	YSize = dataset.RasterYSize
	
	return driver_short, XSize, YSize, proj_wkt, geotransform

# function to read a band from a dat# apply NoDataValue masking.aset
def readrasterband(dataset, aband, NoDataVal=None, masked=True):
	'''Accepts GDAL raster dataset and band number, returns Numpy 2D-array.'''
	if dataset.RasterCount >= aband:		
		# Get one band
		band = dataset.GetRasterBand(aband)
		# test for user specified input NoDataValue
		if NoDataVal is None:
			# test for band specified NoDataValue
			if band.GetNoDataValue() != None:
				NoDataVal = band.GetNoDataValue()
			#	print NoData
			else:
				# else set NoDataValue to be 9999.
				NoDataVal = 9999
		# set NoDataVal for the band (not strictly needed, but good practice if we call the band later).		
		band.SetNoDataValue(NoDataVal)
		# create blank array (full of 0's) to hold extracted data [note Y,X format], get data type from dictionary.
		datarray = np.zeros( ( band.YSize,band.XSize ), gdt2npy[band.DataType] )
			# create loop based on YAxis (i.e. num rows)
		for i in range(band.YSize):
			# read lines of band	
			scanline = band.ReadRaster( 0, i, band.XSize, 1, band.XSize, 1, band.DataType)
			# unpack from binary representation
			tuple_of_vals = struct.unpack(gdt2struct[band.DataType] * band.XSize, scanline)
			# tuple_of_floats = struct.unpack('f' * band.XSize, scanline)
			# add tuple to image array line by line	
			datarray[i,:] = tuple_of_vals
		
		# check if masked=True
		if masked is True:
			# check if data type is int or float using dictionary for numeric test.
			if npy2gdt[datarray.dtype.name] <= 5:
				# data is integer use masked_equal
				# apply NoDataValue masking.
				dataraster = ma.masked_equal(datarray, NoDataVal, copy=False)
				# apply invalid data masking
				dataraster = ma.masked_invalid(dataraster, copy=False)
				return dataraster				
			else:
				# data is float use masked_values
				dataraster = ma.masked_values(datarray, NoDataVal, copy=False)
				# finaly apply mask for NaN values
				dataraster = ma.masked_invalid(dataraster, copy=False)
				# return array (raster)
				return dataraster
		else:
			# user wants numpy array, no masking.
			return datarray
	else:
		raise TypeError	

# function to create new (empty) raster file on disk.
def newgdalraster(outfile, format, XSize, YSize, geotrans, epsg, num_bands, gdal_dtype ):
	'''Accepts file_path, format, X, Y, geotransformation, epsg, number_of_bands, gdal_datatype and returns gdal pointer to new file.

	This is a lower level function that allows users to control data output stream directly, use for specialist cases such as varying band data types or memory limited read-write situations.
	Note that users should not forget to close file once data output is complete (dataset = None).'''
	# get driver and driver properties	
	driver = gdal.GetDriverByName( format )
	metadata  = driver.GetMetadata()
	# check that specified driver has gdal create method and go create	
	if metadata.has_key(gdal.DCAP_CREATE) and metadata[gdal.DCAP_CREATE] =='YES':	
		# Create file
		dst_ds = driver.Create( outfile, XSize, YSize, num_bands, gdal_dtype )
		# define "srs" as a home for coordinate system parameters
		srs = osr.SpatialReference()
		# import the standard EPSG ProjCRS
		srs.ImportFromEPSG( epsg )
		# apply the geotransformation parameters
		#print geotrans
		dst_ds.SetGeoTransform( geotrans )
		# export these features to embedded well Known Text in the GeoTiff
		dst_ds.SetProjection( srs.ExportToWkt() )
		return dst_ds
	# catch error if no write method for format specified
	else:
		#print 'Error, GDAL %s driver does not support Create() method.' % outformat
		raise TypeError

def newrasterband(dst_ds, rasterarray, band_num, NoDataVal=None):
	'''Accepts a GDAL dataset pointer, rasterarray, band number, [NoDataValue], and creates new band in file.'''
	# first check whether array is masked
	if ma.isMaskedArray(rasterarray) is True:
		if NoDataVal is None:
			if npy2gdt[rasterarray[0].dtype.name] == 1:
				NoDataVal = 0
			else:
				NoDataVal = 9999
		dst_ds.GetRasterBand(band_num).SetNoDataValue(NoDataVal)
		# create a numpy view on the masked array	
		output = np.array(rasterarray, copy=False)
		# check if maskedarray has valid mask and apply to numpy array using binary indexing.
		if rasterarray.mask is not ma.nomask:
			output[rasterarray.mask] = NoDataVal
		# write out numpy array with masking
		dst_ds.GetRasterBand(band_num).WriteArray ( output )	
	else:
	# input array is numpy already, write array to band in file
		dst_ds.GetRasterBand(band_num).WriteArray ( rasterarray )

# create function to write GeoTiff raster from NumPy n-dimensional array
def writerasterbands(outfile, format, XSize, YSize, geotrans, epsg, NoDataVal=None, *rasterarrays ):
	''' Accepts raster(s) in Numpy 2D-array, outputfile string, format and geotranslation metadata and writes to file on disk'''
	# get number of bands
	num_bands = len(rasterarrays)	
	# create new raster
	dst_ds = newgdalraster(outfile, format, XSize, YSize, geotrans, epsg, num_bands, npy2gdt[rasterarrays[0].dtype.name])
	# add raster data from raster arrays
	band_num = 1 # band counter
	for band in rasterarrays:
		newrasterband(dst_ds, band, band_num, NoDataVal)
		band_num += 1
	# close output and flush cache to disk
	dst_ds= None

# legacy function to write GeoTiff raster from NumPy n-dimensional array - use writerasterbands instead
def writerasterband(rasterarray, outfile, format, aXSize, aYSize, geotrans, epsg, NoDataVal=None):
	''' Legacy function for backwards compatability with older scripts. Use writerasterbands instead.

	Accepts raster in Numpy 2D-array, outputfile string, format and geotranslation metadata and writes to file on disk'''
	writerasterbands(outfile, format, aXSize, aYSize, geotrans, epsg, NoDataVal, rasterarray)
		
# function to get Authority (e.g. EPSG) code from well known text
def wkt2epsg(wkt):
	'''Accepts well known text of Projection/Coordinate Reference System and generates EPSG code'''
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
def band2txt(band, outfile):
	'''Accepts numpy rasterand writes to specified text file on disk.'''
	if ma.isMaskedArray(band) is True:
		outraster = ma.compressed(band)
	else:
		outraster = band
	np.savetxt(outfile, outraster, fmt='%f')	
	
		
	
		
