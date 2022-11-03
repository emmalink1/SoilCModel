print("here")

### Import necessary packages
import numpy as np
import geopandas as gpd
import pandas as pd
import os
import fiona
import rasterio
import rioxarray as rxr
from rasterio.plot import plotting_extent
import joblib
import shapely
import warnings
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning) 
pd.options.mode.chained_assignment = None

## Import soils data
### National Cooperative soil survey point data for world
NCSS_file = "./MVP1_data/NCSS_Soil_Characterization_Database_09_14_2018.gdb"

pedonSites = gpd.read_file(NCSS_file, layer='NCSS_Site_Location')

## subsetting SSURGO data to site locations in MN
pedonSites = gpd.read_file(NCSS_file, layer='NCSS_Site_Location')
pedons_MN = pedonSites[(pedonSites['state_code']== "MN")]

### When I map this, it is clear that there are some mislabeled pedons in canada so I take those out by latitude.
### There is also one in ND but I'm not worried about that since it's close so I keep it in 
pedons_MN = pedons_MN[(pedons_MN['latitude_decimal_degrees'] < 60)]

### also subsetting out to just the columns that I want/need since there are otherwise 68
pedons_MN = pedons_MN[['site_key', 'site_obsdate', 'state_code', 'PedonName', 'geometry']]

### Finally, add a column 'year' with observation year read from observation date string
pedons_MN['year'] = pedons_MN['site_obsdate'].str[-4:]
print(pedons_MN.head())

## Wrangling and transofrmations of soil Pedon data
### Unfortunately I have to do a 3-way join of the data :( 

### Read in Pedon Taxonomy file
NCSS_Pedon_Taxonomy = gpd.read_file(NCSS_file, layer='NCSS_Pedon_Taxonomy')

### left joining to only keep MN subset but also keep all of it
### I also only want a few columns out of the NCSS_Pedon_Taxonomy layer; pedon_key, site_key
Sites_attributes = pedons_MN.merge(NCSS_Pedon_Taxonomy[['pedon_key','site_key']], on = 'site_key', how = 'left')
print(Sites_attributes.head())
### Read in NCSS_Layer
NCSS_Layer = gpd.read_file(NCSS_file, layer = 'NCSS_Layer')


## Merge sites_attributes with NCSS_Layer
#### Again, I only want a subset of the columns, but this time I want more of them
Sites_attributes = Sites_attributes.merge(NCSS_Layer[['pedon_key','labsampnum','site_key','layer_sequence', 'layer_type','hzn_top', 'hzn_bot']], on = ['pedon_key','site_key'], how = 'left')

### Read in Carbon_and_Extractions layer
Carbon_and_Extractions = gpd.read_file(NCSS_file, layer = 'Carbon_and_Extractions')
#list(Carbon_and_Extractions.columns)

### Merge sites_attributes with carbon_and_extractions layer
Sites_attributes = Sites_attributes.merge(Carbon_and_Extractions[['labsampnum','c_tot','c_tot_code','oc','oc_code']], on = 'labsampnum', how = 'left')

###Read in Bulk density layer
Bulk_Density_and_Moisture = gpd.read_file(NCSS_file, layer = 'Bulk_Density_and_Moisture')
### Merge sites_attributes with bulk_density layer (selecting 'db_od', bulk density over dry, misspelled aghhhh)

Sites_attributes = Sites_attributes.merge(Bulk_Density_and_Moisture[['labsampnum','db_od']], on = 'labsampnum', how = 'left')

### Get rid of points that don't have bulk density and oc data as they're useless to us 
Sites_attributes = Sites_attributes[(Sites_attributes["db_od"].isnull() == False)]

Sites_attributes = Sites_attributes[(Sites_attributes["oc"].isnull() == False)]
print(len(Sites_attributes.pedon_key.unique()))


## Calculate SOC for each pedon 

# pedon_sum: a function to sum the amount of C in all of the horizons. This function calculates the amount of OC in each increment as depth of increment*OC
def pedon_sum(pedon):
    carbon_sum = 0
    for i in range(len(pedon)):
        depth = pedon.iloc[i]['hzn_bot']-pedon.iloc[i]['hzn_top']
        carbon = depth * pedon.iloc[i]['oc'] 
        carbon_sum = carbon + carbon_sum
    return carbon_sum

# a function to create a new df with all the summed C and pedon attributes on 1 line
def new_pedon(pedon): 
    carbon_sum = pedon_sum(pedon)
    site_key = pedon.iloc[0,]['site_key']
    pedon_key = pedon.iloc[0,]['pedon_key']
    year = pedon.iloc[0,]['year']
    geometry = pedon.iloc[0,]['geometry']
    d = {'site_key':[site_key], 'pedon_key':[pedon_key],'year':[year],'geometry':[geometry], 'carbon_sum':[carbon_sum]}
    summed_pedon = pd.DataFrame(data=d)
    return summed_pedon

# a function to create a new df with the summed C of all pedons in original df
def create_pedons(df): 
    new_df = pd.DataFrame(columns=['site_key','pedon_key', 'year', 'geometry', 'carbon_sum'])
    for i in df.pedon_key.unique():
        #print(i)
        site_subset = df[(df["pedon_key"]==i)]
        pedon = new_pedon(site_subset)
        new_df = pd.concat([new_df, pedon])

    return new_df

Sites_CSummed = create_pedons(Sites_attributes)
#print(Sites_CSummed.head())
### Reset the index so that it isn't all 0s 
Sites_CSummed = Sites_CSummed.reset_index()


## Map and inspect soil C attributes

states = gpd.read_file("./MVP1_data/US_States/s_22mr22.shp")
MN = states[(states['NAME']== 'Minnesota')]
base = MN.plot(color='white', edgecolor='black', figsize=(11, 11))

Sites_CSummed_gdf = gpd.GeoDataFrame(Sites_CSummed, geometry='geometry')

### Match crs to our basemap
Sites_CSummed_gdf = Sites_CSummed_gdf.set_crs("EPSG:4269")
Sites_CSummed_gdf = Sites_CSummed_gdf.to_crs(MN.crs)

CSummedPlot = Sites_CSummed_gdf.plot(ax = base, column = 'carbon_sum', legend = True)
fig = CSummedPlot.get_figure()
fig.savefig('CSummedPlot.png')



## Extract landcover information to soils data 

# a function to strip year from each historic landcover file name
def get_year(filenames):
    Years = []
    for file in filenames: 
        Year = file[-8:-4]
        Years.append(Year)
    return Years


### get list of all landcover file directoryies in a dataframe with their year
files = os.listdir("./MVP1_data/HistoricLandcover/")
Years = get_year(files)
d = {'file':files, 'Year':Years}
LandCover = pd.DataFrame(data = d)

print(LandCover.head())

# a function that subsets a dataframe, CarbonDf, by unique years and passes it to sample_landcover. Needs LandCover to pass to sample_landcover. 
# returns a new dataframe with landcover class assigned by year
def get_landcover(CarbonDf,LandCover):
    new_df = pd.DataFrame(columns = ['site_key','pedon_key', 'year', 'geometry', 'carbon_sum','value'])
    for year in CarbonDf.year.unique():
        year_sub = CarbonDf[(CarbonDf['year']==year)]
        landcovered = sample_landcover(year_sub,year,LandCover)
        new_df = pd.concat([landcovered,new_df])
    return new_df

# A function that adds the landcover class from a raster from a year to point data. This is making the assumption that there is only one landcover map per year
def sample_landcover(year_sub,year,LandCover):
    ind = LandCover[LandCover['Year']==year].index.values
    tif = LandCover.loc[ind,'file'].tolist()[0]
    tif_path = "./MVP1_data/HistoricLandcover/"+tif
    landcover = rasterio.open(tif_path)
    coord_list = [(x,y) for x,y in zip(year_sub['geometry'].x , Sites_CSummed_gdf['geometry'].y)]
    year_sub['landcover'] = [x for x in landcover.sample(coord_list)]
    return year_sub

### make sure crs's line up
YearTest = "./MVP1_data/HistoricLandcover/CONUS_Historical_y1992.tif"
Year = rasterio.open(YearTest)
Sites_CSummed_gdf = Sites_CSummed_gdf.to_crs(Year.crs.data)

## run my functions
Sites_landcover = get_landcover(Sites_CSummed_gdf,LandCover)
print("Sites_landcover head", Sites_landcover.head())

## Build Predictive model

### define the columns we want as dependent (sum of total SOC) and independent (landcover and year)
x = Sites_landcover[['landcover']]
y = Sites_landcover['carbon_sum']

### split the dataframe for 70% training, 30% validation
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3)


### Assess the model :) 

### establish baseline error
mean_test = y_test.mean()
baseline_error = abs(mean_test - y_test)
print('Baseline absolute error', round(np.mean(baseline_error),2), 'g/cm^2')

# Fit model using Random Forest Regressor

from sklearn.ensemble import RandomForestRegressor

### create regressor object
regr = RandomForestRegressor(n_estimators = 100, random_state = 0)

###Fit the regressor with dataframes x_train and y_train
regr.fit(X_train, y_train)  

### Run model on the training dataset
y_pred=regr.predict(X_test)

### Evaluate how the model did using mean square error.  
from sklearn.metrics import mean_squared_error

mse = mean_squared_error(y_test, y_pred)
rmse = np.sqrt(mse)
rmse

## or we can look at the absolute value of the difference between predicted and "actual"
errors = abs(y_pred - y_test)
print('Mean Absolute Error:', round(np.mean(errors), 2), 'g/cm^2')

 
## save the model object and training data

joblib.dump(regr, "./random_forest.joblid")
Sites_landcover.to_csv("./SoilCandEnvData.csv")
