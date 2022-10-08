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
            return np.array(
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
                return np.array(
                    [tuple(i)
                     for i in init_array],
                    dtype = [
                        i for i in np.dtype(
                            [i for _, i in cores.numpy_dtype(
                                file).items()
                                if _ not in 'identical']
                            ).descr])
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
                
                return np.array(
                    [tuple(i)
                     for i in np.array(
                             [select_array[i]
                              for i in indices])],
                    dtype = [
                        i for i in np.dtype(
                            [i for _, i in cores.numpy_dtype(
                                file).items()]
                            ).descr])
        else:
            raise TypeError(
                "geometry type {} not implemented yet".format(
                    file.schema['geometry'])
                )
