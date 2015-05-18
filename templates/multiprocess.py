"""
multiprocess.py - use multiprocessing to parallelize processing of raster data,
to calculate Normalised Difference Vegetation Index for all scenes in directory.

Part of the PyRaster suite https://github.com/talltom/PyRaster

To run, do:

python multiprocess.py
"""

import sys, os, string, pyraster
from multiprocessing import Process, Queue

rio = pyraster.RasterIO()
file_list = os.listdir(os.getcwd())

# Create a function for the process
def processfunction(file_list):

	# Create a loop for all files in current directory
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
			band_2 =rio.read_band(dataset, 1)

			# Perform the NDVI calculation and put the results into a new matrix
			new_ndvi_band = ((band_2 - band_1) / (band_2 + band_1))

			# Get the input file filename without extension and create a new file name
			parts =string.split(file)
			newname = './'+parts[0]+'_ndvi.tif' # ./filename_ndvi.tif

	# Get the EPSG code from well known text projection
	epsg = rio.wkt_to_epsg(metadata['projection'])

	# Write the NDVI matrix to a new raster file
	rio.write_bands(newname, 'GTiff', metadata['xsize'], metadata['ysize'], metadata['geotranslation'], epsg, None, new_ndvi_band)

# loop will now go to next file in input list
# Create a run function to accept jobs from queue
def processRun(q, filename):
	q.put(processfunction(filename))

# Create the main function
def main(arg=sys.argv):
	# Get a list fo files in the current directory (assumed to contain raster data)
	file_list = os.listdir(os.getcwd())

	# Get the length of the file list
	len_file_list = len(file_list)
	half_len = len_file_list / 2

	# Create a queue object
	q = Queue()

	# Create two processes (add more depending on processor availability)
	p1 = Process(target=processRun, args=(q, file_list[:half_len]))
	p2 = Process(target=processRun, args=(q, file_list[half_len:]))

	# Start processes
	p1.start()
	p2.start()

# Standard Python script execution/exit handling

if __name__=='__main__':
	sys.exit(main())
