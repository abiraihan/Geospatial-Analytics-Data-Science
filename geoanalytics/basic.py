#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 02:08:14 2022

@author: araihan
"""
import re
import numpy as np
import pyproj
from numpy.lib import recfunctions
import shapely
import fiona
import warnings
import geopandas as gpd
# from base.spatialquery import spatialquery
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

from sklearn.neighbors import KNeighborsRegressor
ff = cores.remove_identical(harvest, xycoords = False)
fs = cores.remove_identical(polyPath, xycoords = False)
# polydata = gpr.structured_numpy_array(polyPath)
# pointdata = gpr.structured_numpy_array(ecom)
# harvestpoint = gpr.structured_numpy_array(harvest)

# unary_poly = shapely.ops.unary_union(polydata['geometry'])

# arrays = gridBounds(unary_po'Elevation_''Elevation_'ly, 4326)

# griData = arrays[0]

# cols, rows = arrays[1]

# join = gpr.SpatialJoin(arrays[0], pointdata, 'intersects', *['R4_mS_m_', 'rWTC___', 'D2I_m_'])

# njoin = gpr.SpatialJoin(join, harvestpoint, 'intersects', *['Yld_Vol_Dr', 'Elevation_'])

# print(join.dtype.names)

# az = gpd.GeoSeries(data=join['geometry'], crs = 'EPSG:4326')
# az = gpd.GeoDataFrame(data = join[['R4_m___mean', 'rWTC__mean', 'D2I___mean']], geometry = az)

# az.plot(column = 'R4_m___mean', figsize = (5,5),linewidth = 1, cmap = 'tab20', edgecolor = 'k')

# A = np.flipud(np.reshape(join['D2I___mean'], (cols, -1)).T)
# B = np.flipud(np.reshape(join['rWTC__mean'], (cols, -1)).T)
# C = np.flipud(np.reshape(join['R4_m___mean'], (cols, -1)).T)

# array_dict = {
#     'D2I___mean' : 0,
#     'rWTC__mean' : 1,
#     'R4_m___mean' : 2
#     }

# arr = np.stack([A, B, C])

def KNeighborArray(multiArray, index):
    
    nrow, ncol = multiArray[index].shape
    frow, fcol = np.where(np.isfinite(multiArray[index]))
    
    train_X, train_y = [[frow[i], fcol[i]] for i in range(len(frow))], multiArray[index][frow, fcol]
    
    knn = KNeighborsRegressor(n_neighbors= 5, weights='uniform', algorithm='kd_tree', p=2)
    knn.fit(train_X, train_y)
    
    r2 = knn.score(train_X, train_y)
    print("R2- {}".format(r2))
    X_pred = [[r, c] for r in range(int(nrow)) for c in range(int(ncol))]
    
    y_pred = knn.predict(X_pred)
    karray = np.zeros((nrow, ncol))
    i=0
    for r in range(int(nrow)):
        for c in range(int(ncol)):
            karray[r, c] = y_pred[i]
            i += 1
    return karray

# d2i = KNeighborArray(arr, array_dict['D2I___mean'])
# print(B)
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

