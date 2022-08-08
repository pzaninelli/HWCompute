#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 13:21:43 2022

@author: Pablo G. Zaninelli
"""

from netCDF4 import Dataset, num2date
import pandas as pd
from multiprocessing import Pool
from functools import partial
import numpy as np
from HWCompute.preprocess import daymax, daymin, tranCelcius, convertLon, coorobj
from HWCompute.compute_percentile import dayPerc, checkAllNAN, checkAnyNAN
from HWCompute.lib.Heatwave import hwstat


def hw1d(df, q, window, umbral, yStartP, yEndP, lon, lat):
    assert isinstance(df, pd.core.frame.DataFrame)
    _reqCol = ['doy', 'temp']
    colnames = [ii for ii in df.keys()]
    colnames.sort()
    if not colnames == _reqCol:
        raise AttributeError("df must have 'doy' and 'temp' columns")
    if not np.ma.is_masked(df.temp) and not checkAllNAN(df.temp):
        perc = dayPerc(df, q, window, yStartP, yEndP)
        if checkAnyNAN(df.temp):
            df = df.dropna() # remove NaN values if they exist
        mat = df.to_numpy()
        inds, indf, acc, mmean, maxi, mini, max_ex, sum_ex = hwstat(mat,perc, umbral)
        if not inds.size == 0:
            tBeginHW, tEndHW = df.index[inds], df.index[indf]
            DF = pd.DataFrame({'longitude':[float(lon)]*acc.shape[0],
                               'latitude':[float(lat)]*acc.shape[0],
                               'start':tBeginHW,
                               'end':tEndHW,
                               'accumulated':acc,
                               'mean':mmean,
                               'maxtemp':maxi,
                               'mintemp':mini,
                               'max_ex':max_ex,
                               'sum_ex':sum_ex})
        else:
            DF = pd.DataFrame({'longitude':float(lon),
                               'latitude':float(lat),
                               'start':np.nan,
                               'end':np.nan,
                               'accumulated':np.nan,
                               'mean':np.nan,
                               'maxtemp':np.nan,
                               'mintemp':np.nan,
                               'max_ex':np.nan,
                               'sum_ex':np.nan},
                              index=[0])
    else:
           DF = pd.DataFrame({'longitude':float(lon),
                               'latitude':float(lat),
                               'start':np.nan,
                               'end':np.nan,
                               'accumulated':np.nan,
                               'mean':np.nan,
                               'maxtemp':np.nan,
                               'mintemp':np.nan,
                               'max_ex':np.nan,
                               'sum_ex':np.nan},
                             index=[0]) 
    return DF

def loadDF(ncFile, main_var, time_var, ilon, ilat, tmax, daily, kelvin):
    nc = Dataset(ncFile)
    time = nc.variables[time_var]
    df = pd.DataFrame({'date':pd.to_datetime([str(x) for x in num2date(time[:], 
                                                        time.units)]),
                        'temp':nc.variables[main_var][:,ilat,ilon]})
    nc.close()
    df['doy'] = df.date.dt.dayofyear
    if not daily or not np.ma.is_masked(df.temp):
        if tmax:
            df = daymax(df)
        else:
            df = daymin(df)
    if kelvin and not np.ma.is_masked(df.temp):
        df = tranCelcius(df) # convert to celsius degree
    return df

def func_mp(ncFile, main_var, time_var, tmax, daily, kelvin, q, window, umbral, 
            yStartP, yEndP, lon, lat, ilat, ilon):
    lon0, lat0 = lon[ilon], lat[ilat]
    print(f"latitude: {lat0}, longitude: {lon0}")
    df = loadDF(ncFile, main_var, time_var, ilon, ilat, tmax, daily, kelvin)
    result = hw1d(df, q, window, umbral, yStartP, yEndP, lon0, lat0)
    return result

def hwbpointNC(ncFile, main_var, time_var, lon_var, lat_var, tmax = True,
               daily = False,
               kelvin = True,
               filemask = None,
               mNCVarName = None,
               mNCLonName = None,
               mNCLatName = None,
               trim_lon = None,
               trim_lat = None,
               ncpu = None,
               **args):
    if not args:
        raise AttributeError("Parameters to compute HW are not defined!")
    if ncpu is None:
        raise AttributeError("The number of CPUs to be used must be provided")
    nc = Dataset(ncFile)
    lon = nc.variables[lon_var][:]
    lon = convertLon(lon)
    lat = nc.variables[lat_var][:]
    nc.close()
    coord = coorobj(lon, lat, trim_lat=trim_lat, trim_lon = trim_lon)
    ilat, ilon = coord.getInd(filemask=filemask,
                              mNCVarName = mNCVarName,
                              mNCLonName = mNCLonName,
                              mNCLatName = mNCLatName)
    func_mp_p = partial(func_mp, ncFile, main_var, time_var,tmax, daily, kelvin,
                        args["q"], 
                        args["window"], 
                        args["umbral"], 
                        args["yStartP"], 
                        args["yEndP"],
                        lon, lat)
    pool = Pool(ncpu)
    dfs = pool.starmap(func_mp_p, zip(ilat,ilon))
    pool.close()
    pool.join()
    hwDF = pd.concat(dfs,ignore_index=True)
    return hwDF
    

if __name__ == "__main__":    
    filename = "/home/pzaninelli/TRABAJO/IGEO/comparacion/2m_temperature_6h_era_5_1950-2021_2_5.nc"
    hwdf = hwbpointNC(filename, main_var ="t2m", time_var = "time",
                      lon_var = "longitude", lat_var = "latitude", tmax = False,
                      daily = False, kelvin = True,
                      filemask="/home/pzaninelli/TRABAJO/IGEO/comparacion/land_sea_mask_6h_era_5_01011979-31121979_2_5.nc",
                      mNCVarName="lsm", mNCLatName="latitude", mNCLonName="longitude",
                      trim_lon = [-22,45], trim_lat = [27,72], ncpu = 10,
                      q= 90,window = 15, umbral = 3, yStartP = 1950, yEndP = 1980)