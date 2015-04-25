PyRaster
========
###Python Geospatial Image Processing

The RasterIO module uses the Geospatial Data Abstraction Library (GDAL)[http://gdal.org] to read and write images and their geospatial metadata to and from NumPy arrays. The aim of the software is to provide an interface for processing large suites of geospatial raster data, such satellite imagery.

The utility scripts use RasterIO to provide a series of functions for batch processing remote sensing imagery, including vectorizing array operations and using the multiprocessing module.

This software was developed as part of my PhD thesis ([Holderness 2013](https://theses.ncl.ac.uk/dspace/handle/10443/1856)), and is used for the [Raster Processing Suite] (http://talltom.github.io/Raster-Processing-Suite/) QGIS plugin.

####Documentation
A PDF of API documentation for RasterIO can be found in the "doc" folder.

#####Supported Formats
* Input: Any [GDAL supported format](http://gdal.org/formats_list.html)
* Output: Default is GeoTiffs created with embedded binary header files containing geospatial information

* Default data-type: 32-bit float

#####NoData Value Handling
If the input data has no recognisable NoDataValue (readable by GDAL) then the input NoDataValue is assumed to be 9999. This can be changed by manually specifying an input NoDataVal when calling read- rasterbands() In accordance with GDAL the output data NoDataValue is 9999 or 9999.0 or can be manually set by when writrasterbands() When using unsigned integer data types the default output NoDataValue will be 0.

#####Dependencies
* Python 2.5 or later
* Numpy 1.4.1 or later

#####In-built help
Documentation for module functions is provided as Python docstrings, accessible from an interactive Python terminal. For example:

```
>>> import rasterIO
>>> help(rasterIO.wkt2epsg)
Help on function wkt2epsg in module rasterIO
wkt2epsg(wkt)
Accepts well known text of Projection/Coordinate Reference System and generates EPSG code
```

###Getting Started
####Reading a file
To read a raster file from disk and covert it to a NumPy array three RasterIO functions are required.

1. opengdalraster(file name)
Accepts a GDAL compatible file on disk and returns GDAL dataset.

2. readrasterband(dataset, band_number, NoDataVal=None, masked=True):
Accepts a GDAL raster dataset and band number, returns Numpy 2D-array.'''

3. readrastermeta(dataset):
Accepts GDAL raster dataset and returns the GDAL drive, number of rows, number of columns, number of bands, projection info (well known text), geotranslation metadata.'''

Figure 1 shows the process of loading a raster file into a NumPy array using RasterIO open and read functions. For example:

```
import rasterIO as rio
dataset = rio.opengdalraster('file.tif')
band_number = 1
b1_data = rio.readrasterband(dataset, band_number)
```

![Figure 1 - loading](https://duckduckgo.com/assets/badges/logo_square.64.png)
