#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:23:09 2022

@author: raihan
"""

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
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)
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
import time
mzs_path = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Soil Sample/Panola Farming_South Panola_SP 12_2022_NO Product_1_poly.shp'
swath_poly_path = '/araihan/Reserach_Data/extracted_data/Panola Farming/processed_data/planting_point_swath_poly.shp'
planting = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Planting/Panola Farming_South Panola_SP 12_2022_P1718-PRYME_1.shp'
ecom = '/araihan/Reserach_Data/extracted_data/Panola Farming/ECOM/Panola Farming_South Panola_SP 12_NO Year_TSM_1.shp'

start_obj = time.time()
arrays_point, profile_point = geoprocessing.structured_numpy_array(ecom)

arrays_poly, profile_poly = geoprocessing.structured_numpy_array(mzs_path)
print("prep data " + str(time.time() - start_obj))
from shapely.geometry.base import BaseGeometry
from rtree import index
from shapely.prepared import prep

def query(geom_query, arrays_point, indexes):
    
    if isinstance(geom_query, BaseGeometry):
        query_geom = prep(geom_query)
        bound = geom_query.bounds
        tree_idx = [int(i) for i in indexes.intersection(bound)]
    else:
        raise TypeError('Not accepted type of geometry')
    
    res = []
    for index_in_tree in tree_idx:
        if query_geom.contains(arrays_point['geometry'][index_in_tree]):
            res.append(index_in_tree)
    tree_idx = res
    
    return np.sort(np.array(tree_idx, dtype=np.intp))

def query_bulk(query_geom, tree_geom):
    
    tree_indexes = index.Index()
    
    for i, j in np.ndenumerate(arrays_point):
        tree_indexes.insert(i[0], j['geometry'].bounds)
        
    tree_index = []
    input_geometry_index = []
    
    for i, geo in enumerate(query_geom['geometry']):
        res = query(geo, tree_geom, tree_indexes)
        tree_index.extend(res)
        input_geometry_index.extend([i] * len(res))
    return np.vstack([input_geometry_index, tree_index])

# start_obj = time.time()
# rtree_indices = query_bulk(arrays_poly, arrays_point)

# print("Time to execute Rtree method " + str(time.time() - start_obj))


# start_objid = time.time()
# import pygeos

# geom_point = [pygeos.from_shapely(i) for i in arrays_point['geometry']]
# geom_poly = [pygeos.from_shapely(i) for i in arrays_poly['geometry']]

# tree = pygeos.STRtree(geom_point)

# tree_indexi = []
# input_geometry_indexi = []
# for i, geom in enumerate(geom_poly):
#     lit = tree.query(geom, predicate='contains').tolist()
#     tree_indexi.extend(np.sort(np.array(lit, dtype = np.intp)))
#     input_geometry_indexi.extend([i] * len(lit))
# pygeos_strtree_indices = np.vstack([input_geometry_indexi, tree_indexi])
# print("Time to execute pygeos STRtree method " + str(time.time() - start_objid))


# query = tree.query_bulk(geom_poly, predicate='contains').tolist()
# query_geobulk = np.vstack([query[0], query[1]])
# print("Time to execute pygeos STRtree method " + str(time.time() - start_obji))



# mean_list = [j for i, j in all_mean.items()]
# a1 = np.array(mean_list, dtype=[('mean', np.float64)])
# arrays = rfn.merge_arrays([arrays_poly, a1], flatten = True, usemask = False)


start_obji = time.time()
from shapely.strtree import STRtree

tree = STRtree(list(arrays_point['geometry']))
index_by_id = dict((id(pt), i) for i, pt in enumerate(list(arrays_point['geometry'])))

tree_indexi = []
input_geometry_indexi = []
point_indices = 0  
for i, query_geom in enumerate(arrays_poly):
    prep_geom = prep(query_geom['geometry'])
    # selected_point = [(index_by_id[id(pt)], pt.wkt) for pt in tree.query(query_geom['geometry']) if prep_geom.contains(pt)]
    # indices = [i[0]for i in selected_point]
    selected_point = [index_by_id[id(pt)] for pt in tree.query(query_geom['geometry']) if prep_geom.intersects(pt)]
    tree_indexi.extend(np.sort(np.array(selected_point, dtype = np.intp)))
    input_geometry_indexi.extend([i] * len(selected_point))
    # point_indices[id(query_geom['geometry'])] = indices
    # point_indices+=len(indices)
    # geoVals = np.array([arrays_point[['Rt_Apd_Ct_', 'Year___Yea']][i] for i in indices])
    # mean_r4 = geoVals['Rt_Apd_Ct_'].mean()
    # mean_r3 = geoVals['Year___Yea'].mean()
    # print('Rate Apd value {} and Year value {} for {} number of points'.format(mean_r4, mean_r3, point_indices))
shapely_strtree_indices = np.vstack([input_geometry_indexi, tree_indexi])
print("Time to execute shapely STRtree method " + str(time.time() - start_obji))

# print('Rtree indices {}'.format(rtree_indices))
# print('pygeos STRtree Indices {}'.format(pygeos_strtree_indices))
print('Shapely STRtree indices {}'.format(shapely_strtree_indices))

class predicate_type:
    
    predicates = {'within', 'contains', 'contains_properly', 'covers', 'intersects'} | set([None])
    
    @classmethod
    def assign_predicate(cls, predicate = None):
        
        cls._predicate = predicate
        if cls._predicate in cls.predicates:
            return cls._predicate
        else:
            raise TypeError("'{}' is not acceptable for opeartion. Select any suitable \
                            predicates from {}".format(cls._predicate, cls.predicates))

f = getattr(predicate_type, 'assign_predicate')('intersects')
print(f)
