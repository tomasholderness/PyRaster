"""
vectorize.py - create an optimised matrix function for pixel-wise raster
computation. Part of the PyRaster suite.

Using the numpy.vectorize() function it is possible to create an
#optimised matrix function from a standard function.

To run, do:

python vectorize.py
"""
import numpy
from pyraster import rasterio as rio


#define function to create Boolean output based on threshold
def value_test(a, b):
    '''Accepts to values (a, b) returns 1 in a <=b, else returns 0'''
    if a <= b:
        return 1
    else:
        return 0
#vectorize the function
value_test_vect = numpy.vectorize(value_test)
#open raster file
dataset = rio.opengdalraster('data/sample1.tif')
#read in band 1
band1 = rio.readrasterband(dataset, 1)
#get raster metadata
metadata = rio.readrastermeta(dataset)
#pass the new vectorized threshold function the matrix and test value
new_matrix = value_test_vect(band1, some_value)
#write Boolean matrix to raster file
rio.writerasterband(dataset, metadata)
