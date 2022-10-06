#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 04:42:24 2022

@author: araihan
"""

import numpy as np
# import os
# os.chdir(os.path.abspath(os.getcwd()))
import shapely
# from base import base
from base.base import geoprocessing as gpr
import pyproj
from sklearn.neighbors import KNeighborsRegressor

projection = lambda geog, proj : pyproj.Transformer.from_crs(
    crs_from=pyproj.CRS.from_user_input(geog),
    crs_to=pyproj.CRS.from_user_input(proj),
    always_xy=True
    ).transform

polyPath = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Soil Sample/Panola Farming_South Panola_SP 12_2022_NO Product_1_poly.shp'
swath_poly_path = '/araihan/Reserach_Data/extracted_data/Panola Farming/processed_data/planting_point_swath_poly.shp'
ecom = '/araihan/Reserach_Data/extracted_data/Panola Farming/ECOM/Panola Farming_South Panola_SP 12_NO Year_TSM_1.shp'

# polydata, polyprof = gpr.structured_numpy_array(polyPath)

# swath_polydata, polyprof = geoprocessing.structured_numpy_array(swath_poly_path)

pointdata, polyprof = gpr.structured_numpy_array(ecom)

# points_data = [shapely.ops.transform(projection(4326, 3857),i) for i in pointdata['geometry']]

unary_point = shapely.ops.unary_union(pointdata['geometry'])


bnds_bx = shapely.geometry.box(*unary_point.bounds).buffer(0.0001)

xmin, ymin, xmax, ymax = unary_point.bounds

# y, x = ((3883819.028850466, 3884534.485259546), (-10159743.755770503, -10159271.336574398))

# ymin, ymax = y
# xmin, xmax = x

# self.gdf=gdf
# self.attribute = attribute
# self.x = gdf.geometry.x.values
# self.y = gdf.geometry.y.values
# self.z = gdf[attribute].values
# self.crs = gdf.crs
# self.xmax = gdf.geometry.x.max()
# self.xmin = gdf.geometry.x.min()
# self.ymax = gdf.geometry.y.max()
# self.ymin = gdf.geometry.y.min()
extent = (xmin, xmax, ymin, ymax)
res = (xmax - xmin) / 100
ncol = int(np.ceil((xmax - xmin) / res))
nrow = int(np.ceil((ymax - ymin) /res))
print(ncol, nrow, res)
x = [i.x for i in pointdata['geometry']]
y = [i.y for i in pointdata['geometry']]
z = [i for i in pointdata['R4_mS_m_']]

hrange = ((ymin,ymax),(xmin,xmax))
zi, yi, xi = np.histogram2d(
    y, x, bins=(int(nrow), int(ncol)),
    weights=z, normed=False,range=hrange)
counts, _, _ = np.histogram2d(
    y, x, bins=(int(nrow), int(ncol)),
    range=hrange)
np.seterr(divide='ignore',invalid='ignore')
zi = np.divide(zi,counts)
np.seterr(divide=None,invalid=None)
zi = np.ma.masked_invalid(zi)
array = np.flipud(np.array(zi))


#Prediction
X = []
frow, fcol = np.where(np.isfinite(array))
for i in range(len(frow)):
    X.append([frow[i], fcol[i]])
y = array[frow, fcol]
train_X, train_y = X, y
knn = KNeighborsRegressor(
    n_neighbors=5, weights='uniform',
    algorithm='brute', p=2)
knn.fit(train_X, train_y)
X_pred = []
for r in range(int(nrow)):
    for c in range(int(ncol)):
        X_pred.append([r, c])
y_pred = knn.predict(X_pred)
karray = np.zeros((nrow, ncol))
i = 0
for r in range(int(nrow)):
    for c in range(int(ncol)):
        karray[r, c] = y_pred[i]
        i += 1


