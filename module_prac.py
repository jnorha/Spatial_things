#Testing of ndvi_c import and application taking arguments. 
# ndvi_c takes 4 arguments: The first is your input GTiff, second is what/where you want your output to go, then an integer describing 
# which band is associated to the Red wavelength, and finally which band is associated with the NIR wavelengths.

import stratos_ndvi


stratos_ndvi.ndvi_c("naip_horicon_1m-0_1.tif", "naip_horicon_NDVIOUT-0_1.tif", 1, 4)
