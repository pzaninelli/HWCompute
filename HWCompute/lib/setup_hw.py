#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 21:41:44 2022

@author: pzaninelli
"""

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import numpy

# To compile: python setup.py build_ext --inplace

ext_modules = [
    Extension(
        "Heatwave",
        ["Heatwave.pyx"],
        extra_compile_args=['-fopenmp'],
        extra_link_args=['-fopenmp'],
        include_dirs=[numpy.get_include()],
    )
]

setup(
    name='Heatwave',
    ext_modules=cythonize(ext_modules),
    include_dirs=[numpy.get_include()]
)