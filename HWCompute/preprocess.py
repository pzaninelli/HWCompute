#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 18 11:44:30 2022
Preprocess functions
@author: Pablo G Zaninelli
"""
from netCDF4 import Dataset
import numpy as np
import itertools

def daymax(df):
    df = df.resample('D', on="date").max()
    return df.drop(columns = ["date"])

def daymin(df):
    df = df.resample('D', on="date").min()
    return df.drop(columns = ["date"])

def tranCelcius(df):
    df.temp = df.temp - 273.15
    return df

def convertLon(lon):
    lon = (((lon + 180) % 360) - 180)
    return lon

class coorobj:
    
    def __init__(self, longitude, latitude, trim_lon = None,
                 trim_lat = None):
        assert latitude.max() <= 90 and latitude.min()>=-90, "latitude out of range"
        assert longitude.max() <= 360 and longitude.min()>=-180, "longitude out of range"
        self._trim_lon = trim_lon
        self._trim_lat = trim_lat
        self._lon = convertLon(longitude)
        if not trim_lon is None:
            assert trim_lon[1]-trim_lon[0]>0, "the left value must be the lower value and the right value the upper value"
            assert trim_lon[0] >=-180 and trim_lon[1] <=180, "values of lon should bounded between -180, 180"
            self._lon, self._tlon = self._trim_coord(self._lon, trim_lon)
        else:
            self._tlon = [ii for ii in range(len(self._lon))]            
        self._lat = latitude
        if not trim_lat is None:
            assert trim_lat[1]-trim_lat[0]>0, "the left value must be the lower value and the right value the upper value"
            assert trim_lat[0] >=-90 and trim_lat[1] <=90, "values of lat should bounded between -90, 90"
            self._lat, self._tlat = self._trim_coord(self._lat, trim_lat)
        else:
            self._tlat = [ii for ii in range(len(self._lat))]
           
    def getInd(self, 
                  filemask = None,
                  mNCVarName = None,
                  mNCLonName = None,
                  mNCLatName = None):
        ilon = []; ilat = [];
        if filemask is None:        
            for x, y in itertools.product(self.tlon, self.tlat):
                ilon.append(x)
                ilat.append(y)
        else:
            print("Mask was found!")
            with Dataset(filemask) as nc:
               lsm = nc.variables[mNCVarName][0,:,:]
               lonM = nc.variables[mNCLonName][:]
               latM = nc.variables[mNCLatName][:]
               lonM = convertLon(lonM)
               lsm = np.where(lsm > .5, lsm, np.nan) # apply the mask

               if not self._trim_lon is None:
                   lonM, tlonM = self._trim_coord(lonM, self._trim_lon)
               if not self._trim_lat is None:
                   latM, tlatM = self._trim_coord(latM, self._trim_lat)
               # checking correspondence between lon and lat and lonM and latM respectivesly
               assert np.max(np.abs(np.sort(self.lat)-np.sort(latM))) == 0.0, "lat of mask do not agree with lat"
               assert np.max(np.abs(np.sort(self.lon)-np.sort(lonM))) == 0.0, "lon of mask do not agree with lon"
               # in the case the domain was trimmed
               if not self._trim_lon is None and not self._trim_lat is None:
                   for y, x in itertools.product(tlatM,tlonM):
                           if not np.isnan(lsm[y,x]):
                               ilat.append(y)
                               ilon.append(x)
               elif self._trim_lon is None and not self._trim_lat is None:
                   for y, x in itertools.product(tlatM,range(len(lonM))):
                       if not np.isnan(lsm[y,x]):
                           ilat.append(y)
                           ilon.append(x)
               elif not self._trim_lon is None and self._trim_lat is None:
                   for y, x in itertools.product(range(len(latM)),tlonM):
                       if not np.isnan(lsm[y,x]):
                           ilat.append(y)
                           ilon.append(x)
               else: # for not trim operation
                    for y, x in itertools.product(range(len(latM)),range(len(lonM))):
                        if not np.isnan(lsm[y,x]):
                            ilat.append(y)
                            ilon.append(x)
        return ilat, ilon
        
    @property
    def lon(self):
        return self._lon

    @property
    def lat(self):
        return self._lat
    
    @property
    def tlon(self):
        return self._tlon

    @property
    def tlat(self):
        return self._tlat
    
    @lon.setter
    def lon(self, longitude):
        if not longitude.max() <= 360 or not longitude.min()>=-180:
            raise AttributeError("longitude out of range")
        self._lon = convertLon(longitude)
        
    @lat.setter
    def lat(self, latitude):
        if not latitude.max() <= 90 or not latitude.min()>=-90:
            raise AttributeError("latitude out of range")
        self._lat = latitude
        
    @staticmethod
    def _trim_coord(coord, trim_coord):
        assert coord.min() <= trim_coord[0] and coord.max() >= trim_coord[1], "Bound out of limits"
        tcoord = np.where((coord >= trim_coord[0]) & (coord <= trim_coord[1]))
        coord = coord[tcoord]
        return coord, tcoord[0]
        
if __name__ == "__main__":    
    filename = "/home/pzaninelli/TRABAJO/IGEO/comparacion/land_sea_mask_6h_era_5_01011979-31121979_2_5.nc"
    with Dataset(filename) as nc:
        lon = nc.variables["longitude"][:]
        lon = (((lon + 180) % 360) - 180)
        lon.sort()
        lat = nc.variables["latitude"][:]
        lsm = nc.variables["lsm"][0,:,:]
        coord = coorobj(lon,lat, trim_lon=[-22, 45], trim_lat=[27,72]) # Euro-CORDEX domain
        ilat, ilon = coord.getInd()
        
        ilat2, ilon2 = coord.getInd(filemask=filename,
                                    mNCLatName="latitude", 
                                    mNCLonName="longitude", 
                                    mNCVarName="lsm")