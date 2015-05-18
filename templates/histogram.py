"""
histogram.py - plot histogram of raster values using Matploblib.

Part of the PyRaster suite https://github.com/talltom/PyRaster

To run, do:

python histogram.py
"""

import sys, os, string, rasterIO
import numpy.ma as ma
import matplotlib.pyplot as plt

# histogram function
def rasterHistogram(raster_matrix):
    '''Accepts matrix and generates histogram'''

    # Flatten 2d-matrix
    flat_raster = ma.compressed(raster_matrix)

    # Setup the plot (see matplotlib.sourceforge.net)
    fig = plt.figure(figsize=(8,11))
    ax = fig.add_subplot(1,1,1)

    # Plot histogram
    ax.hist(flat_raster, 10, normed=0, histtype='bar',
            align=mid)
    # Show the plot on screen
    plt.show()

# Pass matrix representation of raster to function
rasterHistogram(band)
# Shows histogram on screen
