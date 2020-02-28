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
from datetime import datetime, timedelta

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
    ds = ds.rename({var_names[0]:'npp'}).set_coords(['lon','lat'])
    return(ds)

def fix_sign_error(ds):
    ''' 
    Negative and positive 32767 is added for blank values and should be 
    replaced with nans.
    
    Parameters: 
    ds (xarry dataset): single hdf file with erroneous values
  
    Returns: 
    ds: fixed values
    '''
    npp_array = ds['npp'].values
    npp_da = DataArray(npp_array, coords={'lat': ds.lat, 'lon': ds.lon},
             dims=['lat', 'lon'])
    ds['npp'] = npp_da
    return ds.where((ds['npp'] != 32767) & (ds['npp'] != -32767))

def add_time_coordinate(ds, doy):
    '''
    Get the year data from the time_coverage_start attribute and make a
    datetime object out of the day of the year value that is pulled from the
    filename
    '''
    time_start = to_datetime(ds.attrs['time_coverage_start'])
    ds.coords['time'] = datetime(time_start.year, 1, 1) + timedelta(doy - 1)
    ds = ds.expand_dims('time')
    return(ds)

def clean_dataset(ds, doy):
    ''' 
    Given a xarray dataset, clean up the data for it to be concatinated into
    an annual dataset. This involves sveral steps:
        - renaming and assigning the latitude and longitude
        - renaming the npp data to a generic 'npp'
        - Fixing a sign error
        - masking landvalues and null values (pixelValues == -32767,32767)
        - Adding a time dimension
        
    Parameters: 
    ds (xarray dataset): raw hdf4 file loaded into pandas dataframe
    doy (int): day of year represented as an integer
  
    Returns: 
    dataset: A gridded xarray dataset object ready to be concatenated
    '''
    latitude = linspace(45, 30.03597, 417)
    longitude = linspace(-140, -115.5454, 540)
    ds = fix_coordinate(ds, latitude, longitude)
    ds = fix_sign_error(ds)
    ds = add_time_coordinate(ds, doy)
    return ds


# This are the subdirectories to crawl through
sub_directories = [str(yr) for yr in range(1996, 2019)]
# print(sub_directories)
module_path = os.path.join(os.path.curdir,'remote_sensing_data/NPP_winsoft_dataset/')

for num, sub_dir in enumerate(sub_directories):
    file_names = glob(os.path.join(module_path, sub_dir)+'/*.hdf')
    for i, file_name in enumerate(sorted(file_names)):
        doy = int(os.path.basename(file_name)[5:8]) # hack to get the day of year out of the filename
        ds = open_dataset(file_name)
        if i == 0:
            ds_all = clean_dataset(ds, doy)
        else:
            ds = clean_dataset(ds, doy)
            ds_all = concat([ds_all, ds],dim='time')            
        if i == len(file_names) - 1:
            print('Writing out to netcdf {} of {}'.format(num,len(sub_directories)-1))
            ds_all = ds_all.sortby('time')
            ds_all.to_netcdf(os.path.join(module_path,'npp_netcdf/')+'npp_'+sub_dir+'.nc',mode='w')
#        
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