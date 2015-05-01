PyRaster
========
###Python Geospatial Image Processing

[![Build Status](https://travis-ci.org/talltom/PyRaster.svg?branch=dev)](https://travis-ci.org/talltom/PyRaster)

##About
PyRaster provides two elements:

1. RasterIO module

  The aim of the module is to provide a high-level API for Python software to process large suites of geospatial rasters, with a particular focus on satellite imagery.

  The RasterIO module uses the Geospatial Data Abstraction Library ([GDAL](http://gdal.org)) to read and write images and their geospatial metadata to and from NumPy arrays.

2. Scripts

  The utility scripts use RasterIO to provide a series of functions for efficient batch processing of remote sensing imagery, including vectorizing array operations and using the multiprocessing module to parallelize computation.

###References
This software was developed as part of my PhD thesis to batch process large time series of Earth observation data.
* [PhD Thesis](http://hdl.handle.net/10443/1856) - Holderness, T. 2013
* [PyRaster presentation](https://tomholderness.files.wordpress.com/2012/12/holderness_asu_pyraster_pres_handout.pdf) to Mars Space Flight Facility in 2010
* [Raster Processing Suite](http://talltom.github.io/Raster-Processing-Suite/) QGIS plugin.

###Documentation
* A PDF of RasterIO API documentation can be found in the `doc` folder
* Instructions on using the software are provided below in this `README.md` file

###Supported Formats
* Input: Any [GDAL supported format](http://gdal.org/formats_list.html)
* Output: Default is GeoTiffs created with embedded binary header files containing geospatial information
* Default data-type is 32-bit float
* RasterIO handles mapping of GDAL (C) data-types to Python

###Dependencies
* Python 2.7
* Numpy 1.9
* OSgeo (GDAL) 1.11

###Installation
To install the RasterIO module do:
```bash
[pyraster]$ python install setup.py
```
The scripts should now be able to find and load the module.

###Sample Data
[To do] AVHRR scene.

##Using the Software
###1 Getting Started with the RasterIO API
####1.1 Loading the module
```python
from pyraster import rasterio

```

####1.2 In-built help
Documentation for module functions are provided as Python docstrings, accessible from an interactive Python terminal. For example:

```python
>>> from pyraster import rasterio
>>> help(rasterio.wkt2epsg)
Help on function wkt2epsg in module rasterIO
wkt2epsg(wkt)
Accepts well known text of Projection/Coordinate Reference System and generates EPSG code
```

####1.3 Reading a file
To read a raster file from disk and covert it to a NumPy array three RasterIO functions are required.

1. opengdalraster(file name)

  Accepts a GDAL compatible file on disk and returns GDAL dataset.

2. readrasterband(dataset, band_number, NoDataVal=None, masked=True)

  Accepts a GDAL raster dataset and band number, returns Numpy 2D-array.'''

3. readrastermeta(dataset)

  Accepts GDAL raster dataset and returns a dictionary containing the GDAL driver, number of rows, number of columns, number of bands, projection info (well known text), and geotranslation metadata.

Figure 1 shows the process of loading a raster file into a NumPy array using the RasterIO open and read functions. For example:

```python
from pyraster import rasterio as rio
dataset = rio.opengdalraster('file.tif')

band_number = 1
b1_data = rio.readrasterband(dataset, band_number)

print type(b1_data)
<class 'numpy.ma.core.MaskedArray'>
```

![Figure 1 - loading raster data](https://raw.githubusercontent.com/talltom/PyRaster/dev/doc/diagrams/rasterIO_processing_flowline_read.jpg)
Figure 1. Loading Raster Data into a NumPy array using the PyRaster RasterIO module ([Holderness, T. 2013](http://hdl.handle.net/10443/1856)).

####1.4 Metadata Handling
The `readrastermeta()` function complements `readrasterband()`,  to read the geospatial raster meta-data from a raster file.

Using `readrastermeta()` with `readrasterband()` means that when a raster is loaded into a NumPy array the geospatial information can be retained through the Python processing flow-line, and written with output data if required.

For example, to find the GDAL drive for the input data:

```python
metadata = rio.readrastermeta(dataset)
print metadata['driver']
GTIFF
```
#refer to API docs for geotranslation?

####1.5 Masked Arrays & No Data Values

PyRaster uses [NumPy masked arrays](http://docs.scipy.org/doc/numpy/reference/maskedarray.html) to handle no data values in raster images. When masking is in place, masked values are not included in array calculations.

No Data Values (`NoDataValue`) are derived from individual band metadata using the `band.GetNoDataValue()` [GDAL function](http://www.gdal.org/classGDALRasterBand.html#adcca51d230b5ac848c43f1896293fb50).
If the input raster has no recognisable `NoDataValue` readable by GDAL then the input `NoDataValue` is assumed to be 9999. This can be changed by manually specifying an input NoDataVal when calling read- rasterbands()

In accordance with GDAL the output data NoDataValue is 9999 or 9999.0 or can be manually set by when writrasterbands(). Note that when using unsigned integer data types the default output NoDataValue will be 0.


###2 Raster Processing with NumPy
####Simple Example

###3 Writing Data

###4 Scripts
#### batch-ndvi.py
This script calculates the Normalized Difference Vegetation Index (NDVI) using the first two bands of each image in the working directory.

NDVI is defined as a ratio between two bands, where band 1 is in the visible wavelengths and band 2 is near-infrared:

```python
ndvi = (b2-b1)/(b2+b1)
```
(see X ref for further information)

to run, do:
```bash
[pyraster]$ python scripts/batch-ndvi.py
```
Figure X - sample NDVI calculation

batch-ndvi generates a new raster representing the NDVI values calculated. The suffix "-ndvi" is added to the output filename to distinguish it from the original file. The script is a simple example of iterating raster computation over a series of data.

####vectorize.py
NumPy contains a number of methods to optimize array routines (see ref). This script uses the vectorize process to create a Boolean output raster based on a threshold function.

```python
def value_test(a, b):
    if a <= b:
            return 1
        else:
            return 0
```
Once the function is vectorized, and a raster array can be passed in as an argument
```
value_test_vect = numpy.vectorize(value_test)
new_array = value_test_vect(band1, some_value)
```

###Development
* Testing

  The `test` folder contains simple unit testing of rasterio error handling:

  ```bash
  [pyraster]$ python test/rasterio_test.py
  ```
Unit tests are run by Travis-CI when code is pushed to github.

* Style

  adheres to PEP 8, functions contain docstrings, documentation built with pdoc
