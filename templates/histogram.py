"""
histogram.py - plot histogram of raster values using Matploblib.

Part of the PyRaster suite https://github.com/talltom/PyRaster

To run, do:

python histogram.py
"""

import sys, os, string, pyraster
import numpy.ma as ma
import matplotlib.pyplot as plt

# Histogram function
def rasterHistogram(raster_matrix):
    '''Accepts matrix and generates histogram'''

    # Flatten 2d-matrix
    flat_raster = ma.compressed(raster_matrix)

    # Setup the plot (see matplotlib.sourceforge.net)
    fig = plt.figure(figsize=(8,8))
    ax = fig.add_subplot(1,1,1)

    # Plot histogram
    ax.hist(flat_raster, 100, normed=0, histtype='bar',
            align='mid')
    # Show the plot on screen
    plt.show()

# Open raster and read band
rio = pyraster.RasterIO()
dataset = rio.open('file1.tif')
band1 = rio.read_band(dataset, 1)

# Pass matrix representation of raster to function
rasterHistogram(band1)
