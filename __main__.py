#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul  5 10:05:58 2022
main program
@author: Pablo G. Zaninelli
"""
import time
from optparse import OptionParser, OptionGroup
import os
import sys
from HWCompute.ParamsInit import ParamsInit
from HWCompute.hw import hwbpointNC


parser = OptionParser(usage="usage: %prog  [options] ",\
                      version='%prog v0.0.0')
    
# general options
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
# groupal options
query_opts=OptionGroup(parser,'Query Options',"These options control the query mode")

# file in to take the parameters
query_opts.add_option("-p", "--params", dest="file", action="store",
    default="parameters/params.ini", help=".ini file to take the parameters")

# confimation message?
query_opts.add_option("-c", "--noconfirm", dest="conf", action="store_true",
    default=False, help="no confirmation message")

parser.add_option_group(query_opts)
(options, args) = parser.parse_args()


os.chdir(os.path.dirname(__file__)) # change dir to the current file

__bothTemp, __tmax, __tmin, __daily = "T2maxmin", "T2max", "T2min", "Daily"

def confirmation():
    should_continue = False
    count = 1
    while True:
        if count == 10:
            print("Run the script again!\n")
            break
        option = str(input("If your request is OK press yes[Y/y] otherwise cancel[C/c]: "))
        if option.upper()=='Y':
            print("Starting process...\n")
            should_continue = True
            break
        elif option.upper()=='C':
            print("Process stopped!")
            break
        else:
            print("Incorrect option\n")
            continue
        count += 1
    return should_continue

def set_parameters_from_ini(filename = options.file):
    return ParamsInit.from_file(filename)

def compute_hw(params, isDaily, Tmax = True):
    HW = hwbpointNC(ncFile = params.dir_in, 
                  main_var = params.mainvar_nc_name, 
                  time_var = params.time_nc_name,
                  lon_var = params.lon_nc_name, 
                  lat_var = params.lat_nc_name, 
                  tmax = Tmax,
                  daily = isDaily,
                  kelvin = params.is_kelvin,
                  filemask = params.file_mask,
                  mNCVarName = params.mainvar_nc_mask, 
                  mNCLatName = params.lat_nc_name, 
                  mNCLonName = params.lon_nc_name, 
                  trim_lat = params.trimlat,
                  trim_lon = params.trimlon,
                  ncpu = params.ncpu,
                  q = params.percentile_threshold,
                  window = params.window_width, 
                  umbral = params.persistence_hw, 
                  yStartP = params.start_year,
                  yEndP = params.end_year)
    return HW

def main():
    params = set_parameters_from_ini()
    print(params)
    
    if options.conf:
        should_continue = True
    else:
        should_continue = confirmation()
 
    if not should_continue:
        sys.exit(0) 
    if params.variable[0] == __tmax:
        print(params.variable[0])
        hwdf = compute_hw(params, isDaily=False)
        hwdf.to_csv(params.dir_out + "HW_T2max.csv")
    elif params.variable[0] == __tmin:
        print(params.variable[0])
        hwdf = compute_hw(params, isDaily=False, Tmax = False)
        hwdf.to_csv(params.dir_out + "HW_T2min.csv")
    elif params.variable[0] == __bothTemp:
        print(__tmax)
        hwdf_tmax = compute_hw(params, isDaily=False)
        hwdf_tmax.to_csv(params.dir_out + "HW_T2max.csv")
        print("**************\n")
        print(__tmin)
        hwdf_tmin = compute_hw(params, isDaily=False, Tmax = False)
        hwdf_tmin.to_csv(params.dir_out + "HW_T2min.csv")
    elif params.variable[0] == "Daily":
        print(__daily)
        hwdf = compute_hw(params, isDaily=True)
        hwdf.to_csv(params.dir_out + "HW_daily.csv")
        
if __name__ == "__main__":
    start_time = time.time()
    print("Starting process...\n")
    main()
    print("***Process finished***\n")
    print("--- %s seconds ---" % (time.time() - start_time))