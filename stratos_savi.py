import sys, os, struct
import osgeo.gdal as gdal

# Create and run Class Object savi calculator
# Main function to import form this module is savi_c

# savi_c takes 4 arguments, first is the INPUT FILE, then desired OUTPUT FILE, then RED BAND #, then NIR BAND #

# -------------------------------------------------------- #

#First we define the function of what we're actually trying to do here, ultimately produce a GDAL image
def createOutputImage(outFilename, inDataset):
    #define the image driver to be used
    #this will define the output image format (e.g. GeoTiff)
    driver = gdal.GetDriverByName("GTiff")
    #check that this driver can create a new file.
    metadata = driver.GetMetadata()
    if metadata.has_key(gdal.DCAP_CREATE) and metadata[gdal.DCAP_CREATE] == 'YES':
        print 'Driver GTiff supports Create() method'
    else:
        print 'Driver GTiff does not support Create()'
        sys.exit(-1)
    #Get the spatial information from the input file
    geoTransform = inDataset.GetGeoTransform()
    geoProjection = inDataset.GetProjection()
    # Create an output file of the same size as the input
    # image, but with only 1 output band
    newDataset = driver.Create(outFilename, inDataset.RasterXSize, inDataset.RasterYSize, 1, gdal.GDT_Float32)
    newDataset.SetGeoTransform(geoTransform)
    newDataset.SetProjection(geoProjection)
    return newDataset

# -------------------------------------------------------- #

def savi_c(filePath, outFilePath, b_r, b_nir):
    #check to see if input file exists
    if os.path.exists(filePath):
        print "Found input file"
    else:
        print "The input file doesn't exist"
    dataset = gdal.Open(filePath, gdal.GA_ReadOnly)
    #Make sure it was successfully opened
    if dataset is None:
        print "The dataset was not found, or could not be opened"
        sys.exit(-1)

    #create the output dataset
    outDataset = createOutputImage(outFilePath, dataset)
    # Check that the output dataset was successfully created
    if outDataset is None:
        print "Could not create the output image"
        sys.exit(-1)
    # target the red and NIR bands of the image
    # image bands aer hard Coded, I believe NAIP is labeled 'R', 'B', etc.
    # RUN gdalinfo on raster to get bands and their respective numbers
    red_band = dataset.GetRasterBand(b_r) # Red band
    nir_band = dataset.GetRasterBand(b_nir) # NIR Band
    #### NOW WE LOOP THROUGH THE IMAGE, PIXEL BY PIXEL, calculating savi ####
    # retrieve the number of lines within the image
    numLines = red_band.YSize
    # Loop through each line in turn
    for line in range(numLines):
        # Define variable for output line
        outputLine = ''
        # Read in data for the current line from the
        # image band representing the red wavelength
        red_scanline = red_band.ReadRaster( 0, line, red_band.XSize, 1, red_band.XSize, 1, gdal.GDT_Float32)
        # unpack the line of data to be read as floating point data
        red_tuple = struct.unpack('f' * red_band.XSize, red_scanline)
        # Read in data for the current line from the image band representing the NIR wavelength
        nir_scanline = nir_band.ReadRaster( 0, line, nir_band.XSize, 1, nir_band.XSize, 1, gdal.GDT_Float32)
        nir_tuple = struct.unpack('f' * nir_band.XSize, nir_scanline)

        #Loop through the columns within the image
        for i in range(len(red_tuple)):
            #calculate the savi for the current pixel.
            savi_denomer = (nir_tuple[i] + red_tuple[i] + 0.5)
            savi_numer = (1+0.5)(nir_tuple[i] - red_tuple[i])
            savi = 0
            #be careful of zero divide
            if savi_denomer == 0:
                savi = 0
            else:
                savi = savi_numer/savi_denomer
            #add the current pixel to the output line
            outputLine = outputLine + struct.pack('f', savi)
        outDataset.GetRasterBand(1).WriteRaster(0, line, red_band.XSize, 1, outputLine, buf_xsize=red_band.XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
    # Delete the output line folliwng write
    del outputLine
    print 'savi Calculated and Outputted to File'


 # -------------------------------------------------------- #
