#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 11 12:17:26 2019

@author: patrick
"""

from xarray import open_dataset, DataArray, concat
from numpy import linspace, where
from pandas import to_datetime
from glob import glob

import os

def fix_coordinate(ds,latitude,longitude):
    '''
    Data is gridded but the coordinates are not included in the file. For this
    the placeholder coordintes (fakedimensions) should be replaced with
    actual latitude and longitude values. 
    
    Parameters: 
    ds (xr.Dataset): single day raw hdf4 file
    latitude (np.array): 1-D array of latitude values
    longitude (np.array): 1-D array of longitude values
    
    Returns: 
    ds (xr.Datatset): dataset with proper coordinates and the name corrected

    '''
    var_names = [var for var in ds.variables]
    ds = ds.rename({'fakeDim0':'lat','fakeDim1':'lon'})
    ds['lat'] = latitude
    ds['lon'] = longitude
    ds = ds.rename({var_names[0]:'chl'}).set_coords(['lon','lat'])
    return(ds)

def fix_sign_error(ds):
    ''' 
    Data erroniously gets read in as a signed-8 bit int, when it should be 
    unsigned. To fix, data with with values > should have a constant 256 added
    to them. Also mask the landvalues and values where no data is available
    
    Parameters: 
    ds (xarry dataset): single hdf file with erroneous values
  
    Returns: 
    ds: fixed values
    '''
    chl_array = ds['chl'].values
    ix = where(chl_array < 0)
    chl_array[ix[0],ix[1]] = chl_array[ix[0],ix[1]] + 256
    chl_da = DataArray(chl_array, coords={'lat': ds.lat, 'lon': ds.lon},
             dims=['lat', 'lon'])
    ds['chl'] = chl_da
    return ds.where((ds['chl'] != 255) & (ds['chl'] != 1)& (ds['chl'] != 0))

def calculate_chl_conc(ds):
    ''' 
    Calculate chlorophyll concentration from pixelvalues 
    Equation found at http://www.wimsoft.com/CC4km.htm
    '''
    ds['chl'] = 10**(0.015*ds['chl']-2.0)
    return ds

def add_time_coordinate(ds):
    '''
    Add a time dimension to the data and fill that with the time_coverage_start
    value which is in the attributes of the file
    '''
    time_start = to_datetime(ds.attrs['time_coverage_start'])
    time_end = to_datetime(ds.attrs['time_coverage_end'])
    ds.coords['time']  = time_start + (time_start - time_end)/2
    ds = ds.expand_dims('time')
    return(ds)

def clean_dataset(ds):
    ''' 
    Given a xarray dataset, clean up the data for it to be concatinated into
    an annual dataset. This involves sveral steps:
        - renaming and assigning the latitude and longitude
        - renaming the chlorophyll data to a generic 'chl'
        - Fixing a sign error
        - masking landvalues and null values (pixelValues == 225,1,0)
        - Converting the data from pixelvalue to chlorophyll concentration
        - Adding a time dimension
        
    Parameters: 
    ds (xarray dataset): raw hdf4 file loaded into pandas dataframe
  
    Returns: 
    dataset: A gridded xarray dataset object ready to be concatenated
    '''
    latitude = linspace(45, 30.03597, 417)
    longitude = linspace(-140, -115.5454, 540)
    ds = fix_coordinate(ds, latitude, longitude)
    ds = fix_sign_error(ds)
    ds = calculate_chl_conc(ds)
    ds = add_time_coordinate(ds)
    return ds



## This are the subdirectories to crawl through
sub_directories = [str(yr) for yr in range(1996, 2019)]
# print(sub_directories)
module_path = os.path.join(os.path.curdir,'remote_sensing_data')

for sub_dir in sub_directories:
    file_names = glob(os.path.join(module_path, sub_dir)+'/*.hdf')
    for i, file_name in enumerate(sorted(file_names)):
        ds = open_dataset(file_name)
        if i == 0:
            ds_all = clean_dataset(ds)
        else:
            ds = clean_dataset(ds)
            ds_all = concat([ds_all, ds],dim='time')            
        if i == len(file_names) - 1:
            print('Writing out to netcdf')
            ds_all = ds_all.sortby('time')
            ds_all.to_netcdf(os.path.join(module_path,'chl_merged_netcdf/')+'merged_chl_'+sub_dir+'.nc',mode='w')
        
#
#file_name =  os.path.join(module_path, 'remote_sensing_data/2000/S20001992000203_chla_comp.hdf')
#
#ds = open_dataset("./remote_sensing_data/1996/O19963541996358_chla_comp.hdf")
#ds1 = clean_dataset(ds)
#print(ds1)
##
##
##file_name =  os.path.join(module_path, 'remote_sensing_data/2000/S20002002000204_chla_comp.hdf')
#ds = open_dataset('./remote_sensing_data/1996/O19963601996364_chla_comp.hdf')
#ds2 = clean_dataset(ds)
#print(ds2)
##
#ds3 = concat([ds1,ds2],dim='time')
#print(ds3)