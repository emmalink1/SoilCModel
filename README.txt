
# Modelling Soil Carbon Content

## Description of project
This is the same project that I completed for my MVP1. 

## Major code chunks
I tried to follow markdown formatting as best as I could in this script. The major code chunks are: 

##Importing Packages
##Import soils data (NCSS gdb) and subsetting to area of interest (MN)
Originally, I wanted to edit my code for this section and consider the whole US as an area of interest. However, things really broke down when I tried to do this. 
##Wrangling NCSS gdb into one dataframe
- this is followed by reading in all of the data layers that I need from the dataframe (NCSS, carbon_extractions, bulk_density) 
Calculating SOC for each pedon 
- define three functions to do so 
Map and inspect calculated SOC
- I output a .png graph so that I can look at it here
Extract landvoer information from HistoricLandcover modeled layers and join to soils data
- 3 functions defined in this section 
Build Predictive model 
- includes testing and assessment of mean absolute error

## Why this represents a MVP
Originally, I wanted to expand upon the actual code of my MVP1 and move the workflow into a batch submission form for MVP2. At first this seemed 
entirely possible as moving the code in initially went well. However, I soon found that it was very difficult for me to expand and improve the workflow in a batch
submission form - I am much more attacheched to jupyter notebooks than I thought. I initially broke some things (badly) and spent a lot of time 
trying to get back to working code. From this process, I learned that I will probably always try to edit long workflows on a subset of data in a 
Jupyter notebook environment, and move to batch submission only when I feel pretty confident that the workflow is working well. I also was able to 
learn how to push to github from the MSI environment, which was a bit more tricky than from my local environment. I estimate that I spent around 10 
hours on this project. 
My friend Dustin Michels helped me through some github issues. 
 
