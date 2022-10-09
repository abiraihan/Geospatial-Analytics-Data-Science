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
from base.base import geoprocessing as gpr
from core.core import cores
import os
os.chdir(os.path.abspath(os.getcwd()))

def gridBounds(
        polyBounds:shapely.geometry.base.BaseGeometry,
        polyCRS:int,
        sideLength:(float, int) = 10,
        reproject:bool = False
        )->np.ndarray :
    """

    Parameters
    ----------
    polyBounds : shapely.geometry.base.BaseGeometry
        - a valid shapely geometry
    polyCRS : int
        - EPSG code as int
    sideLength : (float, int), optional
        -The default is 10 which is in meter based on EPSG:3857
    reproject : bool, optional
        - If reproject is True then peojection will be as the polyCRS EPSG defined else,
            it will return EPSG as 3857 which is a projected CRS in meter

    Raises
    ------
    TypeError
        - If polyBounds is not a valid shapely geometry
    ValueError
        1. If polyBounds is a empty geometry
        2. If reprojection on 2D surface for EPSG:3857 is out of a valid extent

    Returns
    -------
    numpy.ndarray
        - Structured numpy.ndarray of shapely geometry 

    """
    if not isinstance(polyBounds, shapely.geometry.base.BaseGeometry):
        raise TypeError("{} not a valid geometry type".format(type(polyBounds)))
    if getattr(polyBounds, 'is_empty'):
        raise ValueError("{} is an empty geometry".format(polyBounds))
    
    projection = lambda geog, proj : pyproj.Transformer.from_crs(
        crs_from=pyproj.CRS.from_user_input(geog),
        crs_to=pyproj.CRS.from_user_input(proj),
        always_xy=True
        ).transform
    projected_bound = shapely.ops.transform(
        projection(polyCRS, 3857),
        polyBounds)
    if float('inf') in projected_bound.bounds:
        raise ValueError("{} geometry extent is not a valid one,\
                          please set a valid geometry".format(projected_bound.bounds))
    minx, miny, maxx, maxy = projected_bound.bounds
    x = np.linspace(minx, maxx, int(abs(minx-maxx)/sideLength))
    y = np.linspace(miny, maxy, int(abs(miny-maxy)/sideLength))
    ncol, nrow = len(x)-1, len(y)-1

    hlines = [((xi, yi), (xj, yi)) for xi, xj in zip(x[:-1], x[1:]) for yi in y]
    vlines = [((xi, yi), (xi, yj)) for yi, yj in zip(y[:-1], y[1:]) for xi in x]
    
    grid_geoms = list(
        shapely.ops.polygonize(
            shapely.geometry.MultiLineString(
                hlines+vlines
                )
            )
        )
    if reproject:
        return np.array(
            grid_geoms,
            dtype = [('geometry', object)]
            ), (ncol, nrow)

    return np.array(
        [shapely.ops.transform(
            projection(
                3857,
                polyCRS
                ), i)
            for i in grid_geoms],
        dtype = [('geometry', object)]
        ), (ncol, nrow)

polyPath = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Soil Sample/Panola Farming_South Panola_SP 12_2022_NO Product_1_poly.shp'
swath_poly_path = '/araihan/Reserach_Data/extracted_data/Panola Farming/processed_data/planting_point_swath_poly.shp'
planting = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Planting/Panola Farming_South Panola_SP 12_2022_P1718-PRYME_1.shp'
ecom = '/araihan/Reserach_Data/extracted_data/Panola Farming/ECOM/Panola Farming_South Panola_SP 12_NO Year_TSM_1.shp'
harvest = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Harvest/Panola Farming_South Panola_SP 12_2022_CORN_1.shp'


import collections
from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier

queryGeom = cores.remove_identical(polyPath, xycoords = True)

# harvesting = cores.remove_identical(harvest, xycoords = True)

# pointdata = gpr.structured_numpy_array(ecom)

# plantpoint = gpr.structured_numpy_array(planting)

unary_poly = shapely.ops.unary_union(queryGeom['geometry'])

arrays = gridBounds(unary_poly, 4326)


def getColumnLen(gridData:list, sourceCrs:int):
    projection = lambda geog, proj : pyproj.Transformer.from_crs(
        crs_from=pyproj.CRS.from_user_input(geog),
        crs_to=pyproj.CRS.from_user_input(proj),
        always_xy=True
        ).transform
    getbnds = shapely.ops.unary_union(gridData)
    projected_bound = shapely.ops.transform(
        projection(4326, 3857),
        getbnds)
    
    minx, miny, maxx, maxy = projected_bound.bounds
    
    return len(np.linspace(minx, maxx, int(abs(minx-maxx)/10))) - 1





# join = gpr.SpatialJoin(arrays[0], queryGeom, 'intersects', *['Soil_pH__1', 'P_lb_ac_', 'K_lb_ac_', 'Soil_CEC_m', 'Soil_OM___'])
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

