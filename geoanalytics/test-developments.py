#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:23:09 2022

@author: raihan
"""
from spatialquery import SpatialQuery, RtreeQuery
import os
import re
import fiona
import random
import pyproj
import warnings
import numpy as np
from osgeo import osr
from tqdm import tqdm
from collections import OrderedDict
from core import geoprocessing
from shapely.geometry import Polygon, mapping, MultiPolygon, shape
from shapely.ops import transform
from sklearn.linear_model import LinearRegression
import zipfile
import numpy.lib.recfunctions as rfn
import shapely
from shapely.strtree import STRtree
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
# findFile = lambda dirs, ext:[os.path.join(dirs, i) for i in os.listdir(dirs) if os.path.splitext(i)[1] == str('.'+(ext))]

# zipExtract = lambda zipfiles, outDirs : zipfile.ZipFile(zipfiles, 'r').extractall(outDirs)

def extractPath(dataDirs, ext):
    findFile = lambda dirs, ext:[os.path.join(dirs, i) for i in os.listdir(dirs) if os.path.splitext(i)[1] == str('.'+(ext))]
    parentPath, subfolder, _ = [i for i in os.walk(dataDirs)][1]
    return {i : findFile(f"{parentPath}/{i}", ext) for i in subfolder}


def createPoly(sourcefile, outfile, x_axis, y_axis, rotation):
    
    with fiona.open(sourcefile, 'r') as pointfile:
        pointfile.profile['schema']['geometry'] = 'Polygon'
        with fiona.open(outfile, 'w', **pointfile.profile) as poly:
            for i in tqdm(pointfile):
                prop = {keys:values for keys, values in {**i['properties']}.items()}
                shape = _process_geometry._point_to_poly(
                    i['geometry']['coordinates'],
                    float(i['properties'][x_axis]),
                    float(i['properties'][y_axis]),
                    float(i['properties'][rotation]))
                poly.write({'geometry':mapping(shape),'properties': prop})
            poly.close()
        pointfile.close()
    return outfile


# extractedData = '/araihan/Reserach_Data/extracted_data'

# fileDict = extractPath(extractedData, 'shp')
# typelist = list(fileDict.keys())
# planting = fileDict['2022 Planting']
# harvest = fileDict['2022 Harvest']

# zipfiledirs = '/home/raihan/Data'
# fileZip = findFile(zipfiledirs, 'zip')
# zipExtract(fileZip[0], out)

# array, profile = geoprocessing.structured_numpy_array(filesname['outpath'])
# example of manual way to create a numpy unstructured array from structured numpy array
# example = np.array([array['attr1'], array['attr2']]).T
# attr = [i for i, j in profile['schema']['properties'].items() if re.split(r":", j)[0] == 'float']
# y = np.array([array['attr3']]).T
# for i in attr:
#     X = np.array([array[i]]).T
#     reg = LinearRegression().fit(X, y)
#     print(f" r-square : {reg.score(X, y)} : {i}")
# coords = np.array([array['lat'], array['lon']]).T

# with fiona.open(soil_sample, 'r') as poly:
#     with fiona.open(ecom, 'r') as point:
#         index = rtree.index.Index()
#         for fid, feature in poly.items():
#             geometry = shape(feature['geometry'])
#             index.insert(fid, geometry.bounds)
#             print(fid, geometry.bounds)


from utils import _process_geometry

# out_palnting_filename = 'planting_point'

# removes_identical = geoprocessing.remove_identical_point(
#     planting, outputDirs = outdirs,
#     fileNames = out_palnting_filename,
#     xycoords = True,
#     removeIdentical = True
#     )

# outfilName = f"{outdirs}/{out_palnting_filename}_swath_poly.shp"

# outfiles = createPoly(removes_identical, outfile, x_axis, y_axis, rotation)

# data = []
# for poly in tqdm(list(arrays_poly['geometry'])):
#     for point in list(arrays_point['geometry']):
#         if point.intersects(poly) == True:
#             data.append(point)


# mzs_path = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Soil Sample/Panola Farming_South Panola_SP 12_2022_NO Product_1_poly.shp'
# swath_poly_path = '/araihan/Reserach_Data/extracted_data/Panola Farming/processed_data/planting_point_swath_poly.shp'
# planting = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Planting/Panola Farming_South Panola_SP 12_2022_P1718-PRYME_1.shp'
# ecom = '/araihan/Reserach_Data/extracted_data/Panola Farming/ECOM/Panola Farming_South Panola_SP 12_NO Year_TSM_1.shp'
# harvest = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Harvest/Panola Farming_South Panola_SP 12_2022_CORN_1.shp'
# predicate_list = ["intersects", "within", "contains", "overlaps", "crosses", "touches", "covers", "contains_properly"]
# right_array, _ = geoprocessing.structured_numpy_array(ecom)
# left_array, prof = geoprocessing.structured_numpy_array(mzs_path)

