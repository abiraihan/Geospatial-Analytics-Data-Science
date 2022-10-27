#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:22:50 2022

@author: raihan
"""

import warnings
import shapely

class utils:
    
    @classmethod
    def point_to_poly(
            cls,
            point_origin:tuple,
            y_axis_length:float,
            x_axis_length:float,
            rotation_angle:float,
            **kwargs
            ) -> shapely.geometry.Polygon:
        '''

        Parameters
        ----------
        point_origin : tuple
            - (x, y) coordinates of a point location.
        y_axis_length : float
            - y-axis length of a sqaure/rectangle polygon.
        x_axis_length : float
            - x-axis length of a sqaure/rectangle polygon.
        rotation_angle : float
            - rotaion angle of the polygon at point_origin .
        **kwargs : keyword args
            - y_axis_offset : y axis offset of y_axis_length.
            - x_axis_tolerance : x axis tolerance of how much x-axis should be increased or decreased on top of x_axis_length
            - y_axis_tolerance : y axis tolerance of how much y-axis should be increased or decreased on top of y_axis_length

        Returns
        -------
        polyshape : shapely.geometry.Polygon
            - a shapely polygon geometry.
        '''
        
        cls._point_origin = point_origin
        cls._y_axis_length = y_axis_length
        cls._x_axis_length = x_axis_length
        cls._rotation_angle = rotation_angle
        
        ft_deg = lambda x : (x*0.3047999902464003)/1e5
 
        keyword_args = dict(
            y_axis_offset = 0,
            x_axis_tolerance = 0,
            y_axis_tolerance = 0
            )
        
        if cls._rotation_angle > 360 or cls._rotation_angle < 0:
            warnings.formatwarning = lambda msg, *args, **kwargs: f'{msg}\n'
            warnings.warn(f'--- Found Track degree out of bounds of {cls._rotation_angle}')
        
        for key, value in keyword_args.items():
            if key in kwargs:
                keyword_args[key] = kwargs[key]
        
        if keyword_args['x_axis_tolerance'] != 0 and keyword_args['y_axis_tolerance'] != 0:
            cls._x_axis_length = cls._x_axis_length + float(keyword_args['x_axis_tolerance'])
            cls._y_axis_length = cls._y_axis_length + float(keyword_args['y_axis_tolerance'])
        elif keyword_args['x_axis_tolerance'] != 0 and keyword_args['y_axis_tolerance'] == 0:
            cls._x_axis_length = cls._x_axis_length + float(keyword_args['x_axis_tolerance'])
            cls._y_axis_length = cls._y_axis_length
        elif keyword_args['x_axis_tolerance'] == 0 and keyword_args['y_axis_tolerance'] != 0:
            cls._x_axis_length = cls._x_axis_length
            cls._y_axis_length = cls._y_axis_length + float(keyword_args['y_axis_tolerance'])
        else:
            cls._x_axis_length = cls._x_axis_length
            cls._y_axis_length = cls._y_axis_length
        
        ymax = cls._point_origin[1] + ft_deg(cls._y_axis_length)/2
        ymin = cls._point_origin[1] - ft_deg(cls._y_axis_length)/2
        
        if keyword_args['y_axis_offset'] != 0:
            if keyword_args['y_axis_offset'] < 0 and cls._rotation_angle >= 180:
                xmax = (ft_deg(cls._x_axis_length)/2 + cls._point_origin[0]) + ft_deg(keyword_args['y_axis_offset'])
                xmin = (cls._point_origin[0] - ft_deg(cls._x_axis_length)/2) + ft_deg(keyword_args['y_axis_offset'])
            elif keyword_args['y_axis_offset'] < 0 and cls._rotation_angle < 180:
                xmax = (ft_deg(cls._x_axis_length)/2 + cls._point_origin[0]) - ft_deg(keyword_args['y_axis_offset'])
                xmin = (cls._point_origin[0] - ft_deg(cls._x_axis_length)/2) - ft_deg(keyword_args['y_axis_offset'])
            elif keyword_args['y_axis_offset'] > 0 and cls._rotation_angle < 180:
                xmax = (ft_deg(cls._x_axis_length)/2 + cls._point_origin[0]) - ft_deg(keyword_args['y_axis_offset'])
                xmin = (cls._point_origin[0] - ft_deg(cls._x_axis_length)/2) - ft_deg(keyword_args['y_axis_offset'])
            elif keyword_args['y_axis_offset'] > 0 and cls._rotation_angle >= 180:
                xmax = (ft_deg(cls._x_axis_length)/2 + cls._point_origin[0]) + ft_deg(keyword_args['y_axis_offset'])
                xmin = (cls._point_origin[0] - ft_deg(cls._x_axis_length)/2) + ft_deg(keyword_args['y_axis_offset'])
            else:
                xmax = ft_deg(cls._x_axis_length)/2 + cls._point_origin[0]
                xmin = cls._point_origin[0] - ft_deg(cls._x_axis_length)/2
        else:
            xmax = ft_deg(cls._x_axis_length)/2 + cls._point_origin[0]
            xmin = cls._point_origin[0] - ft_deg(cls._x_axis_length)/2
            
        deg180 = lambda x , y: x - y*(x//y)
        
        poly = shapely.geometry.Polygon([[xmax, ymin], [xmax, ymax], [xmin, ymax], [xmin, ymin]])
        if cls._rotation_angle <= 180:
            polyshape = shapely.affinity.rotate(poly, (180 - cls._rotation_angle), origin = cls._point_origin)
        elif 180 < cls._rotation_angle <= 360:
            polyshape = shapely.affinity.rotate(poly, (360 - cls._rotation_angle), origin = cls._point_origin)
        elif cls._rotation_angle > 360:
            polyshape = shapely.affinity.rotate(poly, deg180(cls._rotation_angle, 180), origin = cls._point_origin)
        else:
            polyshape = shapely.affinity.rotate(poly, cls._rotation_angle, origin = cls._point_origin)
        return polyshape