#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 21 21:23:41 2022

@author: araihan
"""

import rtree
import numpy as np
import warnings
import shapely
import pygeos
from shapely.strtree import STRtree
from tqdm import tqdm
import collections
from statistics import mode
from shapely.errors import ShapelyDeprecationWarning
warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

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
        
        if not isinstance(
                cls.geometry,
                shapely.geometry.base.BaseGeometry
                ):
            raise TypeError(
                "Got `geometry` of type `{}`, `geometry` must be ".format(
                    type(cls.geometry)
                )
                + "a shapely geometry."
            )
        
        if cls.geometry.is_empty:
            return np.array([], dtype=np.intp)
        return cls.geometry
    
    def QueryIndex(
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
        tree_idx = shapely.strtree.STRtree(
            cls._input_geometry
            )
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
                    tree_index.extend(np.sort(np.array(indices, dtype=np.intp)))
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
                        indices = [
                            i for i in tree_idx.query_items(geo)
                            if getattr(geometry, cls._predicate)(cls._input_geometry[i])
                            ]
                        tree_index.extend(np.sort(np.array(indices, dtype=np.intp)))
                else:
                    indices = [i for i in tree_idx.query_items(geo)
                                if getattr(geo, cls._predicate)(cls._input_geometry[i])
                                ]
                    tree_index.extend(np.sort(np.array(indices, dtype=np.intp)))
            input_geom_index.extend([index] * len(indices))
        return np.vstack([input_geom_index, tree_index])


class GeosQuery(pygeos.strtree.STRtree):
    
    def __init__(
            cls,
            tree_geometry:list
            ):
        
        cls._input_geometry = [pygeos.from_shapely(i) for i in tree_geometry]
        super(GeosQuery, cls).__init__(cls._input_geometry)
    
    def QueryIndex(
            cls,
            query_geometry:list,
            predicate:str
            ):
        
        cls._query_geometry = [pygeos.from_shapely(i) for i in query_geometry]
        cls._predicate = predicate
        
        valid_predicates = {p.name for p in pygeos.strtree.BinaryPredicate}
        if cls._predicate not in valid_predicates:
            raise ValueError(
                "Got `predicate` = `{}`, `predicate` must be one of {}".format(
                    cls._predicate, valid_predicates
                )
            )
        
        geostree = pygeos.strtree.STRtree(cls._input_geometry)
        
        tree_index = []
        input_geometry_index = []
        for i, geom in enumerate(cls._query_geometry):
            idx = geostree.query(geom, predicate=cls._predicate).tolist()
            tree_index.extend(np.sort(np.array(idx, dtype = np.intp)))
            input_geometry_index.extend([i] * len(idx))
        return np.vstack([input_geometry_index, tree_index])


class RtreeQuery(rtree.index.Index):
    
    def __init__(
            cls,
            tree_geometry
            ):
        
        cls._input_geometry = tree_geometry
        cls._tree_indices = rtree.index.Index()
        for i, j in np.ndenumerate(cls._input_geometry):cls._tree_indices.insert(i[0], j.bounds)
        super().__init__()
    
    def query_tree(
            cls,
            query_geom:shapely.geometry.base.BaseGeometry,
            predicate:str = None
            ):
        """

        Parameters
        ----------
        query_geom : shapely.geometry.base.BaseGeometry
            - A shapely BaseGeometry type geometry
        predicate : str, optional
            - valid Binary  predicates as
                ['intersects', 'within', 'contains',\
                 'overlaps', 'crosses', 'touches',
                 'covers', 'contains_properly']. The default is None.
        Raises
        ------
        shapely.predicates.PredicateError
            - If invalid predicate assigned/selected for spatial operation.
        TypeError
            - If 'query_geom' not a valid geometry type.

        Returns
        -------
        np.ndarray
            - indices as np.ndarray from tree index where 'query_geom' returns True after \
                performing spatial operation by assigned 'predicate'.

        """
        cls._query_geom = query_geom
        cls._predicate = predicate
        valid_predicates = {
            None,
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
            raise shapely.predicates.PredicateError(
                "Got `predicate` = `{}`, `predicate` must be one of {}".format(
                    cls._predicate, valid_predicates
                )
            )
        
        if not isinstance(
                cls._query_geom,
                shapely.geometry.base.BaseGeometry
                ):
            raise TypeError(
                'Not a valid type of geometry'
                )
        
        tree_idx = [int(i) for i in cls._tree_indices.intersection(cls._query_geom.bounds)]
        
        if cls._predicate == "within":
            if not isinstance(
                    cls._query_geom,
                    shapely.prepared.PreparedGeometry
                    ):
                cls._query_geom = shapely.prepared.prep(cls._query_geom)
                res = [
                    ind for ind in tree_idx
                    if cls._query_geom.contains(
                    cls._input_geometry[ind])
                    ]
        elif cls._predicate in {
                "contains",
                "intersects",
                "covers",
                "contains_properly"
                }:
            if not isinstance(
                    cls._query_geom,
                    shapely.prepared.PreparedGeometry
                    ):
                cls._query_geom = shapely.prepared.prep(cls._query_geom)
                res = [
                    ind for ind in tree_idx if getattr(
                    cls._query_geom,
                    cls._predicate)(cls._input_geometry[ind])]
        elif cls._predicate is not None:
            res = [
                ind for ind in tree_idx if getattr(
                    cls._query_geom,
                    cls._predicate)(
                        cls._input_geometry[ind]
                        )
                        ]
        else:
            raise shapely.predicates.PredicateError(
                "'{}' not a valid predicate".format(
                    cls._predicate)
                )
        return np.sort(
            np.array(
                res,
                dtype = np.intp)
            )
    
    def QueryIndex(
            cls,
            bulk_geom:np.ndarray,
            predicate:str
            ):
        """

        Parameters
        ----------
        bulk_geom : np.ndarray
            - np.ndarray of geometry as numpy structured array with geometry as object.
        predicates : str
            - valid Binary  predicates as
                ['intersects', 'within', 'contains',\
                 'overlaps', 'crosses', 'touches',
                 'covers', 'contains_properly']

        Returns
        -------
        np.ndarray
            - Index of bulk_geom and tree index by input geometry that get queried by bulk_geom

        """
        cls._bulk_geom = bulk_geom
        cls._predicates = predicate
        
        tree_indices, query_geom_indices = [], []
        for indices, geo in enumerate(cls._bulk_geom):
            tree_id = cls.query_tree(geo, cls._predicates)
            tree_indices.extend(tree_id)
            query_geom_indices.extend([indices] * len(tree_id))
        return np.vstack([query_geom_indices, tree_indices])

class ComputeArray:
    
    @staticmethod
    def _fiona_properties(
            attribute_dict:dict
            )->collections.OrderedDict:
        """

        Parameters
        ----------
        attribute_dict : dict
            - dict type object with re-evaluated attribute name and numpy dtype for each attribute

        Returns
        -------
        OrderedDict
            - 'properties' for fiona profile which includes attributes name and dtype for each attribute

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
        return collections.OrderedDict(dict_item)
    
    @classmethod
    def attribute_dtype(
            cls,
            arrays: np.ndarray,
            stat_type: str,
            *args: tuple
            ) -> dict:
        """

        Parameters
        ----------
        arrays : np.ndarray
            - numpy.ndarray of data.
        stat_type : str
            - Statistics to perform on 'geom_queried' numpy.ndarray attributes - ['mean', 'max', 'min']
        *args : tuple
            - list of available/selected attributes.

        Raises
        ------
        ValueError
            - If 'stat_type' is not any of the following ['mean', 'max', 'min']
        AttributeError
            - If selected/available attributes is not available into 'arrays' structured numpy.ndarray
        TypeError
            DESCRIPTION.
        ValueError
            - If any attribute name repeated more than once into 'arrays' as structured numpy.ndarray

        Returns
        -------
        dict
            1. dict type object with re-evaluated attribute name and numpy dtype for each attribute
            2. One of the selected stat_type from ['mean', 'max', 'min']

        """
        cls._arrays = arrays
        cls._stat_type = stat_type
        
        if cls._stat_type not in ['max', 'min', 'mean']:
            raise ValueError(
                "'{}' is not accepted, select one valid statistics from ['max', 'min', 'mean']".format(
                    cls._stat_type)
                )
        
        all_attrs = [i for i, j in cls._arrays.dtype.descr]
        if len(args) == 0:
            attrs = [i for i, j in cls._arrays.dtype.descr if not np.dtype(j).kind in ['O']]
        else:
            attrs = [arg for arg in args]
        
        for arg in args:
            if arg not in all_attrs:
                raise AttributeError(
                    "{} not available into the numpy structured array, \
                        please assign correct attribute name".format(arg))
        
        dtype_dict, unique_items = {}, []
        for i, j in cls._arrays.dtype.descr:
            if i in attrs:
                if np.dtype(j).kind in ['i', 'f']:
                    ivals = ''.join([*[st for st in filter(str.isalnum, i)][:7], '_', cls._stat_type])[:30]
                    if ivals not in unique_items:
                        unique_items.append(ivals)
                        dtype_dict[i] = (''.join([*[st for st in filter(str.isalnum, i)][:7], '_', cls._stat_type])[:30], j)
                    else:
                        dtype_dict[i] = (''.join([*[st for st in filter(str.isalnum, i)], '_', cls._stat_type])[:30], j)
                elif np.dtype(j).kind in ['U', 'M']:
                    uvals = ''.join([*[st for st in filter(str.isalnum, i)][:7], '_', 'major'])[:30]
                    if uvals not in unique_items:
                        unique_items.append(uvals)
                        dtype_dict[i] = (''.join([*[st for st in filter(str.isalnum, i)][:7], '_', 'major'])[:30], j)
                    else:
                        dtype_dict[i] = (''.join([*[st for st in filter(str.isalnum, i)], '_', 'major'])[:30], j)
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
                        
        return dtype_dict, stat_type
    
    @classmethod
    def spatial_join(
            cls,
            query_tree: np.ndarray,
            parent_geom:np.ndarray,
            geom_queried: np.ndarray,
            stats: str,
            *args: tuple
            ):
        """

        Parameters
        ----------
        query_tree : np.ndarray
            - Query Tree index as numpy.ndarray
        geom_queried : np.array
            - Numpy structured array for geometry to estimate spatial query based on.
        stats : str
            - Statistics to perform on 'geom_queried' numpy.ndarray attributes - ['mean', 'max', 'min']
        *args : tuple
            - list of available/selected attributes.

        Returns
        -------
        numpy.ndarray
            Numpy.ndarray of data after compute statistics

        """
        cls._query_tree = query_tree
        cls._parent_geom = parent_geom
        cls._geom_queried = geom_queried
        cls._stats = stats
        
        dtypes, stats_op = cls.attribute_dtype(cls._geom_queried, cls._stats, *args)
        # print(len(np.unique(cls._query_tree[0])))
        array_value = []
        for index in tqdm(range(len(cls._parent_geom))):
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
                        try:
                            join_value.append(
                                mode(
                                    cls._geom_queried
                                    [cls._query_tree[1]
                                      [np.where(cls._query_tree[0]==index)]]
                                    [attribute_name])
                                )
                        except:
                            join_value.append(None)
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
                        try:
                            join_value.append(
                                mode(
                                    cls._geom_queried
                                    [cls._query_tree[1]
                                      [np.where(cls._query_tree[0]==index)]]
                                    [attribute_name])
                                )
                        except:
                            join_value.append(None)
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
                        try:
                            join_value.append(
                                mode(
                                    cls._geom_queried
                                    [cls._query_tree[1]
                                      [np.where(cls._query_tree[0]==index)]]
                                    [attribute_name])
                                )
                        except:
                            join_value.append(None)
            array_value.append(join_value)
        rename_dtype = lambda parent, query : {
            i:(i, j)
            for i, j in
            {
             {
              i[0]:str(str(i[0][:-1])+str(int(i[0][-1])+1))
              if i[0][-1].isdigit() else str(str(i[0])+str(1))
              for i in query.values()
              if i[0] in parent.dtype.names
              and i[0] not in 'geometry'
              }.get(k, k): v
             for k, v in collections.OrderedDict(
                     {i[0]:i[1]
                      for i in query.values() if i[0] not in 'geometry'}
                     ).items()
             }.items()}
        dtypes_changed = [rename_dtype(cls._parent_geom, dtypes) if len(rename_dtype(cls._parent_geom, dtypes))>0 else dtypes]
        # print(dtypes_changed[0])
        return np.array(
            [tuple(i)
              for i in array_value],
            dtype = [j 
                      for i, j in dtypes_changed[0].items()]
            )
