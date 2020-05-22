import sys, os, struct
import osgeo.gdal as gdal

# Create and run Tasseled Cap orthagonal geotransforms
# The TC_c() function can act on Sentinal or Landsat data. Includes coefficients for each.
# This original template will take an argument which specifies "sent2" for Sentinal and "lsat8" for landsat.

# Assumes TOA reflectance, and please, PLEASE try and select images that dont contain too many clouds... shouldn't harm
# the program if you do buuuutt i just dont like clouds.

# TC_c takes 4 arguments, first is the INPUT FILE, then desired OUTPUT FILE, then sensor type (sent2 or lsat8)

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
    newDataset = driver.Create(outFilename, inDataset.RasterXSize, inDataset.RasterYSize, 3, gdal.GDT_Float32)
    newDataset.SetGeoTransform(geoTransform)
    newDataset.SetProjection(geoProjection)
    return newDataset

# -------------------------------------------------------- #

def TC_c(filePath, outFilePath, sensor):
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
        print "Could not create the output image, or identify its desired location"
        sys.exit(-1)
    # target the red and NIR bands of the image
    # image bands aer hard Coded, I believe NAIP is labeled 'R', 'B', etc.
    # RUN gdalinfo on raster to get bands and their respective numbers
    # --  We have to designate each bands location to apply the correct coefficient -- #
    if sensor == "sent2":
        print "still have to establish bands for sent2"
    elif sensor == "lsat8":
        #blue
        B2 = dataset.GetRasterBand(1)
        #green
        B3 = dataset.GetRasterBand(2)
        #red
        B4 = dataset.GetRasterBand(3)
        #nir1
        B5 = dataset.GetRasterBand(4)
        #swir1
        B6 = dataset.GetRasterBand(5)
        #swir2
        B7 = dataset.GetRasterBand(6)

    else:
        print "unknown sensor type, please put either 'sent2' for Sentinal 2 or 'lsat8' for Landsat 8."

    #### NOW WE LOOP THROUGH THE IMAGE, PIXEL BY PIXEL, calculating TC indeces ####
    # retrieve the number of lines within the image
    numLines = B2.YSize
    # Loop through each line in turn
    for line in range(numLines):
        # Read in data for the current line from the
        # image band representing the respective wavelengths
        b2_scanline = B2.ReadRaster( 0, line, B2.XSize, 1, B2.XSize, 1, gdal.GDT_Float32)
        b3_scanline = B3.ReadRaster( 0, line, B2.XSize, 1, B2.XSize, 1, gdal.GDT_Float32)
        b4_scanline = B4.ReadRaster( 0, line, B2.XSize, 1, B2.XSize, 1, gdal.GDT_Float32)
        b5_scanline = B5.ReadRaster( 0, line, B2.XSize, 1, B2.XSize, 1, gdal.GDT_Float32)
        b6_scanline = B6.ReadRaster( 0, line, B2.XSize, 1, B2.XSize, 1, gdal.GDT_Float32)
        b7_scanline = B7.ReadRaster( 0, line, B2.XSize, 1, B2.XSize, 1, gdal.GDT_Float32)
        # unpack the line of data to be read as floating point data
        B2_tuple = struct.unpack('f' * B2.XSize, b2_scanline)
        B3_tuple = struct.unpack('f' * B3.XSize, b3_scanline)
        B4_tuple = struct.unpack('f' * B4.XSize, b4_scanline)
        B5_tuple = struct.unpack('f' * B5.XSize, b5_scanline)
        B6_tuple = struct.unpack('f' * B6.XSize, b6_scanline)
        B7_tuple = struct.unpack('f' * B7.XSize, b7_scanline)

        # Read in data for the current line from the image band representing the NIR wavelength
        transorms = ['Wetness', 'Greenness', 'Brightness']
# --- Here is where you input Greenness, Wetness and Brightness transforms and add them each as a new "WriteRaster"
        #Loop through the columns within the image
        for t in [1, 2, 3]:
            outputLine = ''
            if t == 1:
                #this will first calculate Brightness, Band 1 in output raster
                for i in range(len(B2_tuple)):
                    #calculate the TC for the current pixel.
                    TC = (B2_tuple[i] * 0.3029) + (B3_tuple[i] * 0.2786) + (B4_tuple[i] * 0.4733) + (B5_tuple[i] * 0.5599) + (B6_tuple[i] * 0.508) + (B7_tuple[i] * 0.1872)
                    #add the current pixel to the output line
                    outputLine = outputLine + struct.pack('f', TC)
                outDataset.GetRasterBand(t).WriteRaster(0, line, B2.XSize, 1, outputLine, buf_xsize=B2.XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
                del outputLine
            if t == 2:
                #this will calculate greenness Wohoo! this will be band 2 in our output RasterXSize
                #this will first calculate Brightness, Band 1 in output raster
                for i in range(len(B2_tuple)):
                    #calculate the TC for the current pixel.
                    TC = (B2_tuple[i] * -0.2941) + (B3_tuple[i] * -0.243) + (B4_tuple[i] * -0.5424) + (B5_tuple[i] * 0.7276) + (B6_tuple[i] * 0.0713) + (B7_tuple[i] * -0.1608)
                    #add the current pixel to the output line
                    outputLine = outputLine + struct.pack('f', TC)
                outDataset.GetRasterBand(t).WriteRaster(0, line, B2.XSize, 1, outputLine, buf_xsize=B2.XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
                del outputLine
            if t == 3:
                #this will calculate wetness Wohoo! this will be band 3 in our output RasterXSize
                #this will first calculate Brightness, Band 1 in output raster
                for i in range(len(B2_tuple)):
                    #calculate the TC for the current pixel.
                    TC = (B2_tuple[i] * 0.1511) + (B3_tuple[i] * 0.1973) + (B4_tuple[i] * 0.3283) + (B5_tuple[i] * 0.3407) + (B6_tuple[i] * -0.7117) + (B7_tuple[i] * -0.4559)
                    #add the current pixel to the output line
                    outputLine = outputLine + struct.pack('f', TC)
                outDataset.GetRasterBand(t).WriteRaster(0, line, B2.XSize, 1, outputLine, buf_xsize=B2.XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
                del outputLine
    # Delete the output line folliwng write
    print 'TC Calculated and Outputted to File'


 # -------------------------------------------------------- #
