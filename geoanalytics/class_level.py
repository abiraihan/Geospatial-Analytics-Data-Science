#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 15 22:27:57 2022

@author: araihan
"""

from georead.georead import geotranslate
from base.base import geoprocessing

class analytics(type):
    __repr__ = lambda cls : cls.__name__
    
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)

tics=analytics("Geoanalytics", (geotranslate, geoprocessing, ), {'filepaths': None})

data = analytics("Geoanalytics", (object, ), {})
        
# class geos:
    
#     global class_name
#     class_name = analytics("Geoanalytics", (object, ), {})
    
#     def __init__(cls, **kwargs):
#         for key, values in kwargs.items():
#             print(key)
#             setattr(class_name, key, values)

files ='/home/kali/WorkEasy/2022 Investor Report Data/organized_by_investor/Maritz Investments/boundary/Brown_Brown_Cashup_NO Year_NO Product_1_poly.shp'

# geodata = geos(file = files)


class Geo(str):
    
    def __new__(cls, o):
        return geotranslate(o)
    

x = Geo(files)
        
