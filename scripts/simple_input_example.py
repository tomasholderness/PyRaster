#Read a raster file

# Import the rasterIO module
import rasterIO
 
# Open a gdal pointer to a file on disk
file_pointer = rasterIO.opengdalraster(
    '/path/surface_temperature_kelvin.tif')
 
# Get the spatial reference information from the image
drive, XSize, YSize, proj_wkt, geo_t_params =
    rasterIO.readrastermeta(pointer)
 
# Read a band from the file to a new matrix in memory,
    #the number indicates which band to read.
kelvin_band = rasterIO.readrasterband(file_pointer, 1)
