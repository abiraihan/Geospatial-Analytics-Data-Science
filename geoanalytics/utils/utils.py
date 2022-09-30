#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:22:50 2022

@author: raihan
"""

import numpy as np
import fiona
import re
import warnings
import geopandas as gpd
from tqdm import tqdm
import shapely

class _process_geometry:
    
    @classmethod
    def _point_to_poly(
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
            - x_axis_tolerance : x axis tolerance of how much x-axis should be increased of decreased on top of x_axis_length
            - y_axis_tolerance : y axis tolerance of how much y-axis should be increased of decreased on top of y_axis_length

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
    
    @staticmethod
    def get_polygon(files,
                    attribute:list,
                    **kwargs
                    ):
        #example of attribute = ['Distance_f', 'Swth_Wdth_', 'Track_deg_']
        #example of **kwargs is tolerances = 5 in feet and distances = 5 in feet
        #and yoffset is gonna be the column of the y_offset as name
        # get_polygon(i, ['Distance_f', 'Swth_Wdth_', 'Track_deg_'], yoffset = 'Y_Offset_f')
        keyword_args = dict(
            yoffset = None,
            tolerances = 0,
            distances = 0
            )
        
        for key, value in keyword_args.items():
            if key in kwargs:
                keyword_args[key] = kwargs[key]
        if isinstance(files, str):
            geomsArray = []
            with fiona.open(files, 'r') as file:
                crsNumber = re.split(r'[:]', file.crs['init'])[1]
                fileAttributes = [i for i in file.schema['properties'].keys()]
                for geoms in tqdm(file, desc = f'{len(file)} ', colour = 'blue'):
                    if isinstance(keyword_args['yoffset'], str):
                        try:
                            swathpolygon = cleandata.swath_poly(
                                geoms['geometry']['coordinates'],
                                float(geoms['properties'][attribute[0]]),
                                float(geoms['properties'][attribute[1]]),
                                float(geoms['properties'][attribute[2]]),
                                yoffset = float(geoms['properties'][keyword_args['yoffset']]),
                                tolerances= keyword_args['tolerances'],
                                distances = keyword_args['distances']
                                )
                            run = 0
                        except KeyError:
                            swathpolygon = cleandata.swath_poly(
                                geoms['geometry']['coordinates'],
                                float(geoms['properties'][attribute[0]]),
                                float(geoms['properties'][attribute[1]]),
                                float(geoms['properties'][attribute[2]]),
                                yoffset = 0.0,
                                tolerances= keyword_args['tolerances'],
                                distances = keyword_args['distances']
                                )
                            run = 2
                    elif isinstance(keyword_args['yoffset'], (int, float)):
                        swathpolygon = cleandata.swath_poly(
                            geoms['geometry']['coordinates'],
                            float(geoms['properties'][attribute[0]]),
                            float(geoms['properties'][attribute[1]]),
                            float(geoms['properties'][attribute[2]]),
                            yoffset = float(keyword_args['yoffset']),
                            tolerances= keyword_args['tolerances'],
                            distances = keyword_args['distances']
                            )
                        run = 1
                    else:
                        swathpolygon = cleandata.swath_poly(
                            geoms['geometry']['coordinates'],
                            float(geoms['properties'][attribute[0]]),
                            float(geoms['properties'][attribute[1]]),
                            float(geoms['properties'][attribute[2]]),
                            yoffset = 0.0,
                            tolerances= keyword_args['tolerances'],
                            distances = keyword_args['distances']
                            )
                        run = 2
                    geomsArray.append([
                        *[geoms['properties'][i]
                          for i in list(geoms['properties'].keys())],
                        swathpolygon]
                        )
            schema = {'geometry': 'Polygon',
                      'properties': dict(file.schema['properties'])
                      }
            drt = {}
            for i, j in dict(file.schema['properties']).items():
                drt[i] = re.split(r'[:]', j)[0]
                if j == 'date':
                    drt[i] = 'datetime64[ns]'
            gdf = gpd.GeoDataFrame(
                np.array(geomsArray, dtype=object),
                columns=[*fileAttributes, 'geometry'],
                crs = f'EPSG:{crsNumber}',
                geometry = [i[-1] for i in geomsArray]
                ).astype(drt)
            gdf = gdf.set_geometry('geometry')
            
            if run == 2:
                warnings.formatwarning = lambda msg, *args, **kwargs: f'{msg}\n'
                warnings.warn(f"\n--- Couldnt find the yoffset as column or values , y offset set as 0" )
        elif isinstance(files, gpd.GeoDataFrame) and all(files.geometry.geom_type == 'Point') == True:
            dataDict = {i:str(files[i].dtype) for i in list(files.columns)}
            schema = {'geometry': 'Polygon',
                      'properties': {i:str(files[i].dtype) for i in list(files.columns) if i != 'geometry'}
                      }
            crsNumber = files.crs.to_epsg()
            cols = [i for i in files.columns]
            files['coords'] = files.apply(lambda row : (row.geometry.x, row.geometry.y), axis = 1)
            files = files.drop('geometry', axis = 1)
            
            colIndex = {i:files.columns.get_loc(i) for i in attribute}
            
            
            coords_ = files.columns.get_loc('coords')
            
            geomsArray = []
            for i in tqdm(files.values, desc = f'{len(files)} ', colour = 'blue'):
                dfData = i[:coords_]
                if isinstance(keyword_args['yoffset'], str):
                    try:
                        offset_ = files.columns.get_loc(keyword_args['yoffset'])
                        polys = cleandata.swath_poly(
                            xycoords =i[coords_],
                            distance=i[colIndex[attribute[0]]],
                            swath = i[colIndex[attribute[1]]],
                            track_deg = i[colIndex[attribute[2]]],
                            yoffset = i[offset_],
                            tolerances = keyword_args['tolerances'],
                            distances = keyword_args['distances']
                            )
                    except KeyError:
                        polys = cleandata.swath_poly(
                            xycoords =i[coords_],
                            distance=i[colIndex[attribute[0]]],
                            swath = i[colIndex[attribute[1]]],
                            track_deg = i[colIndex[attribute[2]]],
                            yoffset = 0,
                            tolerances = keyword_args['tolerances'],
                            distances = keyword_args['distances']
                            )
                elif isinstance(keyword_args['yoffset'], (int, float)):
                    polys = cleandata.swath_poly(
                        xycoords =i[coords_],
                        distance=i[colIndex[attribute[0]]],
                        swath = i[colIndex[attribute[1]]],
                        track_deg = i[colIndex[attribute[2]]],
                        yoffset = keyword_args['yoffset'],
                        tolerances = keyword_args['tolerances'],
                        distances = keyword_args['distances']
                        )
                else:
                    polys = cleandata.swath_poly(
                        xycoords =i[coords_],
                        distance=i[colIndex[attribute[0]]],
                        swath = i[colIndex[attribute[1]]],
                        track_deg = i[colIndex[attribute[2]]],
                        yoffset = 0.0,
                        tolerances = keyword_args['tolerances'],
                        distances = keyword_args['distances']
                        )
                geomsArray.append([*dfData, polys])
            
            gdf = gpd.GeoDataFrame(
                np.array(geomsArray, dtype=object),
                columns=cols,
                crs = f'EPSG:{crsNumber}',
                geometry = [i[-1] for i in geomsArray]
                ).astype(dataDict)
            gdf = gdf.set_geometry('geometry')
        return gdf, schema, crsNumber