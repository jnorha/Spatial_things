####################
# Run this script from the command line
# It will request the name/path of your input
# The name/desired path of your output
# Then it will request the band numbers for Red and NIR respectively
# Much of this code leans on the GDAL course led by Dr. Peter Bunting
# This can be found at: http://learningzone.rspsoc.org.uk/index.php/Learning-Materials/Python-Scripting/9.4-Calculate-NDVI-using-GDAL 
####################

# all of this info can easily be found using gdalinfo on your input file prior to running the script

import sys, os, struct
import osgeo.gdal as gdal


# Create and run Class Object NDVI calculator

class GDALCalcNDVI(object):

# -------------------------------------------------------- #

    #First we define the function of what we're actually trying to do here, ultimately produce a GDAL image
    def createOutputImage(self, outFilename, inDataset):
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

    def calcNDVI(self, filePath, outFilePath):
        dataset = gdal.Open(filePath, gdal.GA_ReadOnly)
        #Make sure it was successfully opened
        if dataset is None:
            print "The dataset was not found, or could not be opened"
            sys.exit(-1)

        #create the output dataset
        outDataset = self.createOutputImage(outFilePath, dataset)
        # Check that the output dataset was successfully created
        if outDataset is None:
            print "Could not create the output image"
            sys.exit(-1)
        # target the red and NIR bands of the image
        # image bands aer hard Coded, I believe NAIP is labeled 'R', 'B', etc.
        # RUN gdalinfo on raster to get bands and their respective numbers
        r = input("Which is the red band?: \n")
        nir = input("Which is the nir band?: \n")

        red_band = dataset.GetRasterBand(r) # Red band
        nir_band = dataset.GetRasterBand(nir) # NIR Band
        #### NOW WE LOOP THROUGH THE IMAGE, PIXEL BY PIXEL, calculating NDVI ####
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
                #calculate the NDVI for the current pixel.
                ndvi_denomer = (nir_tuple[i] + red_tuple[i])
                ndvi_numer = (nir_tuple[i] - red_tuple[i])
                ndvi = 0
                #be careful of zero divide
                if ndvi_denomer == 0:
                    ndvi = 0
                else:
                    ndvi = ndvi_numer/ndvi_denomer
                #add the current pixel to the output line
                outputLine = outputLine + struct.pack('f', ndvi)
            outDataset.GetRasterBand(1).WriteRaster(0, line, red_band.XSize, 1, outputLine, buf_xsize=red_band.XSize, buf_ysize=1, buf_type=gdal.GDT_Float32)
        # Delete the output line folliwng write
        del outputLine
        print 'NDVI Calculated and Outputted to File'


 # -------------------------------------------------------- #

    #function from where the script runs
    def run(self):
        #define the input and output images
        filePath = raw_input("Name and/or Path to input image?: \n")
        outFilePath = raw_input("Name and/or Path of desired NDVI output?: \n")
        #check to see if input file exists
        if os.path.exists(filePath):
            #if its there, run the calculation function
            self.calcNDVI(filePath, outFilePath)
        else:
            print "The input file doesn't exist"

if __name__ == '__main__':
  obj = GDALCalcNDVI()
  obj.run()
