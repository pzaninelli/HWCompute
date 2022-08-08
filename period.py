#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 17:21:29 2022

@author: pzaninelli
"""
import pandas as pd
from abc import abstractmethod

class PeriodDF:
    
    def __init__(self, df, is_preproc = False):
        self._df = df
        self._is_preproc = is_preproc
        
    def preproc(self):
        self._df["start"] = pd.to_datetime(self._df["start"], errors = 'coerce')
        self._df["end"] = pd.to_datetime(self._df["end"], errors = 'coerce')
        self._df["year"] = self._df.start.dt.year
        self._df["month"] = self._df.start.dt.month
        self._df["season"] = self._df["month"]%12 // 3 + 1
        self._df["duration"] = self._df.end-self._df.start
        self._is_preproc = True
       
    @abstractmethod   
    def hwf(self, days):
        pass
    
    @abstractmethod   
    def hwd(self, days):
        pass
    
    @abstractmethod   
    def hwa(self, days):
        pass
    
    @abstractmethod   
    def hwm(self, days):
        pass
    
    @property
    def df(self):
        return self._df
    
    @df.setter
    def df(self, df):
        self._df = df

    @property
    def is_preproc(self):
        return self._is_preproc
    
    @is_preproc.setter
    def is_preproc(self,is_o_preproc):
        self._is_preproc = is_o_preproc

    @classmethod
    def from_file(cls, filename):
        df = pd.read_csv(filename)
        df = df.dropna()
        df = df.drop("Unnamed: 0",axis=1)
        return cls(df, False)
    
    @classmethod
    def from_obj(cls, obj):
        return cls(obj.df, obj.is_preproc)

    
class Monthly(PeriodDF):
    
    def __init__(self, df, is_preproc):
        super().__init__(df, is_preproc)
                
    def monthly(self):
        if not super().is_preproc:
            super().preproc()
        return self.df.groupby(["longitude","latitude","month"])
    
    def hwf(self, days = None):
        if not super().is_preproc:
            super().preproc()
        return self.monthly()["mean"].count()
    
    def hwd(self, days = None):
        if not super().is_preproc:
            super().preproc()
        return self.monthly()['duration'].max()
    
    def hwa(self, days = None):
        if not super().is_preproc:
            super().preproc()
        return self.monthly()["max_ex"].max()
    
    def hwm(self, days = None):
        if not super().is_preproc:
            super().preproc()
        return self.monthly()["sum_ex"].sum()
    

class Annual(PeriodDF):
    
    def __init__(self,df, is_preproc):
        super().__init__(df, is_preproc)
        
    def annual(self):
        if not super().is_preproc:
            super().preproc()
        return self.df.groupby(["longitude","latitude","year"])  
    
    def hwf(self, days = None):
        if not super().is_preproc:
            super().preproc()
        return self.annual()["mean"].count()
    
    def hwd(self, days = None):
        if not super().is_preproc:
            super().preproc()
        return self.annual()['duration'].max()
    
    def hwa(self, days = None):
        if not super().is_preproc:
            super().preproc()
        return self.annual()["max_ex"].max()
    
    def hwm(self, days = None):
        if not super().is_preproc:
            super().preproc()
        return self.annual()["sum_ex"].sum() 
      
    
class Seasonal(PeriodDF):
    def __init__(self,df, is_preproc):
        super().__init__(df, is_preproc) 
    
    def seasonal(self):
        if not super().is_preproc:
            super().preproc()
        return self.df.groupby(["longitude","latitude","season"])
 
    def hwf(self, days = None):
        if not super().is_preproc:
            super().preproc()
        return self.seasonal()["mean"].count()
 
    def hwd(self, days = None):
        if not super().is_preproc:
            super().preproc()
        return self.seasonal()['duration'].max()
 
    def hwa(self, days = None):
        if not super().is_preproc:
            super().preproc()
        return self.seasonal()["max_ex"].max()
 
    def hwm(self, days = None):
        if not super().is_preproc:
            super().preproc()
        return self.seasonal()["sum_ex"].sum() 
    

class UserPeriod(PeriodDF):
    def __init__(self,df, is_preproc):
        super().__init__(df, is_preproc) 
        
    def groupdays(self, days):
        assert days > 0, "days must be greater than zero"
        return self.df.set_index("start").groupby(["longitude","latitude",pd.Grouper(freq=(f"{days}D"))])
    
    def hwf(self, days):
        if not super().is_preproc:
            super().preproc()
        return self.groupdays(days)["mean"].count()
 
    def hwd(self,days):
        if not super().is_preproc:
            super().preproc()
        return self.groupdays(days)['duration'].max()
 
    def hwa(self, days):
        if not super().is_preproc:
            super().preproc()
        return self.groupdays(days)["max_ex"].max()
 
    def hwm(self, days):
        if not super().is_preproc:
            super().preproc()
        return self.groupdays(days)["sum_ex"].sum()