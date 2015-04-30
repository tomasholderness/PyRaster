# rasterio module init script
"""
rasterIO -  Library of functions to convert geospatial raster formats to/from Numpy masked arrays.

B{Introduction}

This library contains wrapper functions for GDAL Python bindings, converting data to Numerical Python
multi-dimensional array's in memory for processing. Subsequent generated arrays can be written to disk
in the standard geospatial GeoTiff format.

B{Notes}

   - Error checking - rasterIO contains minimal user-level error checking

B{Supported Formats}

   - Input:
      - rasterIO supports reading any GDAL supported raster format

   - Output:
            - rasterIO generates GeoTiff files by default (this can be modified in the source code)
            - GeoTiffs are created with embedded binary header files containing geo information

B{Supported Datatypes}

   - Raster IO supports Float32 and Int16 data types
   - The default datatype is Float32
   - Boolean datasets use Int16 datatypes

B{NoDataValue}

If the input data has no recognisable NoDataValue (readable by GDAL) then the input NoDataValue
is assumed to be 9999. This can be changed by manually specifying an input NoDataVal when calling readrasterbands()
In accordance with GDAL the output data NoDataValue is 9999 or 9999.0 or can be manually set by when writrasterbands()
When using unsigned integer data types the default output NoDataValue will be 0

B{How to use documentation}

Documentation for module functions is provided as Python docstrings, accessible from an interactive Python terminal
Within docstrings examples from an interactive Python console are identified using '>>>'
Further information is given to developers within the source code using '#' comment strings
To view this text and a list of available functions call the Python in-built help command, specifying module name


	>>> import rasterIO
	>>> help(rasterIO)
	...this text...

For help on a specific function call the Python in-built help command, specifying module.function

	>>> import rasterIO
	>>> help(rasterIO.wkt2epsg)
	Help on function wkt2epsg in module rasterIO
	wkt2epsg(wkt)
	Accepts well known text of Projection/Coordinate
	Reference System and generates EPSG code

B{How to access functions}

To access functions, import the module to Python and call the desired function, assigning the output to a named variable.
Note that the primary input datatype (default) for all functions is either a Numpy array or a Numpy masked array.
Use the rasterIO module to convert Numpy arrays to/from Geospatial raster data formats, for example to read a raster:

	>>> import rasterIO as rio
	>>> pointer = rio.opengdalraster('file.tif')
	>>> band_number = 1
	>>> b1_data = rio.readrasterband(pointer, band_number)

Optional function arguments are shown in document strings in brackets [argument]

B{Dependencies}

Python 2.5 or greater
Numerical python (Numpy) 1.2.1 or greater (1.4.1 recommended)
	- Note that due to bugs in Numpy.ma module, Numpy 1.4.1 or greater is required to support masked arrays of integer values
		* See comments in reasrasterband() for more information

B{License & Authors}

Copyright: Tomas Holderness & Newcastle University\n
Released under the Simplified BSD License (see license.txt)
"""
__version__ = "1.1.2" # module version

# import rasterio submodule
from rasterio import *
