#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  7 16:43:36 2022

@author: pzaninelli
"""

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy

# To compile: python setup.py build_ext --inplace

ext_modules = [
    Extension(
        "Percentile",
        ["percentile.pyx"],
        extra_compile_args=['-fopenmp'],
        extra_link_args=['-fopenmp'],
        include_dirs=[numpy.get_include()],
    )
]

setup(
    name='Percentile',
    ext_modules=cythonize(ext_modules),
    include_dirs=[numpy.get_include()]
)
