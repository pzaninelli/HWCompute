#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 16:33:40 2022

@author: pzaninelli
"""

import cython
import numpy as np
cimport numpy as np
# from libc.stdlib cimport qsort, malloc, free
from dayOfYear import retWinDay
from cython.parallel import prange

ctypedef np.float64_t DTYPE_ff_t
ctypedef np.float32_t DTYPE_f_t 
ctypedef np.int64_t DTYPE_i_t


# Comparation function needed for sorting
# cdef int mycmp(const void * pa, const void * pb) nogil:
#     cdef double a = (<double *>pa)[0]
#     cdef double b = (<double *>pb)[0]
#     if a < b:
#         return -1
#     elif a > b:
#         return 1
#     else:
#         return 0

# # Compute the percentile picking the lower interval. No interpolation.
# cdef double atomic_percentile(float *buf, int n, double perc) nogil:
#     cdef int i
#     cdef int index
#     cdef float result
    
        
#     # Sort the buffer
#     qsort(buf, n, sizeof(float), mycmp)
    
#     # cut of the percentile
#     index = int((<float>n) * perc / 100.0)
#     result = buf[index-1]

#     return result

@cython.boundscheck(False)
def percentileday(np.ndarray[DTYPE_f_t, ndim=1] arr, np.ndarray[DTYPE_i_t, ndim = 1] doy, int q, int win):
    cdef int n = 366
    cdef int L = arr.shape[0]
    cdef np.ndarray[DTYPE_i_t, ndim =1] retw = np.zeros(((win*2)+1)).astype(int)
    cdef np.ndarray[DTYPE_ff_t, ndim =1] result = np.empty((n)).astype(float)
    cdef np.ndarray[DTYPE_ff_t, ndim =1] buffer = np.empty((L)).astype(float)
    cdef int cont = 0
    
    for i in range(n):
        retw = retWinDay(i+1,win)       
        for w in range(retw.shape[0]):
            for l in range(L):
                buffer[l] = 0.0
                if retw[w] == doy[l]:
                    buffer[l] = arr[l]
                    cont += 1
        result[i] = np.percentile(buffer[:cont], q)
        cont = 0
       
    return result
    