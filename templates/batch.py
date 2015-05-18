    """
    batch.py - batch process for geospatial rasters, to calculate
    Normalised Difference Vegetation Index (NDVI) for all scenes in directory

    Part of the PyRaster suite https://github.com/talltom/PyRaster

    Each NDVI scene is written out to a new file.

    To run, do:

    python batch.py
    """
#Import standard modules and rasterio
import sys
import os
import string
import pytaster

rio = pyraster.RasterIO()

#Create a loop for all files in current directory
for file in flist:
    # Check file type (in this case Geotiff)
    if file.endswith('.tif'):
    # Open a pointer to the file
        pointer = rio.open(file)
        # Read the raster metadata for the new output file
        metadata = rio.read_metadata(pointer)
        # Read the first band to a matrix called band_1
        band_1 = rio.read_band(pointer, 1)
        # Read the second band to a matrix called band_2
        band_2 = rio.read_band(pointer, 2)
        # Perform the NDVI calculation and put the results into a new matrix
        new_ndvi_band = ((band_2 - band_1) / (band_2 + band_1))
        # Get the input filename without extension and create a new file name
        parts = string.split(file)
        newname = './'+parts[0]+'_ndvi.tif'  # ./filename_ndvi.tif
        # Get the EPSG code from well known text projection
        epsg = rio.wkt_to_epsg(metadata['projection'])
        # Write the NDVI matrix to a new raster file
        rio.writerasterband(new_ndvi_band, newname, metadata['xsize'],
                            metadata['ysize'], metadata['geotranslation'],
                            epsg)
# loop will now go to next file in input list
