#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 02:08:14 2022

@author: araihan
"""

import numpy as np
import shapely
import fiona

from base.base import geoprocessing
polyPath = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Soil Sample/Panola Farming_South Panola_SP 12_2022_NO Product_1_poly.shp'
swath_poly_path = '/araihan/Reserach_Data/extracted_data/Panola Farming/processed_data/planting_point_swath_poly.shp'
ecom = '/araihan/Reserach_Data/extracted_data/Panola Farming/ECOM/Panola Farming_South Panola_SP 12_NO Year_TSM_1.shp'

# polydata, polyprof = geoprocessing.structured_numpy_array(polyPath)

# swath_polydata, polyprof = geoprocessing.structured_numpy_array(swath_poly_path)

# pointdata, polyprof = geoprocessing.structured_numpy_array(ecom)


data = np.array(np.arange(0, 500),
                dtype = [('lat', np.float64), ('lon', np.float64), ('score', np.intp), ('coef', np.float64)])

loc = [shapely.geometry.Point(i) for i in data[['lat', 'lon']]]



# x_axis = np.arange(0, 24)
# y_axis = np.tile(0, 24)

# arr = np.array([x_axis, y_axis]).T

# poly = []
# for i, j in enumerate(arr):
#     print(i)
#     if i < len(arr) - 1:
#         bnds = (arr[i][0], arr[i][1],  arr[i+1][0], arr[i+1][1])
#         pl = shapely.geometry.box(*bnds)
#         poly.append(pl)
#         print(bnds)
import geopandas as gpd
# f = gpd.GeoSeries(data = poly)
# f.plot()

# z = gpd.GeoSeries(data = [shapely.geometry.box(*i) for i in [(0, 0, 1, 1),
#                                                              (1, 1, 2, 2),
#                                                              (1, 0, 2, 1),
#                                                              (0, 1, 1, 2)]])
# z.plot(cmap = 'Spectral_r')

x, y = np.meshgrid(np.linspace(0, 100,11), np.linspace(0, 100,11))
d = np.array([x, y]).T

poi = []

for i in d:
    for k in i:
        p =shapely.geometry.Point(k[0], k[1])
        poiI am here.append(p)

f = gpd.GeoSeries(data = poi)
f.plot()