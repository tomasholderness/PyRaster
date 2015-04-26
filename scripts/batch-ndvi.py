"""
batch-ndvi.py - calculate NDVI for all rasters in directory. Part of the
PyRaster suite.

Calculate Normalised Differenc Vegetation Index (NDVI) using
the first two bands of all GeoTiffs within the current directory.

Each NDVI scene is written out to a new file.

To run, do:

python batch-ndvi.py
"""
#Import standard modules and rasterio
import sys
import os
import string
from pytaster import rasterio as rio

#Create a loop for all files in current directory
for file in flist:
    # Check file type (in this case Geotiff)
    if file.endswith('.tif'):
    # Open a pointer to the file
        pointer = rio.opengdalraster(file)
        # Read the raster metadata for the new output file
        metadata = rio.readrastermeta(pointer)
        # Read the first band to a matrix called band_1
        band_1 = rio.readrasterband(pointer, 1)
        # Read the second band to a matrix called band_2
        band_2 = rio.readrasterband(pointer, 2)
        # Perform the NDVI calculation and put the results into a new matrix
        new_ndvi_band = ((band_2 - band_1) / (band_2 + band_1))
        # Get the input filename without extension and create a new file name
        parts = string.split(file)
        newname = './'+parts[0]+'_ndvi.tif'  # ./filename_ndvi.tif
        # Get the EPSG code from well known text projection
        epsg = rio.wkt2epsg(proj_wkt)
        # Write the NDVI matrix to a new raster file
        rio.writerasterband(new_ndvi_band, newname, metadata['XSize'],
                            metadata['YSize'], metadata['geotranslation'],
                            epsg)
# loop will now go to next file in input list
