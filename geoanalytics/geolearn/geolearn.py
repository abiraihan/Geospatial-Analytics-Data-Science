#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 03:29:03 2022

@author: araihan
"""

from sklearn.neighbors import KNeighborsRegressor, KNeighborsClassifier
from georead.georead import geotranslate
from geotransform.geotransform import spatialGrid
from core.core import cores, spatialstack
import numpy as np
import pandas as pd
polyPath = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Soil Sample/Panola Farming_South Panola_SP 12_2022_NO Product_1_poly.shp'
swath_poly_path = '/araihan/Reserach_Data/extracted_data/Panola Farming/processed_data/planting_point_swath_poly.shp'
planting = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Planting/Panola Farming_South Panola_SP 12_2022_P1718-PRYME_1.shp'
ecom = '/araihan/Reserach_Data/extracted_data/Panola Farming/ECOM/Panola Farming_South Panola_SP 12_NO Year_TSM_1.shp'
harvest = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Harvest/Panola Farming_South Panola_SP 12_2022_CORN_1.shp'

poly_data = geotranslate(polyPath)
grids = spatialGrid.squaregrid(poly_data.unary_union, poly_data.crs, sideLength = 10)

# lens = spatialGrid.getShape(grids)

planting_data = geotranslate(swath_poly_path)

harvest_data = geotranslate(harvest)
ecom_data = geotranslate(ecom)

spjoin = cores.SpatialJoin(grids, planting_data, 'intersects', *['Rt_Apd_Ct_', 'Product___', 'Date'])
spjoin1 = cores.SpatialJoin(spjoin, poly_data, 'intersects', *['Soil_pH__1', 'P_lb_ac_', 'K_lb_ac_', 'Soil_CEC_m', 'Soil_OM___'])
spjoin2 = cores.SpatialJoin(spjoin1, harvest_data, 'intersects', *['Yld_Vol_Dr', 'Moisture__', 'Date'])
spjoin3 = cores.SpatialJoin(spjoin2, ecom_data, 'intersects', *['R4_mS_m_', 'rWTC___', 'D2I_m_'])

stack_array = spatialstack(spjoin3)
