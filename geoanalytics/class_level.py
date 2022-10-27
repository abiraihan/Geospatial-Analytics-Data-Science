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
        instances = super().__new__(cls, *args, **kwargs)
        return instances

# Geoanalytics=analytics("Geoanalytics", (translate, geoprocessing, ), {})

# data = analytics("Geoanalytics", (object, ), {'files':None})
        
class geos:
    
    global class_name
    class_name = analytics("Geoanalytics", (object, ), {})
    
    def __init__(cls, **kwargs):
        for key, values in kwargs.items():
            print(key)
            setattr(class_name, key, values)
            
    def __repr__(cls):
        return "{}".format(class_name)
    
    @property
    def data(cls):
        class_name.translate = geotranslate(class_name.geofile)
        class_name.process = geoprocessing
        return class_name


files ='/araihan/Reserach_Data/extracted_data/Panola Farming/processed_data/planting_point_swath_poly.shp'

geodata =geos(geofile = files).data