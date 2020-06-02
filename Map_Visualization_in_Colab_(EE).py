!pip install earthengine-api

!earthengine authenticate
import ee
ee.Initialize()

import tensorflow as tf
#tf.enable_eager_execution
import folium

#Define the URL format used for Earth Engine generated map tiles - Folium
EE_TILES = 'https://earthengine.googleapis.com/map/{mapid}/{{z}}/{{x}}/{{y}}?token={token}'

# Define the main bands of interest
bands = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7']
# Use Landsat 8 surface reflectance data.
landsat8_sr = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')

# Cloud masking function.
def maskL8sr(image):
  cloudShadowBitMask = ee.Number(2).pow(3).int()
  cloudsBitMask = ee.Number(2).pow(5).int()
  qa = image.select('pixel_qa')
  mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0).And(
    qa.bitwiseAnd(cloudsBitMask).eq(0))
  return image.updateMask(mask).select(bands).divide(10000)

# The image input data is a 2016 cloud-masked median composite.
L8_2016 = landsat8_sr.filterDate('2016-01-01', '2016-12-31').map(maskL8sr).median()

# Use folium to visualize the imagery.
mapid = L8_2016.getMapId({'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.3})
map = folium.Map(location=[38., -122.5])
folium.TileLayer(
    tiles=EE_TILES.format(**mapid),
    attr='Google Earth Engine',
    overlay=True,
    name='median composite',
  ).add_to(map)
map

import ee.mapclient
import datetime
#sierra_forest = ee.Geometry.Polygon([-121.01084654498175, 36.85826412236856],[-118.11045591998175, 36.85826412236856],[-118.11045591998175, 38.51009291635742],[-121.01084654498175, 38.51009291635742],[-121.01084654498175, 36.85826412236856])
#still figuring out best way to define geometry/clip polygons
collection = (ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
             .filterDate(datetime.datetime(2016, 1, 1), datetime.datetime(2016, 12, 1))
             #.filterBounds(sierra_forest))
             )

#simple index for first attempts at expressions
def NDVI(x):
  return x.expression('float(b("B5") - b("B4")) / (b("B5") + b("B4"))')

#make NDVI from 2016 SR image
ndvi16 = NDVI(L8_2016)

vis = {
    'min': 0,
    'max': 1,
    'palette': [
        'FFFFFF', 'CE7E45', 'DF923D', 'F1B555', 'FCD163',
        '99B718', '74A901', '66A000', '529400', '3E8601',
        '207401', '056201', '004C00', '023B01', '012E01',
        '011D01', '011301'
    ]}

#for exporting images through EE client map
ee.mapclient.addToMap(collection.map(NDVI).mean(), vis)

#use Descartes Folium to visualize map with several layers
ndvi16id = ndvi16.getMapId({'min': 0, 'max': 1, 'palette':['blue', 'white', 'green']})
map2 = folium.Map(location=[38., -122.5])
folium.TileLayer(
    tiles=EE_TILES.format(**ndvi16id),
    attr='Google Earth Engine',
    overlay=True,
    name='NDVI16',
  ).add_to(map2)
folium.TileLayer(
    tiles=EE_TILES.format(**mapid),
    attr='Google Earth Engine',
    overlay=True,
    name='L8 SR 16 mean',
  ).add_to(map2)

#add layer managability
map2.add_child(folium.LayerControl())

#Display map2
map2

## # scroll to top of output to see layer control, depends on your browser window size

#landsat8_sr = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
#L8_2016 = landsat8_sr.filterDate('2016-01-01', '2016-12-31').map(maskL8sr).median()
#all that needs to be done is build the fuction that takes these user inputs to search/apply the earth engine catalog ID and pull the desired dataset at the desired aquisition time


def ee_dataset():
  sensor = input("Sensor: ")
  date = input("Start and end date ('YYYY-MM-DD', 'YYYY-MM-DD'): ")

ee_dataset()


#this function will take input in the form of python list of images in another list with an image - parameter - and layer label *** labels have to be unique to each layer or there will only be one of that name
#one such nested list might look like [ [image, {params}, 'label1'], [image2, {params2}, 'label2'] , [image3, {params3}, 'label3'] ] for example:
images = [[ndvi16, {'min': 0, 'max': 1, 'palette':['blue', 'white', 'green']}, 'NDVI'] , [L8_2016, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.3}, 'Landsat']]

#if the parameters are unknown go with a default of {'palette': ['black', 'white']} --- this will give a blk to white gradient if its scalable and black and white if its a binary image

def display_w_folium(list_of_images):
  #import folium if it hasnt already been done
  import folium
  #set up the EE tile format and token
  EE_TILES = 'https://earthengine.googleapis.com/map/{mapid}/{{z}}/{{x}}/{{y}}?token={token}'
  #set up the map and point of focus
  mymap = folium.Map(location=[37., -119.5])

  #set up a for parser to make ID's where i_p is one image + parameter pair
  #set up list of id's
  ids_ls = []
  for i_p in list_of_images:
    ids = i_p[0].getMapId(i_p[1]) #--- wasnt working either, tried to do directly in list
    #add your new id to the map
    ids_ls.append(ids)
  #add as tiles to the map and make labels
  labels = []
  for a in list_of_images:
    labels.append(a[2])
  g = 0
  print('Layer Names:')
  for y in ids_ls:
    lname = labels[g]
    print(lname)
    folium.TileLayer(
      tiles=EE_TILES.format(**y),
      attr='Google Earth Engine',
      overlay=True,
      name= lname,
    ).add_to(mymap)
    g += 1
  mymap.add_child(folium.LayerControl())
  return mymap

display_w_folium(images) #has to be at bottom to show image output

#create a second list of earth engine images and their parameters
images2 = [[ndvi16, {'min': 0, 'max': 1, 'palette':['blue', 'white', 'green']}, 'NDVI1'] ,
           [L8_2016, {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.3}, 'Landsat'],
           [ndvi16, {'min': 0, 'max': 1, 'palette':['red', 'white', 'green']}, 'NDVI2']]




display_w_folium(images2)
