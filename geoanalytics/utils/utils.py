#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:22:50 2022

@author: raihan
"""

import warnings
import shapely
from shapely.geometry import Polygon
from pyproj import CRS
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_crs_info, query_utm_crs_info

class utils:

    @classmethod
    def swathpoly(
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
        cls._y_axis_length = y_axis_length #Distance
        cls._x_axis_length = x_axis_length #Swath
        cls._rotation_angle = rotation_angle #Track
 
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
        
        ymax = cls._point_origin[1] + (cls._y_axis_length/2)
        ymin = cls._point_origin[1] - (cls._y_axis_length/2)
        
        if keyword_args['y_axis_offset'] != 0:
            if keyword_args['y_axis_offset'] < 0 and cls._rotation_angle >= 180:
                xmax = ((cls._x_axis_length/2) + cls._point_origin[0]) + keyword_args['y_axis_offset']
                xmin = (cls._point_origin[0] - (cls._x_axis_length/2)) + keyword_args['y_axis_offset']
            elif keyword_args['y_axis_offset'] < 0 and cls._rotation_angle < 180:
                xmax = ((cls._x_axis_length/2) + cls._point_origin[0]) - keyword_args['y_axis_offset']
                xmin = (cls._point_origin[0] - (cls._x_axis_length/2)) - keyword_args['y_axis_offset']
            elif keyword_args['y_axis_offset'] > 0 and cls._rotation_angle < 180:
                xmax = ((cls._x_axis_length/2) + cls._point_origin[0]) - keyword_args['y_axis_offset']
                xmin = (cls._point_origin[0] - (cls._x_axis_length/2)) - keyword_args['y_axis_offset']
            elif keyword_args['y_axis_offset'] > 0 and cls._rotation_angle >= 180:
                xmax = ((cls._x_axis_length/2) + cls._point_origin[0]) + keyword_args['y_axis_offset']
                xmin = (cls._point_origin[0] - (cls._x_axis_length/2)) + keyword_args['y_axis_offset']
            else:
                xmax = (cls._x_axis_length/2) + cls._point_origin[0]
                xmin = cls._point_origin[0] - (cls._x_axis_length/2)
        else:
            xmax = (cls._x_axis_length/2) + cls._point_origin[0]
            xmin = cls._point_origin[0] - (cls._x_axis_length/2)
            
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
     
    @staticmethod
    def find_spcs(
            geoms:shapely.geometry,
            utm_datum:str = None,
            area_of_use:bool = False
            )-> dict:
        """

        Parameters
        ----------
        geoms : shapely.geometry
            DESCRIPTION. shapely.geometry object \n
        area_of_use : bool, optional
            DESCRIPTION. The default is False. \n
        utm_datum : str, optional
            DESCRIPTION. The default is None. \n
            
        Returns
        -------
        dict
            DESCRIPTION. Dict items with EPSG - 'US Survey Code'

        """
        # UTM Datum can be
        # 'WGS84'- for geographic (On ellipsoid/sphere),
        # 'NAD83' - For Projected (On Plane), 'NAD27'
        # use of def:
        # d = Point(-93.312345, 40.754346)
        # sp = find_spcs(d, 'NAD83')
        xmin, ymin, xmax, ymax = geoms.bounds
        spc_crs = query_crs_info(auth_name = 'EPSG',
        pj_types = 'PROJECTED_CRS',
        area_of_interest=AreaOfInterest(
            west_lon_degree=xmin,
            south_lat_degree=ymin,
            east_lon_degree=xmax,
            north_lat_degree=ymax,
        ),contains = True)
        
        if utm_datum is not None:
            utm_crs = query_utm_crs_info(
                datum_name= utm_datum,
            area_of_interest=AreaOfInterest(
                west_lon_degree=xmin,
                south_lat_degree=ymin,
                east_lon_degree=xmax,
                north_lat_degree=ymax,
            ),)
        else:
            utm_crs = query_utm_crs_info(
                datum_name= 'NAD83',
            area_of_interest=AreaOfInterest(
                west_lon_degree=xmin,
                south_lat_degree=ymin,
                east_lon_degree=xmax,
                north_lat_degree=ymax,
            ),)
        
        epsg_cod = []
        for i in spc_crs:
            if CRS.from_epsg(i.code).axis_info[0].unit_name == 'US survey foot':
                if i.code not in epsg_cod:
                    epsg_cod.append(i.code)
        try:
            epsg_code = [i.code
                        for i in spc_crs
                        if i.projection_method_name == 'Lambert Conic Conformal (2SP)' and
                        CRS.from_epsg(i.code).axis_info[0].unit_name == 'US survey foot'][0]
            final_crs = {
                'spcs' : int(epsg_code),
                'spcs_unit' : CRS.from_epsg(epsg_code).axis_info[0].unit_name
                }
        except IndexError:
            epsg_code = [i.code
                        for i in spc_crs
                        if i.projection_method_name == 'Transverse Mercator' and
                        CRS.from_epsg(i.code).axis_info[0].unit_name == 'US survey foot'][0]
            final_crs = {
                'spcs' : int(epsg_code),
                'spcs_unit' : CRS.from_epsg(epsg_code).axis_info[0].unit_name
                }
        
        final_crs['utm'] = int(utm_crs[0].code)
        final_crs['comp_code'] = int(epsg_cod[0])
        
        if final_crs['comp_code'] == final_crs['spcs']:
            final_crs['Match'] = True
        else:
            final_crs['Match'] = False
        
        if utm_datum is None:
            final_crs['datum'] = 'NAD83'
        else:
            final_crs['datum'] = utm_datum
        
        final_crs['projected'] = CRS.from_epsg(final_crs['spcs']).is_projected
        if area_of_use:
            final_crs['area_of_use'] = CRS.from_epsg(final_crs['spcs']).area_of_use.name
        
        return final_crs
