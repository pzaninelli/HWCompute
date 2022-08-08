#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 13:44:34 2022

@author: Pablo G. Zaninelli
"""

import numpy as np

class dayc:
    
    def __init__(self, day = int(1)):
        assert day >=1 and day <= 366, "Day is define between 1 and 366"
        self._day = day
        
    def __add__(self, o):
        if self._day + o.day > 366:
            return self._day + o.day - 366
        else:
            return self._day + o.day
        
    def __sub__(self, o):
        if self._day - o.day <=0:
            return self._day - o.day + 366
        else:
            return self._day - o.day
        
    def __str__(self):
        return f"{self.day}"
    
    @property
    def day(self):
        return self._day
    

class dayIter:
    
    def __init__(self, dlow, dhigh):
        assert dlow >= 1 and dlow <= 366, "low must be between 1 and 366"
        assert dhigh >= 1 and dhigh <= 366, "high must be between 1 and 366" 
        self._dlow = dlow
        self._dcurrent = dlow-1
        self._dhigh = dhigh
        self.auxhigh = 366 + self._dhigh
        self.auxcurr = self._dlow
        
    def __iter__(self):
        return self
    
    def __next__(self):
        self._dcurrent += 1
        if self._dlow > self._dhigh:
          
          if self.auxcurr > self.auxhigh:
              raise StopIteration
          else:
              self.auxcurr += 1
        else:
          if self._dcurrent > self._dhigh:
              raise StopIteration
              
        if self._dcurrent > 366:
           self._dcurrent = 1
        return self._dcurrent
    
def retWinDay(day_of_year, window):
    doy =  dayc(day_of_year)
    win = dayc(window)
    i0, ie = doy - win, doy + win
    return np.array([ii for ii in dayIter(i0,ie)])