PyRaster
========
###Python Geospatial Image Processing

[![Build Status](https://travis-ci.org/talltom/PyRaster.svg?branch=dev)](https://travis-ci.org/talltom/PyRaster)
[![Coverage Status](https://coveralls.io/repos/talltom/PyRaster/badge.svg?branch=dev)](https://coveralls.io/r/talltom/PyRaster?branch=dev)

##About
PyRaster provides two elements:

####1. PyRaster module (RasterIO Class)

  The aim of the module is to provide a high-level API for Python software to process large suites of geospatial rasters, with a particular focus on satellite imagery.

  The RasterIO class uses the Geospatial Data Abstraction Library (GDAL)<sup>[1](#1)</sup> to read and write images and their geospatial metadata to and from NumPy arrays.

####2. Templates

  The template scripts use RasterIO to demonstrate a series of functions for efficient batch processing of remote sensing imagery, including vectorizing array operations and using the multiprocessing module to parallelize computation.

###References
This software was developed as part of my PhD thesis to batch process large time series of Earth observation data.
* Holderness, T. (2013) <i>Quantifying the spatio-temporal temperature dynamics of Greater London using thermal Earth observation.</i> <sup>[2](#2)</sup>
* PyRaster presentation to Mars Space Flight Facility in 2010. <sup>[3](#3)</sup>
* Raster Processing Suite QGIS plugin. <sup>[4](#4)</sup>

###Documentation
* RasterIO API documentation in HTML format can be found in the `doc` folder
* Instructions on using the software are provided below in this `README.md` file

###Supported Formats
* Input: Any GDAL supported format <sup>[5](#5)</sup>
* Output: Default is GeoTiffs created with embedded binary header files containing geospatial information
* Default data-type is 32-bit float
* RasterIO handles mapping of GDAL (C) data-types to Python

###Dependencies
* Python 2.7
* Numpy 1.9
* OSgeo (GDAL) 1.11
* Matplotlib (optional)

###Installation
To install the RasterIO module do:
```bash
[pyraster]$ python setup.py install
```
Python, and the PyRaster scripts should now be able to find and load the module.

##Using the Software
###1 Getting Started with the RasterIO API
####1.1 Loading the module
```python
from pyraster import RasterIO

```

####1.2 In-built help
Documentation for module functions are provided as Python docstrings, accessible from an interactive Python terminal. For example:

```python
>>> from pyraster import RasterIO
>>> help(RasterIO().wkt_to_epsg)
Help on function wkt2epsg in module rasterIO
wkt2epsg(wkt)
Accepts well known text of Projection/Coordinate Reference System and generates EPSG code
```

####1.3 Reading a file
To read a raster file from disk and covert it to a NumPy array three RasterIO functions are required.

1. open(file name)

  Accepts a GDAL compatible file on disk and returns GDAL dataset.

2. read_band(dataset, band_number, NoDataVal=None, masked=True)

  Accepts a GDAL raster dataset and band number, returns Numpy 2D-array.

Figure 1 shows the process of loading a raster file into a NumPy array using the RasterIO open and read functions. For example:

```python
import pyraster
rio = pyraster.Raster()
dataset = rio.opengdalraster('file.tif')

band_number = 1
b1 = rio.readrasterband(dataset, band_number)

print type(b1)
<class 'numpy.ma.core.MaskedArray'>
```

![Figure 1 - loading raster data](https://raw.githubusercontent.com/talltom/PyRaster/dev/doc/diagrams/rasterIO_processing_flowline_read.jpg)
Figure 1. Loading Raster Data into a NumPy array using the PyRaster RasterIO module (Adapted from Holderness, T. 2013 <sup>[2](#2)</sup>).

####1.4 Metadata Handling
The `read_metadata()` method complements `read_band()`,  to read the geospatial raster meta-data from a raster file. The `read_metadata()` function accepts a GDAL raster dataset (i.e. from `open_raster`) and returns a dictionary containing the GDAL driver, number of rows, number of columns, number of bands, projection info (well known text), and geotranslation metadata.

Using `read_metadata()` with `read_band()` means that when a raster is loaded into a NumPy array the geospatial information can be retained through the Python processing flow-line, and written with output data if required.

For example, to find the GDAL drive for the input data:

```python
metadata = rio.read_metadata(dataset)
print metadata['driver']
GTIFF
```

####1.5 Masked Arrays & No Data Values
PyRaster uses NumPy masked arrays <sup>[6](#6)</sup> to handle no data values in raster images. When masking is in place, masked values are not included in array calculations.

No Data Values (`NoDataValue`) are derived from individual band metadata using the `band.GetNoDataValue()` GDAL function <sup>[7](#7)</sup>.
If the input raster has no recognisable `NoDataValue` readable by GDAL then the input `NoDataValue` is assumed to be 9999. This can be changed by manually specifying an input NoDataVal when calling `read_band()`.

In accordance with GDAL the output data NoDataValue is 9999 or 9999.0 or can be manually set by when write_bands(). Note that when using unsigned integer data types the default output NoDataValue will be 0.

####1.6 Writing Data
The `write_bands()` method is used to write NumPy arrays to geosaptial raster files. An output file is specified, along with a GDAL supported file type. Geospatial metadata parameters are the same as those generated by `read_metadata()` and so can be copied from an origional input file. The methods requires the following parameters:
- filename
- GDAL file type (e.g. 'GTIFF')
- xsize - number of array columns
- ysize - number of array rows
- geotranslation metadata
- EPGS project code
- number of bands
- No data value (optionaly None)
- NumPy array(s)

```python
rio.write_bands('newfile.tif', 'GTiff', metadata['xsize'], metadata['ysize'], metadata['geotranslation'], rio.wkt_to_epsg(metadata['projection']), 1, None, array)
```
Note that an EPSG value can be generated from the project WKT generated by read_metadata, using the `wkt_to_epsg()` method.

###2 Raster Processing
NumPy Elementwise Array Operations <sup>[8](#8)</sup>
```python
band_celsius = band_kelvin - 273.15  #convert all cell values from Kelvin to Celsius temperatures
```
```python
band_difference = band1 - band2 #compute elementwise difference for all cell values between two bands
```
NumPy Universal Functions <sup>[9](#9)</sup>
```python
print band.mean(), band.min(), band.max  #compute mean, min and max values from all cells in band
```

###3 Template Scripts
Notes for template scripts, found in `templates` folder.

#### 3.1 batch.py
This script calculates the Normalized Difference Vegetation Index (NDVI) using the first two bands of each image in the working directory.

NDVI is defined as a ratio between two bands, where band 1 is in the red visible wavelength and band 2 is near-infrared. <sup>[10](#10)</sup>

```python
import pyraster
rio = pyraster.Raster()
#open the dataset
dataset = rio.opengdalraster('file.tif')
#read the bands
b1 = rio.readrasterband(dataset, 1)
b2 = rio.readrasterband(dataset, 2)
ndvi = (b2-b1)/(b2+b1)
```

To run the script, do:
```bash
[pyraster]$ python scripts/batch-ndvi.py
```

batch-ndvi generates a new raster representing the NDVI values calculated. The suffix "-ndvi" is added to the output filename to distinguish it from the original file. The script is a simple example of iterating raster computation over a series of data.

####3.2 vectorize.py
Vectorized functions can improve NumPy performance. <sup>[11](#11)</sup> This script uses the vectorize process to create a Boolean output raster based on a threshold function.

```python
def value_test(a, b):
    if a <= b:
            return 1
        else:
            return 0
```
Once the function is vectorized, and a raster array can be passed in as an argument
```python
value_test_vect = numpy.vectorize(value_test)
new_array = value_test_vect(band1, some_value)
```

####3.3 multiprocess.py
The Python Multiprocessing module can be used to parallelize processing of multiple scenes. <sup>[12](#12)</sup> The multiprocess script demonstrates using two threads to simultaneously calculate NDVI for a list of raster images. The list of images to process is split into two, and each assigned to a separate processing thread.

```python
#Create two processes (add more depending on processor availability)
p1 = Process(target=processRun, args=(q, flist[:half_length]))
p2 = Process(target=processRun, args=(q, flist[half_length:]))
```

####3.4 historgram.py
This script demonstrates creation of a band histogram plotted using the Matplotlib library. <sup>[13](#13)</sup>
The array is first flattened, and then passed to the Matploblib `hist` method.

```python
# Flatten 2d-matrix
flat_raster = ma.compressed(raster_matrix)
# Plot histogram
ax.hist(flat_raster, 10, normed=0, histtype='bar',
        align=mid)
```

####3.5 plot.py
The Matplotlib library can also be used to plot arrays as images using the `imshow` method. <sup>[14](#14)</sup>

```python
import matplotlib.pyplt as plt
from matplotlib import cmap
import pyraster

#Read the data
rio = pyraster.Raster()
dataset = rio.open('file.tif')
band = rio.read_band(dataset,1)

#Plot on screen using Matploblib.
plt.imshow(band, cmap=cm.Greys_r, vmin=19, vmax=50)
plt.show()
```
![Figure 2 - landsat plot](https://raw.githubusercontent.com/talltom/PyRaster/dev/doc/diagrams/landsat_7_ETM+.png)
Figure 2. Landsat 7 ETM+ Pancromatic Scene of London Plotted using Matplotlib.

##Development
###Unit Tests

  The `test` folder contains simple unit testing for RasterIO using the unittest and mock modules:

  ```bash
  [pyraster]$ python test/rasterio_test.py
  ```
Unit tests are run by Travis-CI when code is pushed to github.

Coverage of tests can be generated by running:
```bash
[pyraster]$ coverage run --pylib --source=pyraster test/rasterio_test.py
```
###Release
- Update the CHANGELOG.md file with the newly released version, date, and a high-level overview of changes. Commit the change.
- Create a tag in git from the current head of master. The tag version should be the same as the version specified in the pyraster.py file - this is the release version.
- Update the version in the pyraster.py file and commit the change.
- Further development is now on the updated version number until the release process begins again.

###Documentation
API documentation for pyraster is created using pdoc, generate HTML files in the `doc` directory by doing
```bash
[pyraster]$ pdoc --html --html-dir=doc/ --overwrite pyraster.py
```
##Notes
<a name="1"></a>[1] Geospatial Data Abstraction Library http://gdal.org

<a name="2"></a>[2] Holderness, T. 2013 PhD Thesis http://hdl.handle.net/10443/1856

<a name="3"></a>[3] Holderness, T. 2010 PyRaster Presentation https://tomholderness.files.wordpress.com/2012/12/holderness_asu_pyraster_pres_handout.pdf

<a name="4"></a>[4] Raster Processing Suite QGIS Plugin http://talltom.github.io/Raster-Processing-Suite/

<a name="5"></a>[5] GDAL Format List http://www.gdal.org/formats_list.html

<a name="6"></a>[6] NumPy Arrays
http://docs.scipy.org/doc/numpy/reference/maskedarray.html

<a name="7"></a>[7] GDAL No Data Values (http://www.gdal.org/classGDALRasterBand.html#adcca51d230b5ac848c43f1896293fb50)

<a name="8"></a>[8] NumPy Elementwise Array Operations http://wiki.scipy.org/Tentative_NumPy_Tutorial#head-4c1d53fe504adc97baf27b65513b4b97586a4fc5

<a name="9"></a>[9] NumPy Universal Functions http://wiki.scipy.org/Tentative_NumPy_Tutorial#head-053463ac1c1df8d47f8723f470b62c4bd0d11f07

<a name="10"></a>[10] Normalised Difference Vegetation Index https://en.wikipedia.org/wiki/Normalized_Difference_Vegetation_Index

<a name="11"></a>[11] NumPy vectorize  http://docs.scipy.org/doc/numpy/reference/generated/numpy.vectorize.html

<a name="12"></a>[12] Python Multiprocessing module https://docs.python.org/2/library/multiprocessing.html

<a name="13"></a>[13] Plotting an image histogram with Matplotlib http://matplotlib.org/users/image_tutorial.html#examining-a-specific-data-range

<a name="14"></a>[14] Plotting an image with Matploblib http://matplotlib.org/users/image_tutorial.html#image-tutorial
