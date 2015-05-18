PyRaster
===========
**Python Geospatial Image Processing**

####PyRaster Changelog

### 1.0.1 - First release "working" 10/11/2010
- Added NoDataVal handling for both read and write.
- Added PCRS support using WKT from source image metadata
- New function wkt2epsg
- Moved UHII function to avhrr.py
- Moved all AVHRR specific functions to avhrr.py
- Moved all statistical functions to rasterStats.py.v1
- Moved all processing functions to rasterProcs.py.v1
- Moved this file (remaining functions) to rasterIO.py.v1
- readrasterband - Added masking to NaN values.
- opengdalraster - Added exception, raising IOError if opening broken raster.
- Added exceptions, raising errors where appropriate.
- Marked this as version 1.0.1 - working.
