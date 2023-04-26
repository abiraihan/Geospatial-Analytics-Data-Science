#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 00:29:24 2023

@author: kali
"""

file = '/home/kali/Data/Panola/2022 Planting/Corn/Panola Farming_Panola_12_2022_DKC70-27 PRYME_1.shp'

from georead.georead import geotranslate

df = geotranslate(file)

dfs = df.crs

print(dfs)
