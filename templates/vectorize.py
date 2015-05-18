"""
vectorize.py - create an optimised matrix function for pixel-wise raster
computation.

Part of the PyRaster suite https://github.com/talltom/PyRaster

Using the numpy.vectorize() function it is possible to create an
#optimised matrix function from a standard function.

To run, do:

python vectorize.py
"""
import numpy
import pyraster

# Create instance of RasterIO class
rio = pyraster.RasterIO()

#define function to create Boolean output based on threshold
def value_test(a, b):
    '''Accepts to values (a, b) returns 1 in a <=b, else returns 0'''
    if a <= b:
        return 1
    else:
        return 0
#vectorize the function, forcing 32-bit ints on 64-bit machines
value_test_vect = numpy.vectorize(value_test, otypes=[numpy.int32])
#open raster file
dataset = rio.open('file1.tif')
#read in band 1
band1 = rio.read_band(dataset, 1)
#get raster metadata
metadata = rio.read_metadata(dataset)
#pass the new vectorized threshold function the matrix and test value
threshold = 20
new_band = value_test_vect(band1, threshold)
#write Boolean matrix to raster file
rio.write_bands('newfile.tif', 'GTiff', metadata['xsize'], metadata['ysize'], metadata['geotranslation'], rio.wkt_to_epsg(metadata['projection']), None, new_band)
