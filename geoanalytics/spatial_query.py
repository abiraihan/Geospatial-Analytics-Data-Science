#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 21:23:41 2022

@author: araihan
"""

import numpy as np
import warnings
import shapely
from tqdm import tqdm
from core import geoprocessing
from shapely.geometry.base import BaseGeometry
import numpy.lib.recfunctions as rfn
from collections import OrderedDict
from statistics import mode
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

class SpatialQuery(shapely.strtree.STRtree):
    
    def __init__(
            cls,
            tree_geometry
            ):
        cls._input_geometry = tree_geometry
        super(SpatialQuery, cls).__init__(tree_geometry)
    
    def check_geometry(
            cls,
            geometry
            ):
        cls.geometry = geometry
        if cls.geometry is None:
            return np.array([], dtype=np.intp)
        
        if not isinstance(cls.geometry, BaseGeometry):
            raise TypeError(
                "Got `geometry` of type `{}`, `geometry` must be ".format(
                    type(cls.geometry)
                )
                + "a shapely geometry."
            )
        
        if cls.geometry.is_empty:
            return np.array([], dtype=np.intp)
        return cls.geometry
    
    def query_bulk(
            cls,
            query_geometry:list,
            predicate = None
            ):
        cls._query_geometry = query_geometry
        cls._predicate = predicate
        valid_predicates = {
            "intersects",
            "within",
            "contains",
            "overlaps",
            "crosses",
            "touches",
            "covers",
            "contains_properly",
        }
        if cls._predicate not in valid_predicates:
            raise ValueError(
                "Got `predicate` = `{}`, `predicate` must be one of {}".format(
                    cls._predicate, valid_predicates
                )
            )
        tree_idx = shapely.strtree.STRtree(cls._input_geometry)
        if not tree_idx:
            return np.array([], dtype=np.intp)
        tree_index, input_geom_index = [], []
        for index, geo in enumerate(cls._query_geometry):
            geo = cls.check_geometry(geo)
            if cls._predicate == 'within':
                if not isinstance(
                        geo,
                        shapely.prepared.PreparedGeometry
                        ):
                    geometry = shapely.prepared.prep(geo)
                    indices = [i for i in tree_idx.query_items(geo)
                               if geometry.contains(cls._input_geometry[i])
                               ]
                    tree_index.extend(indices)
            elif cls._predicate is not None:
                if cls._predicate in (
                        "contains",
                        "intersects",
                        "covers",
                        "contains_properly",
                        ):
                    if not isinstance(
                            geo,
                            shapely.prepared.PreparedGeometry
                            ):
                        geometry = shapely.prepared.prep(geo)
                        indices = [i for i in tree_idx.query_items(geo)
                                   if getattr(geometry, cls._predicate)(cls._input_geometry[i])
                                   ]
                        tree_index.extend(indices)
                else:
                    indices = [i for i in tree_idx.query_items(geo)
                                if getattr(geo, cls._predicate)(cls._input_geometry[i])
                                ]
                    tree_index.extend(indices)
            input_geom_index.extend([index] * len(indices))
        return np.vstack([input_geom_index, tree_index])


class compute_array:
    
    @staticmethod
    def additional_properties(
            attribute_dict:dict
            )->OrderedDict:
        """

        Parameters
        ----------
        attribute_dict : dict
            DESCRIPTION.

        Returns
        -------
        OrderedDict
            DESCRIPTION.

        """
        dict_item = {}
        for i, j in attribute_dict.items():
            if np.dtype(j[1]).kind == 'U':
                dict_item[j[0]] = "str:254"
            elif np.dtype(j[1]).kind == 'i':
                dict_item[j[0]] = "int:{}".format(np.dtype(j[1]).num)
            elif np.dtype(j[1]).kind == 'f':
                dict_item[j[0]] = "float:{}.4".format(np.dtype(j[1]).num)
            elif np.dtype(j[1]).kind == 'M':
                dict_item[j[0]] = "date"
        return OrderedDict(dict_item)
    
    @classmethod
    def attribute_dtype(
            cls,
            arrays: np.array,
            stat_type: str,
            *args: tuple
            ) -> dict:
        """

        Parameters
        ----------
        arrays : np.array
            DESCRIPTION.
        stat_type : str
            DESCRIPTION.
        *args : tuple
            DESCRIPTION.

        Raises
        ------
        AttributeError
            DESCRIPTION.
        TypeError
            DESCRIPTION.

        Returns
        -------
        dict
            DESCRIPTION.

        """
        cls._arrays = arrays
        cls._stat_type = stat_type
        
        if cls._stat_type not in ['max', 'min', 'mean']:
            raise AttributeError(
                "'{}' is not accepted, select one valid statistics from ['max', 'min', 'mean']".format(cls._stat_type))
        
        all_attrs = [i for i, j in cls._arrays.dtype.descr]
        if len(args) == 0:
            attrs = [i for i, j in cls._arrays.dtype.descr if not np.dtype(j).kind in ['O']]
        else:
            attrs = [arg for arg in args]
        
        for arg in args:
            if arg not in all_attrs:
                raise AttributeError(
                    "{} not available into the numpy structured array, \
                        please assing correct attribute name".format(arg))
        
        dtype_dict = {}
        for i, j in cls._arrays.dtype.descr:
            if i in attrs:
                if np.dtype(j).kind in ['i', 'f']:
                    dtype_dict[i] = (''.join([(i[:3] + i[3::2])[:8], '_', cls._stat_type])[:12], j)
                elif np.dtype(j).kind in ['U', 'M']:
                    dtype_dict[i] = (''.join([(i[:3] + i[3::2])[:7], '_', 'major'])[:12], j)
                elif np.dtype(j).kind in ['O']:
                    raise TypeError(
                        "'{}' attribute is an object type and its not acceptable for numeric function, \
                            Please remove or assign dtype other than 'np.object'".format(i))
                            
        unique_item = []
        for name in [j[0] for i, j in dtype_dict.items()]:
            if name not in unique_item:
                unique_item.append(name)
            else:
                raise ValueError(
                    "'{}' exist more than once into dict as attribute name, \
                        either change it or rename the attribute name".format(name))
        
        properties = cls.additional_properties(dtype_dict)
                        
        return dtype_dict, stat_type, properties
    
    @classmethod
    def spatial_join(
            cls,
            query_tree: np.ndarray,
            geom_queried: np.array,
            stats: str,
            *args: tuple):
        """

        Parameters
        ----------
        query_geom : np.array
            DESCRIPTION.
        geom_queried : np.array
            DESCRIPTION.
        stats : str
            DESCRIPTION.
        *args : tuple
            DESCRIPTION.

        Returns
        -------
        TYPE
            DESCRIPTION.
        prop : TYPE
            DESCRIPTION.

        """
        cls._query_tree = query_tree
        cls._geom_queried = geom_queried
        cls._stats = stats
        
        dtypes, stats_op, properties = cls.attribute_dtype(cls._geom_queried, cls._stats, *args)
        # print(len(np.unique(cls._query_tree[0])))
        array_value = []
        for index in tqdm(np.unique(cls._query_tree[0])):
            join_value = []
            for attribute_name, attribute_type in dtypes.items():
                if stats_op == 'mean':
                    if np.dtype(attribute_type[1]).kind in ['i', 'f']:
                        join_value.append(
                            np.nanmean(
                                cls._geom_queried
                                [cls._query_tree[1]
                                 [np.where(cls._query_tree[0]==index)]]
                                [attribute_name],
                                axis = 0)
                            )
                    elif np.dtype(attribute_type[1]).kind in ['U', 'M']:
                        join_value.append(
                            mode(
                                cls._geom_queried
                                [cls._query_tree[1]
                                 [np.where(cls._query_tree[0]==index)]]
                                [attribute_name])
                            )
                elif stats_op == 'max':
                    if np.dtype(attribute_type[1]).kind in ['i', 'f']:
                        join_value.append(
                            np.nanmax(
                                cls._geom_queried
                                [cls._query_tree[1]
                                 [np.where(cls._query_tree[0]==index)]]
                                [attribute_name],
                                axis = 0)
                            )
                    elif np.dtype(attribute_type[1]).kind in ['U', 'M']:
                        join_value.append(
                            mode(
                                cls._geom_queried
                                [cls._query_tree[1]
                                 [np.where(cls._query_tree[0]==index)]]
                                [attribute_name])
                            )
                elif stats_op == 'min':
                    if np.dtype(attribute_type[1]).kind in ['i', 'f']:
                        join_value.append(
                            np.nanmin(
                                cls._geom_queried
                                [cls._query_tree[1]
                                 [np.where(cls._query_tree[0]==index)]]
                                [attribute_name],
                                axis = 0)
                            )
                    elif np.dtype(attribute_type[1]).kind in ['U', 'M']:
                        join_value.append(
                            mode(
                                cls._geom_queried
                                [cls._query_tree[1]
                                 [np.where(cls._query_tree[0]==index)]]
                                [attribute_name])
                            )
            array_value.append(join_value)
        
        return np.array(
            [tuple(i)
             for i in array_value],
            dtype = [j 
                     for i, j in dtypes.items()]
            ), properties, np.unique(cls._query_tree[0])


class geoprocess:
    
    @classmethod
    def SpatialJoin(
            cls,
            left_data_path: str,
            right_data_path: str,
            predicates: str,
            *args: tuple,
            **kwargs
            ):
        
        cls._left_data_path = left_data_path
        cls._right_data_path = right_data_path
        cls._predicates = predicates
        
        if cls._predicates not in {"intersects", "within", "contains",
                                   "overlaps", "crosses", "touches",
                                   "covers", "contains_properly"
                                   }:
            raise ValueError("{} not an valid predicate".format(cls._predicates))
        
        join_args = dict(
            stats = 'mean'
            )
        
        for key, value in join_args.items():
            if key in kwargs:
                join_args[key] = kwargs[key]
        
        left_array, left_profile = geoprocessing.structured_numpy_array(cls._left_data_path)
        
        right_array, right_profile = geoprocessing.structured_numpy_array(cls._right_data_path)
        
        query_shape = SpatialQuery(
            right_array['geometry']).query_bulk(
                query_geometry = left_array['geometry'],
                predicate = cls._predicates
                )
        
        joined_data, properties, unique_tree_indices = compute_array.spatial_join(
            query_shape,
            right_array,
            join_args['stats'],
            *args
            )
        left_profile['schema']['properties'].update(properties)
        
        try:
            arrays = rfn.merge_arrays([left_array, joined_data], flatten = True, usemask = False)
            print("Binary predicate : - {} - by Regular".format(cls._predicates))
        except ValueError:
            try:
                arrays = rfn.merge_arrays([left_array[unique_tree_indices], joined_data], flatten = True, usemask = False)
                print("Binary predicate : - {} - by Exception".format(cls._predicates))
            except IndexError:
                print("Binary predicate : - {} - not accepted for current spatial operation".format(cls._predicates))
        if args is not None:
            print("For shapefile - '{}', statistics set as '{}' for spatial operation on attribute : - {}".format(
                cls._right_data_path, join_args['stats'], args))
        return arrays, left_profile

mzs_path = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Soil Sample/Panola Farming_South Panola_SP 12_2022_NO Product_1_poly.shp'
swath_poly_path = '/araihan/Reserach_Data/extracted_data/Panola Farming/processed_data/planting_point_swath_poly.shp'
planting = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Planting/Panola Farming_South Panola_SP 12_2022_P1718-PRYME_1.shp'
ecom = '/araihan/Reserach_Data/extracted_data/Panola Farming/ECOM/Panola Farming_South Panola_SP 12_NO Year_TSM_1.shp'
harvest = '/araihan/Reserach_Data/extracted_data/Panola Farming/2022 Harvest/Panola Farming_South Panola_SP 12_2022_CORN_1.shp'

predicate_list = ["intersects", "within", "contains", "overlaps", "crosses", "touches", "covers", "contains_properly"]

datas, profile = geoprocess.SpatialJoin(swath_poly_path, ecom, predicate_list[1], *['R4_mS_m_'])