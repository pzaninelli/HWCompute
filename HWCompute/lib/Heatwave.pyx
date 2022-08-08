#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 12:30:43 2022

@author: pzaninelli
"""

import cython
import numpy as np
cimport numpy as np
# from libc.stdlib cimport malloc, free, qsort
from cython.parallel import prange, parallel
    

ctypedef np.float64_t DTYPE_ff_t
ctypedef np.float32_t DTYPE_f_t 
ctypedef np.int64_t DTYPE_i_t

@cython.boundscheck(False)
@cython.wraparound(False)
def hwstat(double[::1,:] arr, double[:] perc, int umbral = 3):
    
    cdef Py_ssize_t t = arr.shape[0]
    indS = np.zeros((arr.shape[0]),dtype=np.intc) # index of start hw
    indF = np.zeros((arr.shape[0]),dtype=np.intc) # index of end hw 
    exced = np.zeros((arr.shape[0]),dtype=np.double)
    indS.fill(-9)
    indF.fill(-9)
    cdef int[:] indS_view = indS 
    cdef int[:] indF_view = indF
    cdef double[:] exced_view = exced
    cdef int cont = 0
    cdef int chd = 0
    cdef Py_ssize_t i
    cdef int j
    # compute the start and end index of each hw event
    for i in range(t):
        j = int(arr[i,1])-1
        if arr[i,0] > perc[j]:
            chd += 1
            exced[i] = arr[i,0]-perc[j]
            if chd == umbral:
                indS_view[cont] = i-umbral +1
        elif arr[i,0] <= perc[j] and chd < umbral:
            chd = 0
        elif arr[i,0] <= perc[j] and chd >= umbral:
            indF_view[cont] = i
            cont += 1
            chd = 0
    cdef Py_ssize_t n = cont
    # compute statistics of hw
    acc = np.zeros((n),dtype=np.double)
    mean = np.zeros((n),dtype=np.double)
    maxi = np.zeros((n),dtype=np.double)
    mini = np.zeros((n),dtype=np.double)
    max_ex = np.zeros((n),dtype=np.double)
    sum_ex = np.zeros((n),dtype=np.double)
    # define the views
    cdef double[:] acc_view = acc
    cdef double[:] mean_view = mean
    cdef double[:] maxi_view = maxi
    cdef double[:] mini_view = mini
    cdef double[:] max_ex_view = max_ex
    cdef double[:] sum_ex_view = sum_ex
    if not cont == 0:
        for i in range(n):
            acc_view[i] = np.sum(arr[indS_view[i]:indF_view[i],0])
            mean_view[i] = acc_view[i]/(indF_view[i]-indS_view[i])
            maxi_view[i] = np.max(arr[indS_view[i]:indF_view[i],0])
            mini_view[i] = np.min(arr[indS_view[i]:indF_view[i],0])
            max_ex_view[i] = np.max(exced_view[indS_view[i]:indF_view[i]])
            sum_ex_view[i] = np.sum(exced_view[indS_view[i]:indF_view[i]])
    return indS[:cont], indF[:cont], acc, mean, maxi, mini, max_ex, sum_ex   