# HWCompute

This program computes heatwaves events (HW).

A heatwave is defined as an uninterrupted period with extreme temperatures above a given (percentile-based) threshold. This percentile, which is calculated locally with a running window centered on each day of year, and the minimum duration (in days) required to define a heatwave are user-defined. The definition can be applied to maximum temperature (hot days), minimum temperature (hot nights), or both (hot days and nights).

To pass the arguments to the program, you have to fill in a *.ini* located at

```Bash
HWCompute/parameters/params.ini
```
To run

```Bash
python HWCompute
```
To see the possible options, use the "-h" option to see the help:

```Bash
python HWCompute -h
```
The output is a *csv* file with the following columns: *longitude*, *latitude*, *start* (start date), *end* (end date), *accumulated* (accumulated temperature in ºC), *mean* (mean temperature in ºC), *maxtemp* (maximum temperature recorded for each HW), *mintemp* (minimum temperature recorded for each HW), *max_ex* (maximum exceedence respect to the threshold in ºC) and *sum_ex* (accumulated exceedence respect to the threshold in ºC). 

Furthermore, the **inidices.py** script can be used to compute the HW statistics of [HWStat](https://github.com/pzaninelli/HWStat). To see the options:

```Bash
python /HWCompute/indices.py -h
```
