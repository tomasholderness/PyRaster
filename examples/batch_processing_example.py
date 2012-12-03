#!/usr/bin/env python
# Import standard modules and rasterIO
import sys, os, string, rasterIO

# Get a list of files in current directory
# Create a loop for all files in current directory

for file in flist:
	# Check file type (in this case Geotiff)    
	if file.endswith('.tif'):
        
	# Open a pointer to the file
	pointer = rasterIO.opengdalraster(file)
        
	# Read the raster metadata for the new output file
        driver, XSize, YSize, proj_wkt, geo_t_params = rasterIO.readrastermeta(pointer)
        
	# Read the first band to a matrix called band_1
        band_1 =rasterIO.readrasterband(pointer, 1)
        
	# Read the second band to a matrix called band_2
        band_2 = rasterIO.readrasterband(pointer, 2)
        
	# Perform the NDVI calculation and put the results into a new matrix
        new_ndvi_band = ((band_2 - band_1) / (band_2 + band_1))
	# Get the input file filename without extension and create a new file name
        parts = string.split(file)
        newname ='./'+parts[0]+'_ndvi.tif' # ./filename_ndvi.tif
	# Get the EPSG code from well known text projection
	epsg =rasterIO.wkt2epsg(proj_wkt)
        
	# Write the NDVI matrix to a new raster file
	rasterIO.writerasterband(new_ndvi_band, newname, XSize, YSize, geo_t_params, epsg)
    
# loop will now go to next file in input list
