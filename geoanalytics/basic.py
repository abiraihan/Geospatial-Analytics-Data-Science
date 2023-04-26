#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 02:08:14 2022

@author: araihan
"""

import numpy as np
import pyproj
import shapely
import fiona
from numpy.lib import recfunctions
import warnings
import geopandas as gpd
from geoanalytics.base.base import geoprocessing as gpr
from geoanalytics.core.core import cores
# import os
# os.chdir(os.path.abspath(os.getcwd()))
file = '/home/kali/Data/Panola/2022 Planting/Corn/Panola Farming_Panola_12_2022_DKC70-27 PRYME_1.shp'

polyPath = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Soil Sample/Panola Farming_South Panola_SP 12_2022_NO Product_1_poly.shp'
swath_poly_path = '/araihan/Reserach_Data/extracted_data/Panola Farming/processed_data/planting_point_swath_poly.shp'
planting = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Planting/Panola Farming_South Panola_SP 12_2022_P1718-PRYME_1.shp'
ecom = '/araihan/Reserach_Data/extracted_data/Panola Farming/ECOM/Panola Farming_South Panola_SP 12_NO Year_TSM_1.shp'
harvest = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Harvest/Panola Farming_South Panola_SP 12_2022_CORN_1.shp'


import collections
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier

# queryGeom = cores.remove_identical(polyPath, xycoords = True)

# harvesting = cores.remove_identical(harvest, xycoords = True)

pointdata = gpr.structured_numpy_array(file)

# plantpoint = gpr.structured_numpy_array(planting)

# unary_poly = shapely.ops.unary_union(queryGeom['geometry'])

# arrays = gridBounds(unary_poly, 4326)


# def getColumnLen(gridData:list, sourceCrs:int):
#     projection = lambda geog, proj : pyproj.Transformer.from_crs(
#         crs_from=pyproj.CRS.from_user_input(geog),
#         crs_to=pyproj.CRS.from_user_input(proj),
#         always_xy=True
#         ).transform
#     lengths = np.sqrt(shapely.ops.transform(projection(4326, 3857), gridData[0]).area)
#     getbnds = shapely.ops.unary_union(gridData)
#     projected_bound = shapely.ops.transform(
#         projection(4326, 3857),
#         getbnds)
    
#     minx, miny, maxx, maxy = projected_bound.bounds
    
#     return len(np.linspace(minx, maxx, int(abs(minx-maxx)/int(lengths)))) - 1

# d = getColumnLen(arrays[0]['geometry'], queryGeom.EPSG)



# join = cores.SpatialJoin(polyPath, plantpoint, 'intersects', *['Rt_Apd_Ct_'])
# njoin = gpr.SpatialJoin(join, harvesting, 'intersects', *['Yld_Vol_Dr', 'Time'])
# snjoin = gpr.SpatialJoin(njoin, pointdata, 'intersects', *['R4_mS_m_', 'rWTC___', 'D2I_m_'])
# pnjoin = gpr.SpatialJoin(snjoin, plantpoint, 'intersects', *['Rt_Apd_Ct_'])

# griData = arrays[0]

# cols, rows = arrays[1]

# f8 = {i: j for i, j in pnjoin.dtype.descr if np.dtype(j).kind in ['i', 'f']}
# idx = {i:list(f8.keys()).index(i) for i, j in f8.items()}
# final_nparray = pnjoin[list(idx.keys())]
# join = gpr.SpatialJoin(arrays[0], queryGeom, 'intersects')


# uxi = {i:(i, j) for i, j in pnjoin.dtype.descr if np.dtype(j).kind in ['U', 'M']}
# uidx = {j:list(uxi.keys()).index(i) for i, j in uxi.items()}
# final_array = pnjoin[[i[0] for i in uidx.keys()]]
# stack_uarray = np.stack([np.flipud(np.reshape(final_array[i], (cols, -1)).T) for i in final_array.dtype.names])

# stack_array = np.stack([np.flipud(np.reshape(final_nparray[i], (cols, -1)).T) for i in final_nparray.dtype.names])

# def KNC(multiArray, index):
    
#     nrow, ncol = multiArray[index].shape
#     frow, fcol = np.where(np.isfinite(multiArray[index]))
    
#     train_X, train_y = [[frow[i], fcol[i]] for i in range(len(frow))], multiArray[index][frow, fcol]
    
#     knn = KNeighborsClassifier(n_neighbors= 5, weights='distance', algorithm='ball_tree', p=2)
#     knn.fit(train_X, train_y)
    
#     r2 = knn.score(train_X, train_y)
#     print("R2- {}".format(r2))
#     X_pred = [[r, c] for r in range(int(nrow)) for c in range(int(ncol))]
    
#     y_pred = knn.predict(X_pred)
#     karray = np.zeros((nrow, ncol))
#     i=0
#     for r in range(int(nrow)):
#         for c in range(int(ncol)):
#             karray[r, c] = y_pred[i]
#             i += 1
#     return karray

# def KNR(multiArray, index):
    
#     nrow, ncol = multiArray[index].shape
#     frow, fcol = np.where(np.isfinite(multiArray[index]))
    
#     train_X, train_y = [[frow[i], fcol[i]] for i in range(len(frow))], multiArray[index][frow, fcol]
    
#     knn = KNeighborsRegressor(n_neighbors= 5, weights='distance', algorithm='ball_tree', p=2)
#     knn.fit(train_X, train_y)
    
#     r2 = knn.score(train_X, train_y)
#     print("R2- {}".format(r2))
#     X_pred = [[r, c] for r in range(int(nrow)) for c in range(int(ncol))]
    
#     y_pred = knn.predict(X_pred)
#     karray = np.zeros((nrow, ncol))
#     i=0
#     for r in range(int(nrow)):
#         for c in range(int(ncol)):
#             karray[r, c] = y_pred[i]
#             i += 1
#     return karray

# data = griData
# for name, index in idx.items():
#     vals = np.fliplr(KNR(stack_array, index).T).reshape([stack_array[index].size, 1]).flatten()
#     st_array = np.array([vals], dtype = [(name, np.float64)])
#     data = recfunctions.merge_arrays(
#         [data, st_array],
#         fill_value = np.nan,
#         flatten=True,
#         usemask=False
#         )
#     print(name)

# datas = griData
# for name, index in uidx.items():
#     vals = np.fliplr(KNC(stack_uarray, index).T).reshape([stack_uarray[index].size, 1]).flatten()
#     st_array = np.array([vals], dtype = [name])
#     datas = recfunctions.merge_arrays(
#         [datas, st_array],
#         fill_value = np.nan,
#         flatten=True,
#         usemask=False
#         )
#     print(name[0])


# import matplotlib.pyplot as plt
# plt.imshow(B)

# res = (-91.2665025302993 - 32.9188277330139) / 0.0001
# from rasterio.transform import from_origin
# import rasterio

# transform = from_origin(-91.2665025302993 , 32.9188277330139, res, res)
# path =  '/araihan/Reserach_Data/extracted_data/Panola Farming/processed_data/tifFile.tiff'
# new_dataset = rasterio.open(path, 'w', driver='GTiff',
#                             height=d.shape[0], width=d.shape[1], count=1, dtype=d.dtype,
#                             crs='EPSG:4326', transform=transform, nodata=np.nan)
# new_dataset.write(d, 1)
# new_dataset.close()

