
# Modelling Soil Carbon Content

# Description of project
This is the same project that I completed for my MVP1 but now executable via a bash submission script on MSI resources. The only changes I made were taking out visualizations printed in-line in Jupyter and exporting some map and model objects in the script so that they can be inspected as outputs outside of the slurm job summary output. 

My friend Dustin Michels helped me through some github issues. 

# Major code chunks
I tried to follow markdown formatting as best as I could in this script. The major code chunks are: 

## Importing Packages

## Import soils data (NCSS gdb) and subsetting to area of interest (MN)
Originally, I wanted to edit my code for this section and consider the whole US as an area of interest. However, things really broke down when I tried to do this entirely in nano editing, so after messing around for a few hours, I went back to the original. 

## Wrangling NCSS gdb into one dataframe
- this is followed by reading in all of the data layers that I need from the dataframe (NCSS, carbon_extractions, bulk_density) 

Some of the soils don't have bulk density data or soil C data so we're going to have to throw them out because you can't calculate total soil C without bulk density information.So now we are down to only 184 samples. This seems a bit low to me; I have seen other publications that had way larger datasets for states (including WI, next door). But I can't quite figure it out after looking for ~30 minutes. For proof of concept I'm going to move on with this much smaller dataset.

## Calculating SOC for each pedon 
- define three functions to do so. One function, create_pedons, passes each pedon to another function, new_pedon, and recieves calculated output to concatenate into a new dataframe. New_pedon runs pedon_sum, recieves its output, and adds necessary metadata from the original pedon information into it. Pedon_sum is a for loop over all rows in a pedon, adding them together and returning one summed line. 
- I am still not calculating SOC in the right way, mathematically. I'm running with an approximation because the math is hard. 
It's fairly standard practice to just consider the top 0.3 m (though there is a lot of SOC below that...). But at first, I'll consider the whole depth profile. In a more robust project I would make sure that soil C is calculated along the same depth and probably just subset to 0.3 m.  

Usually, we would use some pretty complicated math (spline function) to estimate the amount of carbon along the depth profile, smoothly. Unfortunately, a lot of the packages that were built around the spline function for soil C calculations are now not available and I am not very good at math. For proof of concept, I am not going to deal with that. Instead, I will calculate the amount of C in the soil profile just by adding up the amount of carbon in each depth increment as it is defined, without smoothing. 

## Map and inspect calculated SOC
- In contrast to my MVP1, where I printed maps in the Jupyter output, here I output a .png graph so that I can look at it. This is something I added and learned how to do. 

## Extract landvoer information from HistoricLandcover modeled layers and join to soils data
- 3 functions defined in this section 

## Build Predictive model 
- Build a random forest regressor using sklearn. Train and test it. 
- includes testing and assessment of mean absolute error

## Export predictive model 
- this is an additional one part that I added to my MVP1. I export the random forest regressor and the dataset so that I don't have to go back and rebuild it if I need to access the values

# Why this represents a MVP
Originally, I wanted to expand upon the actual code of my MVP1 and move the workflow into a batch submission form for MVP2. At first this seemed 
entirely possible as moving the code in initially went well. However, I soon found that it was very difficult for me to expand and improve the workflow 
in a batch submission form - I am much more attacheched to jupyter notebooks than I thought. I initially broke some things (badly) and spent a lot of 
time trying to get back to working code. From this process, I learned that I will probably always try to edit long workflows on a subset of data in a 
Jupyter notebook environment, and move to batch submission only when I feel pretty confident that the workflow is working well. One change that I made to the workflow was exporting objects like maps as a png and the random forest regression model and final data. This was the only way to view results outside of the slurm summary file, and I figured this would be good for sharing the results of the project. I also was able to learn how to push to github from the MSI environment, which was a bit more tricky than from my local environment. I estimate that I spent around 10 
hours on this project. 

 
