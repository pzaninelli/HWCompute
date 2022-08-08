#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 16:01:42 2022

@author: Pablo G Zaninelli
"""
 
import numpy as np
import warnings
from HWCompute.dayOfYear import retWinDay

def checkAllNAN(arr):
    return np.isnan(arr).all()

def checkAnyNAN(arr):
    return np.isnan(arr).any()

def percentile(arr, perc):
    if checkAnyNAN(arr):
        warnings.warn("The time series contains NaN values!")
        return np.nanpercentile(arr, perc)
    else:
        return np.percentile(arr,perc)

def dayPerc(df, q, window,  yStartP, yEndP):
    assert window <= 180, "the maximum window allowed is 180 days"
    perc = np.zeros((366))
    for iday in np.arange(1,366+1):
        c = retWinDay(iday, window)
        indices = np.where(np.in1d(df[(df.index.year>=yStartP) & (df.index.year <= yEndP)].doy,
                                   c))[0]
        perc[iday-1] = percentile(df.temp[indices],q)    
    return perc

def heatwave2( arr, perc, umbral = 3):
    indS = np.empty((arr.shape[0])) # index of start hw
    indF = np.empty((arr.shape[0])) # index of end hw 
    indS.fill(np.nan)
    indF.fill(np.nan)
    n = arr.shape[0]
    cont = 0
    chd = 0
       
    for i in range(n):
        if arr[i] > perc:
            chd += 1
            if chd == umbral:
               indS[cont] = i-umbral +1
        elif arr[i] <= perc and chd >= umbral:
            indF[cont] = i
            cont += 1
            chd = 0
    
    return indS[:cont].astype(int), indF[:cont].astype(int)