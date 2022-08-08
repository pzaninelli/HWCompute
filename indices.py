#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compute heatwave indexes from .csv file
@author: Pablo G Zaninelli
"""

import pandas as pd
import xarray as xr
from os.path import exists as path_exists
import warnings
import re
import time
from functools import partial
from optparse import OptionParser, OptionGroup
from multiprocessing import Pool, cpu_count
from period import Monthly, Seasonal, Annual, UserPeriod


parser = OptionParser(usage="usage: %prog  [options] ",\
                      version='%prog v0.0.0')
    
# general options
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
# groupal options
query_opts=OptionGroup(parser,'Query Options',"These options control the query mode")


# metrics
query_opts.add_option("-m", "--metric", dest="metric", action="store",
    default="all", 
    help="Metric to compute. Optons are 'all', 'hwf', 'hwd', 'hwa' or 'hwm'")

# period
query_opts.add_option("-p", "--period", dest="period", action="store",
    default="all", 
    help="Period to compute metrics. Optons are 'all', 'monthly', 'annual', 'seasonal' or 'none'")

# moving period
query_opts.add_option("-P", "--Period", dest="sp", action="store",
    default=None, help="Moving period to compute metrics.")

# output format
query_opts.add_option("-o", "--output", dest="output", action="store",
    default="netcdf", help="Output file format. It could be 'netcdf' or 'csv'.")

parser.add_option_group(query_opts)
(options, args) = parser.parse_args()


def postproc(met, formato, metric):
    df = pd.DataFrame({f"{metric}":met})
    ds = xr.Dataset.from_dataframe(df)
    ds = ds.transpose(df.index.names[2],"latitude","longitude")
    if formato == "csv":
        ds = ds.to_dataframe()
    return ds


def write(ds, formato, metric, period, mper):
    if mper == "None":
        Filename = "./" + metric + "_" + period + "."
    else:
        Filename = "./" + metric + "_Roll_" + mper + "days."
    if formato == "csv":
        ds.to_csv(Filename + "csv")
    elif formato == "netcdf":
        ds.to_netcdf(Filename + "nc")

        
def process2run(formato, process):
    print(f"***Process to run: {process}***\n")
    pattern_name = re.compile(r"\((.*?)\..*?\)\.(.*?)\((.*?)\)$")
    period = pattern_name.search(process).group(1)
    metric = pattern_name.search(process).group(2)
    mper = pattern_name.search(process).group(3)
    ds = eval(process)
    ds = postproc(ds, formato, metric)
    write(ds, formato, metric, period, mper)


def make_process(per, mper, metrics, filename):
    if not per == 'all' and not per == 'none':
        __ind = [f"{per.capitalize()}.from_file('{filename}')"]
    elif per == "all":
        __ind = [f"Monthly.from_file('{filename}')", 
             f"Seasonal.from_obj(Monthly.from_file('{filename}'))", 
             f"Annual.from_obj(Monthly.from_file('{filename}'))"]
    elif per == "none":
        __ind = [f"UserPeriod.from_file('{filename}')"]
    else:
        raise AttributeError(f"{per} is not a valid option!")


    if not metrics == 'all':
        __metric = [metrics]
    elif metrics == "all":
        __metric = ['hwf', 'hwd', 'hwa', 'hwm']
    else:
        raise AttributeError(f"{metrics} is not a valid metric!")
 
    process = []    
    for ii in (f"({x}).{y}({mper})" for x in __ind for y in __metric):
        process.append(ii)
            
    return process

    
def main():

    filename = args[0]
    per = options.period
    metrics = options.metric
    mper = options.sp   
    formato = options.output
    ncpu = cpu_count()
    
    if not formato in ["netcdf", "csv"]:
        raise AttributeError('Format not defined!')
    
    if not path_exists(filename):
        raise FileNotFoundError(f"{filename} does not exist!")
    
    
    if not mper is None and not per == "none":
        warnings.warn("period variables was set to 'none'")
        per = "none"
       
    process = make_process(per, mper, metrics, filename)
            
    process2run_p = partial(process2run, formato)
    
    if ncpu >=4:
        pool = Pool(4)   
    else:
        pool = Pool(ncpu)
    
    pool.map(process2run_p, process)
    pool.close()
    pool.join()
 
    
if __name__ == "__main__":
    start_time = time.time()
    print("Starting process...\n")
    main()
    print("***Process finished***\n")
    print("--- %s seconds ---" % (time.time() - start_time))