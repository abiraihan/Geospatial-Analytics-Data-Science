#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:22:50 2022

@author: raihan
"""

import numpy as np
from shapely.geometry import Point, mapping
from tqdm import tqdm
from collections import OrderedDict
import os
import re
import pyproj
import fiona
from osgeo import osr
# Iterate directory for shapefile

def set_attribute(
        profiles:dict,
        targetProj:int,
        *args,
        **kwargs
        ) -> dict:
    
    schema = profiles['schema']
    geom_type = schema['geometry']
    
    data_args = dict(
        xycoords = False
        )
    
    for key, value in data_args.items():
        if key in kwargs:
            data_args[key] = kwargs[key]
    
    xy = OrderedDict(
        [('lat', 'float:20.20'),
        ('lon', 'float:20.20')]
        )
    
    identical_cols = OrderedDict([('identical', 'int:15')])
    
    mergeDict = OrderedDict(list(xy.items()) + list(schema['properties'].items()) + list(identical_cols.items()))
    
    if data_args['xycoords'] == True:
        for arg in args:
            if arg not in list(schema['properties'].keys()):
                raise ValueError(f"'{arg}' not available into the data columns,\
                                 please assign available attribute name")
        attribute = list(xy.keys()) + [arg for arg in args]
    else:
        for arg in args:
            if arg not in list(schema['properties'].keys()):
                raise ValueError(f"'{arg}' not available into the data columns,\
                                  please assign available attribute name")
        if len(args) > 0:
            attribute = [arg for arg in args]
        else:
            attribute = list(schema['properties'].keys())
    
    crs = {'init':f'epsg:{targetProj}'}
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(targetProj)
    crs_wkt = srs.ExportToWkt()
    
    profile = {
        'driver': profiles['driver'],
        'schema' : {'geometry': schema['geometry'],
        'properties':OrderedDict({i:j
                                  for i, j in mergeDict.items()
                                  if i not in ['lat', 'lon']
                                  }
                                 )},
        'crs' : crs,
        'crs_wkt' : crs_wkt
        }
    
    if geom_type == 'Point':
        attributeDict  = {
            i:list(mergeDict.keys()).index(i)
            for i, _ in mergeDict.items()
            if i in attribute
            }
        
        return {'index' : list(attributeDict.values()),
                'attribute_index' : {
                    i:list(mergeDict.keys()).index(i)
                    for i, _ in mergeDict.items()
                    if i not in ['lat', 'lon']},
                'profile' : profile}
    
def clean_identical(
        filename:str,
        *args,
        **kwargs        
        ):
    
    filenames = os.path.basename(filename)
    
    data_args = dict(
        output_dirs = None,
        file_names = None,
        target_crs = None,
        xycoords = False,
        remove_identical = False
        )
    
    for key, value in data_args.items():
        if key in kwargs:
            data_args[key] = kwargs[key]
    
    file = fiona.open(filename, 'r')
    source_crs = int(re.split(r":", file.crs['init'])[1])
    
    if data_args['target_crs'] is not None:
        transformer = pyproj.Transformer.from_crs(
            crs_from=pyproj.CRS.from_user_input(source_crs),
            crs_to=pyproj.CRS.from_user_input(int(data_args['target_crs'])),
            always_xy=True)
        schemas = set_attribute(file.profile, int(data_args['target_crs']), *args, **kwargs)

    else:
        transformer = pyproj.Transformer.from_crs(
            crs_from=pyproj.CRS.from_user_input(source_crs),
            crs_to=pyproj.CRS.from_user_input(source_crs),
            always_xy=True
            )
        schemas = set_attribute(file.profile, source_crs, *args, **kwargs)
    
    shapeArray = []
    
    assert file.schema['geometry'] == 'Point', f"geometry type should be 'Point', '{file.schema['geometry']}' not accepted"
    for i in tqdm(file, desc = f'Reading Files ---> {filenames}'):
        x, y = transformer.transform(
            i['geometry']['coordinates'][0],
            i['geometry']['coordinates'][1]
            )
        shapeArray.append([x, y, *[values for keys, values in {**i['properties']}.items()]])
            
    file.close()
    
    point, indices, inverse, count  = np.unique(
        np.array(shapeArray)[:, schemas['index']],
        return_index=True,
        return_inverse=True,
        return_counts=True,
        axis = 0
        )
    
    # with_indices = np.array([np.insert(select_array[i], len(select_array[i]), i, axis = 0) for i in indices])
    select_array = np.concatenate((shapeArray, inverse.reshape(len(inverse), 1)), axis=1)
    
    if data_args['remove_identical'] == False:
        identical_array = select_array
        schemas['array_data'] = identical_array
    else:
        identical_array = np.array([select_array[i] for i in indices])
        schemas['array_data'] = identical_array
    
    if data_args['output_dirs'] is not None:
        if os.path.exists(os.path.dirname(filename)):
            if data_args['file_names'] is not None:
                file_path = f"{data_args['output_dirs']}/{data_args['file_names']}.shp"
            else:
                file_path = f"{data_args['output_dirs']}/{filenames}"
        else:
            raise ValueError(f"Aformentioned directory {data_args['output_dirs']} is not a valid path location.\
                             Please assign valid directory")
    else:
        if data_args['file_names'] is not None:
            file_path = f"{os.path.dirname(filename)}/{data_args['file_names']}.shp"
        else:
            file_path = f"{os.path.dirname(filename)}/{filenames}"
    
    nameFile = os.path.basename(file_path)
            
    with fiona.open(file_path, 'w', **schemas['profile']) as output:
        for row in tqdm(schemas['array_data'], desc = f'Creating Files --> {nameFile}', colour = 'Green'):
             point = Point(float(row[0]), float(row[1]))
             properties = {name : row[vals] for name, vals in schemas['attribute_index'].items()}
             output.write({'geometry':mapping(point),'properties': properties})
    output.close()
    
    return file_path

dirPath = '/home/raihan/2018'
outDirs = '/home/raihan/ExportData'
file = lambda dirs, ext:[os.path.join(dirPath, i) for i in os.listdir(dirs) if os.path.splitext(i)[1] == str('.'+(ext))]
import random
filesname = OrderedDict()
filesname['inpath'] = file(dirPath, 'shp')[random.randint(0, len(file(dirPath, 'shp')))]
filesname['output_dirs'] = outDirs
filesname['file_names'] = 'removedDuplicated'
filesname['target_crs'] = None
filesname['xycoords'] = True
filesname['remove_identical'] = True
filesname['attribute'] = ['Product', 'Distance_f', 'Track_deg_', 'Swth_Wdth_', 'Y_Offset_f', 'Rt_Apd_Ct_', 'Date']
filesname['outpath'] = clean_identical(filesname['inpath'], *filesname['attribute'], **filesname)

shape_array = []
with fiona.open(filesname['outpath'], 'r') as shapefile:
    source_crs = int(re.split(r":", shapefile.crs['init'])[1])
    for i in shapefile:
        shape_array.append(
            [i['geometry']['coordinates'][0],
              i['geometry']['coordinates'][1],
              *[values for keys, values in {**i['properties']}.items()]]
            )
    schemas = set_attribute(shapefile.profile, source_crs, *filesname['attribute'], xycoords = False)
shapefile.close()