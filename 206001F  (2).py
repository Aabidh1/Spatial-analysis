# -*- coding: utf-8 -*-
"""206001F.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FbnxMj2vjuRo3gtkRnbCxLR3jNFjV0Hs
"""

# First we will import the earth engine package
import ee

# Trigger the authentication
ee.Authenticate()

# Initialize the library
ee.Initialize()

# Import the feature collection as the world dataset
world = ee.FeatureCollection('USDOS/LSIB_SIMPLE/2017')
# Map over the feature collection to extract the 'country_na' attribute and get unique values
country_names = world.aggregate_array('country_na').distinct().getInfo()
# Print the list of country names
for country in country_names:
 print(country)

import folium

country = 'Mexico'
aoi = world.filter(ee.Filter.eq('country_na', country))
precip = (ee.ImageCollection('UCSB-CHG/CHIRPS/PENTAD')
.select('precipitation')
.filterDate('2010-01-01', '2015-12-31')
.filterBounds(aoi)
.sum())
# Define a colour palette to visualize the images
RF_PALETTE = "ff0000, ffff00, 00ffff, 0000ff"
vis_params = {
'min': 0,
'max': 2000,
'palette': RF_PALETTE
}

#!pip install folium
import folium
# Function to visualize Earth Engine image layers using folium.
def add_ee_layer(self, ee_object, vis_params, name):
    try:
        if isinstance(ee_object, ee.image.Image):
            map_id_dict = ee.Image(ee_object).getMapId(vis_params)
            folium.raster_layers.TileLayer(
                tiles = map_id_dict['tile_fetcher'].url_format,
                attr = 'Google Earth Engine',
                name = name,
                overlay = True,
                control = True
            ).add_to(self)
        elif isinstance(ee_object, ee.imagecollection.ImageCollection):
            ee_object_new = ee_object.mosaic()
            map_id_dict = ee.Image(ee_object_new).getMapId(vis_params)
            folium.raster_layers.TileLayer(
                tiles = map_id_dict['tile_fetcher'].url_format,
                attr = 'Google Earth Engine',
                name = name,
                overlay = True,
                control = True
            ).add_to(self)
        elif isinstance(ee_object, ee.geometry.Geometry):
            folium.GeoJson(
                data = ee_object.getInfo(),
                name = name,
                overlay = True,
                control = True
            ).add_to(self)
        elif isinstance(ee_object, ee.featurecollection.FeatureCollection):
            ee_object_new = ee.Image().paint(ee_object, 0, 2)
            map_id_dict = ee.Image(ee_object_new).getMapId(vis_params)
            folium.raster_layers.TileLayer(
                tiles = map_id_dict['tile_fetcher'].url_format,
                attr = 'Google Earth Engine',
                name = name,
                overlay = True,
                control = True
            ).add_to(self)
    except:
        print("Could not display {}".format(name))

# Add custom method to folium
folium.Map.add_ee_layer = add_ee_layer

# Create a map centered around the country
location = [22.079731,-124.4056723]
map_country = folium.Map(location=location, zoom_start=7)
map_country.add_ee_layer(precip.clip(aoi), vis_params, 'Rainfall')
map_country.add_ee_layer(aoi, {}, country)
# Display the map
display(map_country)

# Define the years for which you want to get the precip images
years = [2010, 2011, 2012, 2013, 2014, 2015]

# Initialize an empty dictionary to store the precip images
precip_images = {}

# Loop through each year
for year in years:
    # Convert the year to string for date formatting
    str_year = str(year)

    # Load an image of daily precipitation in mm/day.
    # Sums up the precipitation values from all the images in the filtered ImageCollection.
    # The result is a single ee.Image where each pixel value represents
    # the total accumulated precipitation for the entire year within the AOI.
    precip = (ee.ImageCollection('UCSB-CHG/CHIRPS/PENTAD')
               .select('precipitation')
               .filterDate(f'{str_year}-01-01', f'{str_year}-12-31')
               .filterBounds(aoi)
               .sum())

    # Store the precip image in the dictionary using the year as the key
    precip_images[year] = precip

    # Add the precipitation layers for each year
    map_country.add_ee_layer(precip.clip(aoi), vis_params, f'Rainfall {year}')

# Add the AOI layer
map_country.add_ee_layer(aoi, {}, country)

# Add Layer Control
folium.LayerControl().add_to(map_country)

# Display the map
display(map_country)

# Define the years for which you want to get the NDVI images
years = [2010, 2011, 2012, 2013, 2014, 2015]

# Initialize an empty dictionary to store the NDVI images
ndvi_images = {}

# Loop through each year
for year in years:
    # Convert the year to string for date formatting
    str_year = str(year)

    # Load the image collection for the given year within the AOI.
    # The MODIS MOD09Q1 product has a band named ’sur_refl_b02’ for red and ’sur_refl_b01’ for NIR.
    images = (ee.ImageCollection('MODIS/006/MOD09Q1')
              .select(['sur_refl_b01', 'sur_refl_b02'])
              .filterDate(f'{str_year}-01-01', f'{str_year}-12-31')
              .filterBounds(aoi))

    # Compute the mean NDVI for the entire year.
    # NDVI formula: (NIR - RED) / (NIR + RED)
    mean_ndvi = images.map(lambda img: img.normalizedDifference(['sur_refl_b01', 'sur_refl_b02'])).mean()

    # Store the mean NDVI image in the dictionary using the year as the key
    ndvi_images[year] = mean_ndvi

folium.Map.add_ee_layer = add_ee_layer


# Define a colour palette to visualize the images
RF_PALETTE = "ff0000, ffff00, 00ffff, 0000ff"
vis_params = {
    'min': -1,
    'max': 1,
    'palette': RF_PALETTE
}

# Create a map centered around the country
location = [22.079731,-124.4056723]
map_country = folium.Map(location=location, zoom_start=7)

# Add the ndvi layers for each year
for year in [2010, 2011, 2012, 2013, 2014, 2015]:
    ndvi = ndvi_images[year]
    map_country.add_ee_layer(ndvi.clip(aoi), vis_params, f'NDVI {year}')

# Add the AOI layer
map_country.add_ee_layer(aoi, {}, country)

# Add Layer Control
folium.LayerControl().add_to(map_country)

# Display the map
display(map_country)

# Assume ’ndvi_2015’ is the NDVI image for the year
ndvi_2015 = ndvi_images[2015]
# Set visualization parameters
vis_params = {
'min': -1,
'max': 1,
'palette': RF_PALETTE
}
# Get the thumbnail URL
thumbnail_url = ndvi_2015.getThumbUrl({
'bands': 'nd',
'min': vis_params['min'],
'max': vis_params['max'],
'palette': vis_params['palette'],
'region': aoi.geometry().bounds().getInfo()['coordinates'],
'dimensions': 512,
'format': 'png'
})
from IPython.display import display, Image
display(Image(url=thumbnail_url))