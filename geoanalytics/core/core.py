#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:22:19 2022

@author: raihan
"""

import shapely
import fiona
import numpy as np
import collections
import pyproj
import pandas
from base.spatialquery.spatialquery import (
    SpatialQuery,
    GeosQuery,
    RtreeQuery,
    ComputeArray
    )
from base.base import geoprocessing, geo_array
from georead.georead import geotranslate
from geotransform.geotransform import spatialGrid

class cores:
    
    """
    Module provides functionalty to read and cache spatial data set as a numpy structured array
    
    """
    
    @staticmethod
    def numpy_dtype(shapefile):
        
        
        properties = collections.OrderedDict(list(collections.OrderedDict(
            [('geometry', 'object')]
            ).items()) + list(shapefile.profile['schema']['properties'].items()) +
            list(collections.OrderedDict([('identical', 'float:15.4')]).items()))
        attribute_type = {}
        for i, j in properties.items():
            itemType = tuple(j.split(':'))
            if itemType[0] == 'str':
                attribute_type[i] = (i, np.compat.unicode, int(itemType[1]))
            elif itemType[0] == 'float':
                attribute_type[i] = (i, np.float64)
            elif itemType[0] == 'date':
                attribute_type[i] = (i, 'datetime64[D]')
            elif itemType[0] == 'int':
                attribute_type[i] = (i, np.int64)
            elif itemType[0] == 'object':
                attribute_type[i] = (i, 'object')
            else:
                attribute_type[i] = (i, 'object')
        return attribute_type
    
    @classmethod
    def set_attribute_point(
            cls,
            fileProfile:dict,
            *args, **kwargs) -> dict:
        '''

        Parameters
        ----------
        fileProfile : dict
            'profile' from the fiona shapefile **meta as a dictionary.
        *args : TYPE
            List of Attribute name will return as index.
        **kwargs : TYPE
            Default 'xycoords' arguments is set False as to confirm that
                xy coordinates will not be account for point geometry.

        Returns
        -------
        dict
            key as 'index': index location of the attribute into numpy array,

        '''
        
        cls._fileProfile = fileProfile
        
        schema = cls._fileProfile['schema']
        
        point_args = dict(
            xycoords = False
            )
        
        for key, value in point_args.items():
            if key in kwargs:
                point_args[key] = kwargs[key]
        
        xyattributes = collections.OrderedDict(
            [('lat', 'float:22.20'),
            ('lon', 'float:22.20')]
            )
        
        identical_cols = collections.OrderedDict([('identical', 'float:15.4')])
        
        mergeDict = collections.OrderedDict(
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
        
        attributeDict  = {
            i:list(mergeDict.keys()).index(i)
            for i, _ in mergeDict.items()
            if i in attribute
            }
        
        return {
            'index' : list(attributeDict.values())
            }

    @classmethod
    def set_attribute_poly(
            cls,
            fileProfile:dict,
            *args
            ) -> dict:
        '''

        Parameters
        ----------
        fileProfile : dict
            'profile' from the fiona shapefile **meta as a dictionary.

        Returns
        -------
        dict
            key as 'index': index location of the attribute into numpy array,

        '''
        
        cls._fileProfile = fileProfile
        schema = cls._fileProfile['schema']
        
        polys = collections.OrderedDict(
            [('geometry', 'object')])
        
        mergeDict = collections.OrderedDict(
            list(polys.items()) +
            list(schema['properties'].items()))
        
        for arg in args:
            if arg not in list(schema['properties'].keys()):
                raise ValueError(
                    f"'{arg}' not available into the data columns,\
                        please select correct attribute name")

        if len(args) > 0:
            attribute = [arg for arg in args]
        else:
            attribute = list(schema['properties'].keys())
            
        attributeDict  = {
            i:list(mergeDict.keys()).index(i)
            for i, _ in mergeDict.items()
            if i in attribute
            }
        return {
            'index' : list(attributeDict.values())
            }
    
    @classmethod
    def remove_identical(
            cls,
            filename:str,
            *args,
            **kwargs) -> str:
        '''
        

        Parameters
        ----------
        filename : str
            -> file path location of shapefile.
        *args : tuple, non-keywords args
            -> List of Attribute name that will be accounted for find identical values.
        **kwargs : dict, keywords agrs
            --> 'xycoords' arguments is set 'False' as to confirm that
                xy coordinates will not be account for point geometry,

        Returns
        -------
        str
            --> file path location of the exported shapefile.

        '''
        
        cls._filename = filename
                
        point_args = dict(
            xycoords = False
            )
        
        for key, value in point_args.items():
            if key in kwargs:
                point_args[key] = kwargs[key]
        
        file = fiona.open(cls._filename, 'r')
        crs = int(file.crs['init'].split(':')[1])
        
        if file.schema['geometry'] == 'Point':
            schemas = cls.set_attribute_point(
                file.profile,
                *args,
                **kwargs
                )
            assert file.schema['geometry'] == 'Point', "geometry type should be 'Point', '{}' not accepted".format(
                file.schema['geometry']
                )
            shapeArray = [
                [i['geometry']['coordinates'][0],
                 i['geometry']['coordinates'][1],
                 *[values for keys, values in {**i['properties']}.items()]]
                for i in file]
            file.close()
            
            point, indices, inverse, count  = np.unique(
                np.array(shapeArray)[:, schemas['index']],
                return_index=True,
                return_inverse=True,
                return_counts=True,
                axis = 0
                )
            select_array = np.concatenate((
                shapeArray,
                inverse.reshape(len(inverse), 1)),
                axis=1
                )
            
            arrays = np.array(
                [tuple([getattr(
                    shapely.geometry,
                    file.schema['geometry']
                    )(float(i[0]),
                      float(i[1])),
                      *i[2:]])
                      for i in np.array(
                              [select_array[i]
                               for i in indices])],
                      dtype = [
                          i for i in np.dtype(
                              [i for _, i in cls.numpy_dtype(
                                  file).items()]
                              ).descr])
            return geo_array(arrays, crs= crs)
        elif file.schema['geometry'] == 'Polygon':
            if point_args['xycoords'] == True:
                assert file.schema['geometry'] == 'Polygon', "geometry type should be 'Polygon', '{}' not accepted".format(
                    file.schema['geometry']
                    )
                init_array = []
                for i in file:
                    if not any(
                            poly[0].equals(
                                shapely.geometry.shape(i['geometry'])
                                           )
                            for poly in init_array
                            ):
                        init_array.append(
                            [shapely.geometry.shape(i['geometry']),
                             *[values for keys, values in {**i['properties']}.items()]]
                            )
                file.close()
                arrays = np.array(
                    [tuple(i)
                     for i in init_array],
                    dtype = [
                        i for i in np.dtype(
                            [i for _, i in cls.numpy_dtype(
                                file).items()
                                if _ not in 'identical']
                            ).descr])
                return geo_array(arrays, crs= crs)
            elif point_args['xycoords'] == False:
                schemas = cls.set_attribute_poly(
                    file.profile,
                    *args
                    )
                assert file.schema['geometry'] == 'Polygon', "geometry type should be 'Polygon', '{}' not accepted".format(
                    file.schema['geometry']
                    )
                init_array = []
                for i in file:
                    if not any(
                            poly[0].equals(
                                shapely.geometry.shape(i['geometry'])
                                )
                            for poly in init_array
                            ):
                        init_array.append(
                            [shapely.geometry.shape(i['geometry']),
                             *[values for keys, values in {**i['properties']}.items()]]
                            )
                file.close()
                
                poly, indices, inverse, count  = np.unique(
                    np.array(init_array)[:, schemas['index']].astype('<U254'),
                    return_index=True,
                    return_inverse=True,
                    return_counts=True,
                    axis = 0
                    )
                select_array = np.concatenate((
                    init_array,
                    inverse.reshape(len(inverse), 1)),
                    axis=1
                    )
                arrays = np.array(
                    [tuple(i)
                     for i in np.array(
                             [select_array[i]
                              for i in indices])],
                    dtype = [
                        i for i in np.dtype(
                            [i for _, i in cls.numpy_dtype(
                                file).items()]
                            ).descr])
                return geo_array(arrays, crs= crs)
        else:
            raise TypeError(
                "geometry type {} not implemented yet".format(
                    file.schema['geometry'])
                )

    @classmethod
    def SpatialJoin(
            cls,
            left_data_path: (str, np.ndarray, geo_array, geotranslate),
            right_data_path: (str, np.ndarray, geo_array, geotranslate),
            predicates: str,
            *args: tuple,
            **kwargs
            ):
        """
        
        Parameters
        ----------
        left_data_path : (str, np.ndarray)
            - Spatial data path as str or numpy.ndarray to join data from right_data_path
        right_data_path : (str, np.ndarray)
            - Spatial data path as str or numpy.ndarray to join data to left_data_path
        predicates : str
            - Binary Predicates. Accepted predicates are : "intersects", "within", "contains", "overlaps", "crosses",
              "touches", "covers", "contains_properly"
        *args : tuple, non-keyword args
            - Assign list of attributes to perform statistics on.
        **kwargs : dict as keyword args
            - keywwords:
                1. "stats" - Name of statistics, Valid are : 'mean', 'max', 'min'
                2. "query_index_by" - Spatial indexing rule, Valid rule are ['shapely', 'pygeos' 'rtree']
            
        Raises
        ------
        ValueError
            - If spatail query tree algorithm is not from ['shapely', 'pygeos' 'rtree']

        Returns
        -------
        arrays : numpy.ndarry
            - numpy.ndarray structured array data for spatially joined data

        """

        cls._left_data_path = left_data_path
        cls._right_data_path = right_data_path
        cls._predicates = predicates
        
        if cls._predicates not in {
                "intersects",
                "within",
                "contains",
                "overlaps",
                "crosses",
                "touches",
                "covers",
                "contains_properly"
                }:
            raise ValueError(
                "{} not an valid predicate".format(
                    cls._predicates)
                )
        
        join_args = dict(
            stats = 'mean',
            query_index_by = 'shapely'
            )
        
        valid_tree_index = ['shapely', 'pygeos', 'rtree']
        
        for key, value in join_args.items():
            if key in kwargs:
                join_args[key] = kwargs[key]
        
        if join_args['query_index_by'] not in valid_tree_index:
            raise TypeError(
                "{} not a valid rule, Select one valid rules from {}".format(
                    join_args['query_index_by'], valid_tree_index)
                )
        
        # print(type(cls._left_data_path), type(cls._right_data_path))
        if isinstance(cls._left_data_path, str):
            left_array = geoprocessing.structured_numpy_array(cls._left_data_path)
            
        if isinstance(cls._right_data_path, str):
            right_array  = geoprocessing.structured_numpy_array(cls._right_data_path)
        
        if isinstance(cls._left_data_path, geo_array | np.ndarray):
            left_array = cls._left_data_path
        
        if isinstance(cls._right_data_path, geo_array | np.ndarray):
            right_array = cls._right_data_path
        
        if isinstance(cls._left_data_path, geotranslate):
            left_array = cls._left_data_path.__data__
        
        if isinstance(cls._right_data_path, geotranslate):
            right_array = cls._right_data_path.__data__
            
        if isinstance(left_array, geo_array | geotranslate):
            if left_array.crs != right_array.crs:
                raise pyproj.exceptions.CRSError("Left CRS - '{}' doesn't match with Right CRS - {}".format(
                    left_array.crs, right_array.crs))

        if join_args['query_index_by'] == 'shapely':
            query_shape = SpatialQuery(
                right_array['geometry']).QueryIndex(
                    query_geometry = left_array['geometry'],
                    predicate = cls._predicates
                    )
        elif join_args['query_index_by'] == 'rtree':
            query_shape = RtreeQuery(
                right_array['geometry']).QueryIndex(
                    bulk_geom = left_array['geometry'],
                    predicate = cls._predicates
                    )
        elif join_args['query_index_by'] == 'pygeos':
            query_shape = GeosQuery(
                right_array['geometry']).QueryIndex(
                    query_geometry = left_array['geometry'],
                    predicate = cls._predicates
                    )
        else:
            raise ValueError(
                "Set a valid spatial index algorithm from one of the folowing {}".format(
                    valid_tree_index)
                )
        
        joined_data = ComputeArray.spatial_join(
            query_shape,
            left_array,
            right_array,
            join_args['stats'],
            *args
            )

        arrays = np.lib.recfunctions.merge_arrays(
            [left_array, joined_data],
            flatten=True,
            usemask=False
            )
        if isinstance(left_array, geo_array | geotranslate):
            return geotranslate(geo_array(arrays, left_array.crs))
        elif isinstance(left_array, np.ndarray):
            return arrays
        else:
            raise NotImplementedError("{} not implementated".format(type(left_array)))


class spatialstack:
    
    def __init__(cls, joinData):
        cls._joinData = joinData
        
    def __repr__(cls):
        return '{}'.format(pandas.DataFrame(data = cls._joinData.__data__))
        
    def __str__(cls):
        return '{}'.format(pandas.DataFrame(data = cls._joinData.__data__))
    
    def __getitem__(cls, key):
        if key not in 'geometry':
            cols, rows = spatialGrid.getShape(cls._joinData)
            return np.flipud(np.reshape(cls._joinData.__data__[key], (cols, -1)).T)
        else:
            print("{} can't be processed".format(key))
    
    @property
    def crs(cls):
        return cls._joinData.crs
    
    @property
    def attribute(cls):
        return [i for i in cls._joinData.attribute if i not in 'geometry']
    
    @property
    def unary_union(cls):
        return cls._joinData.unary_union
    
    @property
    def dtype(cls):
        return cls._joinData.dtype
    
    @property
    def continuous_array(cls):
        cols, rows = spatialGrid.getShape(cls._joinData)
        f8 = {i: j for i, j in cls._joinData.dtype if np.dtype(j).kind in ['i', 'f']}
        cidx = {i:list(f8.keys()).index(i) for i, j in f8.items()}
        final_nparray = cls._joinData[list(cidx.keys())]
        return cidx, np.stack([np.flipud(np.reshape(final_nparray[i], (cols, -1)).T) for i in final_nparray.dtype.names])
    
    @property
    def discrete_array(cls):
        cols, rows = spatialGrid.getShape(cls._joinData)
        uxi = {i:(i, j) for i, j in cls._joinData.dtype if np.dtype(j).kind in ['U']}
        uidx = {j:list(uxi.keys()).index(i) for i, j in uxi.items()}
        final_array = cls._joinData[[i[0] for i in uidx.keys()]]
        return uidx, np.stack([np.flipud(np.reshape(final_array[i], (cols, -1)).T) for i in final_array.dtype.names])
    
    @property
    def datetime_array(cls):
        cols, rows = spatialGrid.getShape(cls._joinData)
        uxi = {i:(i, j) for i, j in cls._joinData.dtype if np.dtype(j).kind in ['M']}
        didx = {j:list(uxi.keys()).index(i) for i, j in uxi.items()}
        final_array = cls._joinData[[i[0] for i in didx.keys()]]
        return didx, np.stack([np.flipud(np.reshape(final_array[i], (cols, -1)).T) for i in final_array.dtype.names])
