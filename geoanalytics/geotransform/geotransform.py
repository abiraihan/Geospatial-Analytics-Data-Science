#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 03:55:35 2022

@author: araihan
"""

import numpy as np
import shapely
import pyproj
from tqdm import tqdm
from base.base import geo_array
class spatialGrid:
    
    @classmethod
    def squaregrid(
            cls,
            polyBounds:shapely.geometry.base.BaseGeometry,
            polyCRS:int,
            sideLength:int = 10,
            reproject:bool = False
            )->np.ndarray :
        """
    
        Parameters
        ----------
        polyBounds : shapely.geometry.base.BaseGeometry
            - a valid shapely geometry
        polyCRS : int
            - EPSG code as int
        sideLength : int, optional
            -The default is 10 which is in meter based on EPSG:3857
        reproject : bool, optional
            - If reproject is True then peojection will be as the polyCRS EPSG defined else,
                it will return EPSG as 3857 which is a projected CRS in meter
    
        Raises
        ------
        TypeError
            - If polyBounds is not a valid shapely geometry
        ValueError
            1. If polyBounds is a empty geometry
            2. If reprojection on 2D surface for EPSG:3857 is out of a valid extent
    
        Returns
        -------
        numpy.ndarray
            - Structured numpy.ndarray of shapely geometry 
    
        """
        cls._polyBounds = polyBounds
        cls._polyCRS = polyCRS
        cls._sideLength = sideLength
        cls._reproject = reproject
        if not isinstance(cls._polyBounds, shapely.geometry.base.BaseGeometry):
            raise TypeError("{} not a valid geometry type".format(type(cls._polyBounds)))
        if getattr(cls._polyBounds, 'is_empty'):
            raise ValueError("{} is an empty geometry".format(cls._polyBounds))
        
        projection = lambda geog, proj : pyproj.Transformer.from_crs(
            crs_from=pyproj.CRS.from_user_input(geog),
            crs_to=pyproj.CRS.from_user_input(proj),
            always_xy=True
            ).transform
        projected_bound = shapely.ops.transform(
            projection(cls._polyCRS, 3857),
            cls._polyBounds)
        if float('inf') in projected_bound.bounds:
            raise ValueError("{} geometry extent is not a valid one,\
                              please set a valid geometry with valid extent".format(projected_bound.bounds))
        minx, miny, maxx, maxy = projected_bound.bounds
        x = np.linspace(minx, maxx, int(abs(minx-maxx)/cls._sideLength))
        y = np.linspace(miny, maxy, int(abs(miny-maxy)/cls._sideLength))
    
        hlines = [((xi, yi), (xj, yi)) for xi, xj in zip(x[:-1], x[1:]) for yi in y]
        vlines = [((xi, yi), (xi, yj)) for yi, yj in zip(y[:-1], y[1:]) for xi in x]
        
        grid_geoms = list(
            shapely.ops.polygonize(
                shapely.geometry.MultiLineString(
                    hlines+vlines
                    )
                )
            )
        if cls._reproject:
            arrays = np.array(
                grid_geoms,
                dtype = [('geometry', object)]
                )
        else:
            arrays = np.array(
                [shapely.ops.transform(
                projection(
                    3857,
                    cls._polyCRS
                    ), i)
                for i in tqdm(grid_geoms)],
            dtype = [('geometry', object)]
            )
        return geo_array(arrays, cls._polyCRS)
    
    @classmethod
    def getShape(cls, gridData):
        """
        
        Parameters
        ----------
        gridData : list
            - shapely geometry as a list.
        sourceCrs : int
            - CRS of gridData.

        Returns
        -------
        cols : int
            - Number of columns of the gridData.
        rows : int
            - Number of rows of the gridData.

        """
        cls.gridData = gridData
        # if not isinstance(cls.gridData, geo_array):
        #     raise TypeError("Input array should be a {} data type".format(type(cls.gridData)))
        projection = lambda geog, proj : pyproj.Transformer.from_crs(
            crs_from=pyproj.CRS.from_user_input(geog),
            crs_to=pyproj.CRS.from_user_input(proj),
            always_xy=True
            ).transform
        
        lengths = np.sqrt(shapely.ops.transform(projection(cls.gridData.crs, 3857), cls.gridData['geometry'][0]).area)
        getbnds = shapely.ops.unary_union(cls.gridData['geometry'])
        
        projected_bound = shapely.ops.transform(
            projection(cls.gridData.crs, 3857),
            getbnds)
        
        minx, miny, maxx, maxy = projected_bound.bounds
        cols = len(np.linspace(minx, maxx, int(abs(minx-maxx)/int(lengths)))) - 1
        rows = len(np.linspace(miny, maxy, int(abs(miny-maxy)/int(lengths)))) - 1
        return cols, rows