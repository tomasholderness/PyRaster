"""
multiprocess.py - use multiprocessing to parallelize processing of raster data,
to calculate Normalised Difference Vegetation Index for all scenes in directory.

Part of the PyRaster suite https://github.com/talltom/PyRaster

To run, do:

python multiprocess.py
"""

import sys, os, string, rasterIO
from multiprocessing import Process, Queue

# Create a function for the process

def processfunction(file_list):

	# Create a loop for all files in current directory


	for file in file_list:

		# Check file type (in this case Geotiff)
		if file.endswith('.tif'):

		# Open a pointer to the file
		pointer = rasterIO.opengdalraster(file)

		# Read the raster metadata for the new output file
		driver, XSize, YSize, proj_wkt, geo_t_params = rasterIO.readrastermeta(pointer)

		# Read the first band to a matrix called band_1
		band_1 = rasterIO.readrasterband(pointer, 1)

		# Read the second band to a matrix called band_2

		band_2 =rasterIO.readrasterband(pointer, 2)

		# Perform the NDVI calculation and put the results into a new matrix
		new_ndvi_band = ((band_2 - band_1) / (band_2 + band_1))

		# Get the input file filename without extension and create a new file name
		parts =string.split(file)
		newname = './'+parts[0]+'_ndvi.tif' # ./filename_ndvi.tif

	# Get the EPSG code from well known text projection
	epsg = rasterIO.wkt2epsg(proj_wkt)

	# Write the NDVI matrix to a new raster file
	rasterIO.writerasterband(new_ndvi_band, newname, XSize, YSize, geo_t_params, epsg)

# loop will now go to next file in input list
# Create a run function to accept jobs from queue
def processRun(q, filename):
	q.put(processfunc(filename))

# Create the main function
def main(arg=sys.argv):
	# Get a list fo files in the current directory (assumed to contain raster data)
	file_list = os.listdir(os.getcwd())

	# Get the length of the file list
	len_flist = len(file_list)
	half_len = len_flist / 2

	# Create a queue object
	q = Queue()

	# Create two processes (add more depending on processor availability)
	p1 = Process(target=processRun, args=(q, flist[:half_len]))
	p2 = Process(target=processRun, args=(q, flist[half_len:]))

	# Start processes
	p1.start()
	p2.start()

# Standard Python script execution/exit handling

if __name__=='__main__':
	sys.exit(main())
