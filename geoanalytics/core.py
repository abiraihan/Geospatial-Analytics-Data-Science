#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:22:19 2022

@author: raihan
"""

import os
import re
import fiona
import pyproj
import numpy as np
from osgeo import osr
from tqdm import tqdm
from collections import OrderedDict
from shapely.ops import transform
from shapely.geometry import Point, mapping, Polygon, MultiPolygon


class geoprocessing:
    
    @classmethod
    def set_attribute_point(
            cls,
            fileProfile:dict,
            targetCrs:int,
            *args, **kwargs) -> dict:
        '''

        Parameters
        ----------
        fileProfile : dict
            'profile' from the fiona shapefile **meta as a dictionary.
        targetCrs : int
            CRS number as from EPSG CODE to create new 'profile' for new shapefile to create
        *args : TYPE
            List of Attribute name will return as index.
        **kwargs : TYPE
            Default 'xycoords' arguments is set False as to confirm that \
                xy coordinates will not be account for point geometry.

        Returns
        -------
        dict
            key as 'index': index location of the attribute into numpy array,
            key as 'attribute_index': dict as of the location of the attribute and attribute name,
            key as 'profile': 'profile' as dict for the new shapefile that will be created. 

        '''
        
        cls._fileProfile = fileProfile
        cls._targetCrs = targetCrs
        
        schema = cls._fileProfile['schema']
        
        point_args = dict(
            xycoords = False
            )
        
        for key, value in point_args.items():
            if key in kwargs:
                point_args[key] = kwargs[key]
        
        xyattributes = OrderedDict(
            [('lat', 'float:20.20'),
            ('lon', 'float:20.20')]
            )
        
        identical_cols = OrderedDict([('identical', 'int:15')])
        
        mergeDict = OrderedDict(
            list(xyattributes.items()) +
            list(schema['properties'].items()) +
            list(identical_cols.items()))
        
        if point_args['xycoords'] == True:
            for arg in args:
                if arg not in list(schema['properties'].keys()):
                    raise ValueError(
                        f"'{arg}' not available into the data columns,\
                            please select correct attribute name")
            attribute = list(xyattributes.keys()) + [arg for arg in args]
        else:
            for arg in args:
                if arg not in list(schema['properties'].keys()):
                    raise ValueError(
                        f"'{arg}' not available into the data columns,\
                            please select correct attribute name")
            if len(args) > 0:
                attribute = [arg for arg in args]
            else:
                attribute = list(schema['properties'].keys())
        
        crs = {'init':f'epsg:{cls._targetCrs}'}
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(cls._targetCrs)
        crs_wkt = srs.ExportToWkt()
        
        profile = {
            'driver': cls._fileProfile['driver'],
            'schema' : {'geometry': schema['geometry'],
            'properties':OrderedDict(
                {i:j
                 for i, j in mergeDict.items()
                 if i not in list(xyattributes.keys())
                 }
                )},
            'crs' : crs,
            'crs_wkt' : crs_wkt
            }
        
        attributeDict  = {
            i:list(mergeDict.keys()).index(i)
            for i, _ in mergeDict.items()
            if i in attribute
            }
        
        return {'index' : list(attributeDict.values()),
                'attribute_index' : {
                    i:list(mergeDict.keys()).index(i)
                    for i, _ in mergeDict.items()
                    if i not in list(xyattributes.keys())},
                'profile' : profile,
                'keep_type' : OrderedDict(
                    {i:j for i, j in mergeDict.items()
                     if i in attribute
                     }
                    ),
                'keep_index' : {
                    i:list(mergeDict.keys()).index(i)
                    for i, _ in mergeDict.items()
                    if i in attribute}
                }
    
    @classmethod
    def set_attribute_poly(
            cls,
            fileProfile:dict,
            targetCrs:int
            ) -> dict:
        '''

        Parameters
        ----------
        fileProfile : dict
            'profile' from the fiona shapefile **meta as a dictionary.
        targetCrs : int
            CRS number as from EPSG CODE to create new 'profile' for new shapefile to create

        Returns
        -------
        dict
            key as 'index': index location of the attribute into numpy array,
            key as 'profile': 'profile' as dict for the new shapefile that will be created.

        '''
        
        cls._fileProfile = fileProfile
        cls._targetCrs = targetCrs
        
        polys = OrderedDict(
            [('lat', 'float:20.20')])
        
        mergeDict = OrderedDict(
            list(polys.items()) +
            list(cls._fileProfile['schema']['properties'].items()))
        
        if cls._targetCrs is not None:
            crs = {'init':f'epsg:{cls._targetCrs}'}
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(cls._targetCrs)
            crs_wkt = srs.ExportToWkt()
        else:
            crs = cls._fileProfile['crs']
            crs_wkt = cls._fileProfile['crs_wkt']
        
        profile = {
            'driver' : cls._fileProfile['driver'],
            'schema' : {'geometry' : cls._fileProfile['schema']['geometry'],
                        'properties': cls._fileProfile['schema']['properties'].items()},
            'crs' : crs,
            'crs_wkt' : crs_wkt
            }
        return {
            'attribute_index' : {
                i:list(mergeDict.keys()).index(i)
                for i, _ in mergeDict.items()
                if i not in list(polys.keys())},
            'profile' : profile}
    
    @classmethod
    def remove_identical_point(
            cls,
            filename:str,
            *args,
            **kwargs) -> str:
        '''
        

        Parameters
        ----------
        filename : str
            -> file path location of shapefile.
        *args : non-keywords args
            -> List of Attribute name that will be accounted for find identical values.
        **kwargs : keywords agrs
            --> 'outputDirs' is 'None', if assigned then shapefile will be \
                exported to the assinged 'ouputDirs' directory.
            --> 'fileNames' is 'None', if assigned then shapefile name will be \
                assinged while exporting shapefile,
            --> 'targetEPSG' is 'None', if assinged then shapefile projection will \
                be assinged and exported with 'targetEPSG' as coordinate reference
                system
            --> 'xycoords' arguments is set 'False' as to confirm that \
                xy coordinates will not be account for point geometry,
            --> 'removeIdentical' is 'False'', If assinged 'True' then identical \
                records will be removed from the datasets/shapefile.

        Returns
        -------
        str
            --> file path location of the exported shapefile.

        '''
        
        cls._filename = filename
                
        point_args = dict(
            outputDirs = None,
            fileNames = None,
            targetEPSG = None,
            xycoords = False,
            removeIdentical = False
            )
        
        for key, value in point_args.items():
            if key in kwargs:
                point_args[key] = kwargs[key]
        
        file = fiona.open(cls._filename, 'r')
        
        if point_args['targetEPSG'] is not None:
            target_crs = int(point_args['targetEPSG'])
        else:
            target_crs = int(re.split(r":", file.crs['init'])[1])
        
        transformer = pyproj.Transformer.from_crs(
            crs_from=pyproj.CRS.from_user_input(int(re.split(r":", file.crs['init'])[1])),
            crs_to=pyproj.CRS.from_user_input(target_crs),
            always_xy=True
            )
        schemas = cls.set_attribute_point(file.profile, target_crs, *args, **kwargs)
        
        shapeArray = []
        
        assert file.schema['geometry'] == 'Point', f"geometry type should be 'Point', '{file.schema['geometry']}' not accepted"
        for i in tqdm(file, desc = f'Reading Files ---> {os.path.basename(cls._filename)}'):
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
        
        
        select_array = np.concatenate((shapeArray, inverse.reshape(len(inverse), 1)), axis=1)
        # with_indices = np.array([np.insert(select_array[i], len(select_array[i]), i, axis = 0) for i in indices])
        
        if point_args['removeIdentical'] == False:
            identical_array = select_array
            schemas['array_data'] = identical_array
        else:
            identical_array = np.array([select_array[i] for i in indices])
            schemas['array_data'] = identical_array
        
        if point_args['outputDirs'] is not None:
            if os.path.exists(os.path.dirname(cls._filename)):
                if point_args['fileNames'] is not None:
                    file_path = f"{point_args['outputDirs']}/{point_args['fileNames']}.shp"
                else:
                    file_path = f"{point_args['outputDirs']}/{os.path.basename(cls._filename)}"
            else:
                raise ValueError(f"Aformentioned directory {point_args['outputDirs']} is not a valid path location.\
                                 Please assign valid directory")
        else:
            if point_args['fileNames'] is not None:
                file_path = f"{os.path.dirname(cls._filename)}/{point_args['fileNames']}.shp"
            else:
                file_path = f"{os.path.dirname(cls._filename)}/{os.path.basename(cls._filename)}"
                
        with fiona.open(file_path, 'w', **schemas['profile']) as output:
            for row in tqdm(schemas['array_data'], desc = f'Creating Files --> {os.path.basename(file_path)}', colour = 'Green'):
                 point = Point(float(row[0]), float(row[1]))
                 properties = {name : row[index] for name, index in schemas['attribute_index'].items()}
                 output.write({'geometry':mapping(point),'properties': properties})
        output.close()
        
        return file_path

    @classmethod
    def remove_identical_poly(
            cls, 
            filename:str, 
            **kwargs) -> str:
        '''

        Parameters
        ----------
        filename : str
            -> file path location of shapefile.
        **kwargs : keywords agrs
            --> 'outputDirs' is 'None', if assigned then shapefile will be \
                exported to the assinged 'ouputDirs' directory.
            --> 'fileNames' is 'None', if assigned then shapefile name will be \
                assinged while exporting shapefile,
            --> 'targetEPSG' is 'None', if assinged then shapefile projection will \
                be assinged and exported with 'targetEPSG' as coordinate reference
                system
            --> 'removeIdentical' is 'False'', If assinged 'True' then identical \
                records will be removed from the datasets/shapefile.

        Raises
        ------
        TypeError
            --> if found geometry type other than 'Polygon' or 'MultiPolygon'
        ValueError
            if assigned 'outputDirs' is not a valid directory path.

        Returns
        -------
        str
            --> file path location of the exported shapefile.

        '''
        
        cls._filename = filename
                
        poly_args = dict(
            outputDirs = None,
            fileNames = None,
            targetEPSG = None,
            removeIdentical = False
            )
        
        for key, value in poly_args.items():
            if key in kwargs:
                poly_args[key] = kwargs[key]
        
        shapefile = fiona.open(cls._filename, 'r')
        
        if poly_args['targetEPSG'] is not None:
            target_crs = int(poly_args['targetEPSG'])
        else:
            target_crs = int(re.split(r":", shapefile.crs['init'])[1])
        
        transformer = pyproj.Transformer.from_crs(
            crs_from=pyproj.CRS.from_user_input(int(re.split(r":", shapefile.crs['init'])[1])),
            crs_to=pyproj.CRS.from_user_input(target_crs),
            always_xy=True
            )
        
        schemas = cls.set_attribute_poly(shapefile.profile, poly_args['targetEPSG'])
        
        assert shapefile.schema['geometry'] == 'Polygon', f"geometry type should be 'Polygon', '{shapefile.schema['geometry']}' not accepted"
        
        init_array = []
        for i in tqdm(shapefile, desc = f'Reading Files ---> {os.path.basename(cls._filename)}'):
            if i['geometry']['type'] == 'Polygon':
                polys = [Polygon(geom) for geom in i['geometry']['coordinates']]
                trsnPoly = [transform(transformer.transform, i) for i in polys]
                init_array.append([
                    *trsnPoly,
                    *[values for keys, values in {**i['properties']}.items()]]
                    )
            elif i['geometry']['type'] == 'MultiPolygon':
                multipolys = [Polygon(coords[0]) for coords in i['geometry']['coordinates']]
                trsnMultiPoly = MultiPolygon([transform(transformer.transform, i) for i in multipolys])
                init_array.append([
                    trsnMultiPoly,
                    *[values for keys, values in {**i['properties']}.items()]]
                    )
            else:
                raise TypeError(f"Found {i['geometry']['type']} geometry type")
        shapefile.close()
        
        if poly_args['removeIdentical'] == True:
            unique_array, unique_poly = [], []
            for geom in init_array:
                if not any(poly.equals(geom[0]) for poly in unique_poly):
                    unique_array.append([*geom])
        else:
            unique_array = init_array
        
        if poly_args['outputDirs'] is not None:
            if os.path.exists(os.path.dirname(cls._filename)):
                if poly_args['fileNames'] is not None:
                    file_path = f"{poly_args['outputDirs']}/{poly_args['fileNames']}.shp"
                else:
                    file_path = f"{poly_args['outputDirs']}/{os.path.basename(cls._filename)}"
            else:
                raise ValueError(f"Aformentioned directory {poly_args['outputDirs']} is not a valid path location.\
                                  Please assign valid directory")
        else:
            if poly_args['fileNames'] is not None:
                file_path = f"{os.path.dirname(cls._filename)}/{poly_args['fileNames']}.shp"
            else:
                file_path = f"{os.path.dirname(cls._filename)}/{os.path.basename(cls._filename)}"
        with fiona.open(file_path, 'w', **schemas['profile']) as output:
            for row in tqdm(unique_array, desc = f'Creating Files --> {os.path.basename(file_path)}', colour = 'Green'):
                  properties = {name : row[index] for name, index in schemas['attribute_index'].items()}
                  output.write({'geometry':mapping(row[0]),'properties': properties})
        output.close()
        
        return file_path
    
    @classmethod
    def structured_numpy_array(
            cls,
            filePath:str
            ):
        '''

        Parameters
        ----------
        filePath : str
                --> file path of shapefile location.

        Raises
        ------
        TypeError
            Raise TypeError if dtype not found to assign.

        Returns
        -------
        array : numpy.array
            numpy structured array.
        profile : dict
            fiona shapefile profile of the shapefile.

        '''
        
        cls._filePath = filePath
                
        shape_array = []
        with fiona.open(cls._filePath, 'r') as shapefile:
            source_crs = int(re.split(r":", shapefile.crs['init'])[1])
            for i in shapefile:
                shape_array.append(
                    tuple([
                    i['geometry']['coordinates'][0],
                    i['geometry']['coordinates'][0],
                    *[values for keys, values in {**i['properties']}.items()]
                    ])
                    )
            
            properties = OrderedDict(list(OrderedDict(
                [('lat', 'float:20.20'),
                ('lon', 'float:20.20')]
                ).items()) + list(shapefile.profile['schema']['properties'].items()))
            
            crs = {'init':f'epsg:{source_crs}'}
            srs = osr.SpatialReference()
            srs.ImportFromEPSG(source_crs)
            crs_wkt = srs.ExportToWkt()
            
            profile = {'driver': shapefile.profile['driver'],
                        'schema' : {'geometry': shapefile.profile['schema']['geometry'],
                        'properties':properties},
                        'crs' : crs,
                        'crs_wkt' : crs_wkt
                        }
        shapefile.close()
        
        attribute_type = {}
        for i, j in properties.items():
            itemType = tuple(re.split(r":", j))
            if itemType[0] == 'str':
                attribute_type[i] = (i, np.unicode, int(itemType[1]))
            elif itemType[0] == 'float':
                attribute_type[i] = (i, np.float64)
            elif itemType[0] == 'date':
                attribute_type[i] = (i, 'datetime64[D]')
            elif itemType[0] == 'int':
                attribute_type[i] = (i, np.int64)
            else:
                raise TypeError(f"Please define dtype for {i} at 'structured_numpy_array' definition")
                
        array = np.array(shape_array, dtype=[i for i in np.dtype([i for _, i in attribute_type.items()]).descr])
        
        return array, profile