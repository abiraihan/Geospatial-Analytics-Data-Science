#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 03:55:35 2022

@author: araihan
"""

import numpy as np
import shapely
import pyproj

def gridBounds(
        polyBounds:shapely.geometry.base.BaseGeometry,
        polyCRS:int,
        sideLength:(float, int) = 10,
        reproject:bool = False
        )->np.ndarray :
    """

    Parameters
    ----------
    polyBounds : shapely.geometry.base.BaseGeometry
        - a valid shapely geometry
    polyCRS : int
        - EPSG code as int
    sideLength : (float, int), optional
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
    if not isinstance(polyBounds, shapely.geometry.base.BaseGeometry):
        raise TypeError("{} not a valid geometry type".format(type(polyBounds)))
    if getattr(polyBounds, 'is_empty'):
        raise ValueError("{} is an empty geometry".format(polyBounds))
    
    projection = lambda geog, proj : pyproj.Transformer.from_crs(
        crs_from=pyproj.CRS.from_user_input(geog),
        crs_to=pyproj.CRS.from_user_input(proj),
        always_xy=True
        ).transform
    projected_bound = shapely.ops.transform(
        projection(polyCRS, 3857),
        polyBounds)
    if float('inf') in projected_bound.bounds:
        raise ValueError("{} geometry extent is not a valid one,\
                          please set a valid geometry".format(projected_bound.bounds))
    minx, miny, maxx, maxy = projected_bound.bounds
    x = np.linspace(minx, maxx, int(abs(minx-maxx)/sideLength))
    y = np.linspace(miny, maxy, int(abs(miny-maxy)/sideLength))
    ncol, nrow = len(x)-1, len(y)-1

    hlines = [((xi, yi), (xj, yi)) for xi, xj in zip(x[:-1], x[1:]) for yi in y]
    vlines = [((xi, yi), (xi, yj)) for yi, yj in zip(y[:-1], y[1:]) for xi in x]
    
    grid_geoms = list(
        shapely.ops.polygonize(
            shapely.geometry.MultiLineString(
                hlines+vlines
                )
            )
        )
    if reproject:
        return np.array(
            grid_geoms,
            dtype = [('geometry', object)]
            ), (ncol, nrow)

    return np.array(
        [shapely.ops.transform(
            projection(
                3857,
                polyCRS
                ), i)
            for i in grid_geoms],
        dtype = [('geometry', object)]
        ), (ncol, nrow)

def getColumnLen(gridData:list, sourceCrs:int):
    projection = lambda geog, proj : pyproj.Transformer.from_crs(
        crs_from=pyproj.CRS.from_user_input(geog),
        crs_to=pyproj.CRS.from_user_input(proj),
        always_xy=True
        ).transform
    
    getbnds = shapely.ops.unary_union(gridData)
    
    projected_bound = shapely.ops.transform(
        projection(4326, 3857),
        getbnds)
    
    minx, miny, maxx, maxy = projected_bound.bounds
    
    return len(np.linspace(minx, maxx, int(abs(minx-maxx)/10))) - 1