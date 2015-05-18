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
import pyraster

rio = pyraster.RasterIO()
file_list = os.listdir(os.getcwd())

#Create a loop for all files in current directory
for file in file_list:
    # Check file type (in this case Geotiff)
    if file.endswith('.tif'):
    # Open a dataset to the file
        dataset = rio.open(file)
        # Read the raster metadata for the new output file
        metadata = rio.read_metadata(dataset)
        # Read the first band to a matrix called band_1
        band_1 = rio.read_band(dataset, 1)
        # Read the second band to a matrix called band_2
        band_2 = rio.read_band(dataset, 2)
        # Perform the NDVI calculation and put the results into a new matrix
        new_ndvi_band = ((band_2 - band_1) / (band_2 + band_1))
        # Get the input filename without extension and create a new file name
        parts = string.split(file)
        newname = './'+parts[0]+'_ndvi.tif'  # ./filename_ndvi.tif
        # Get the EPSG code from well known text projection
        epsg = rio.wkt_to_epsg(metadata['projection'])
        # Write the NDVI matrix to a new raster file
        rio.write_bands(newname, 'GTiff', metadata['xsize'],
                            metadata['ysize'], metadata['geotranslation'],
                            epsg, None, new_ndvi_band)
# loop will now go to next file in input list
