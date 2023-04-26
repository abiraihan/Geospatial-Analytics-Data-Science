"""
Created on Fri Sep 30 04:42:24 2022

@author: araihan
"""

import numpy as np
import fiona
import shapely
import pyproj
from tqdm import tqdm
import pandas as pd
from geoanalytics.utils.utils import utils
from geoanalytics.base.base import geoprocessing, geo_array

class geotranslate:
    
    __repr__ = lambda cls : cls.__name__
    
    def __init__(cls, filepath):
        
        cls.filepath = filepath
        
        if isinstance(cls.filepath, str):
            cls.__data__ = geoprocessing.structured_numpy_array(cls.filepath)
            cls._crs = int(fiona.open(cls.filepath, 'r').crs['init'].split(':')[1])
        elif isinstance(cls.filepath, geo_array):
            cls.__data__ = cls.filepath
            cls._crs = cls.filepath.crs
        # elif isinstance(cls.filepath, np.ndarray):
        #     cls.__data__ = cls.filepath
            # cls._crs = cls.filepath.crs
        elif isinstance(cls.filepath, geotranslate):
            cls.__data__ = cls.filepath.__data__
            cls._crs = cls.filepath.crs
        else:
            raise TypeError("'{}' initiatlized data not a filepath or numpy.ndarray".format(type(filepath)))
    
    def __repr__(cls):
        return '{}'.format(pd.DataFrame(data = cls.__data__))
    
    def __str__(cls):
        return '{}'.format(pd.DataFrame(data = cls.__data__))
    
    def __getitem__(cls, key):
        if isinstance(key, str):
            return geo_array(getattr(cls, '__data__')[key], cls.crs)
        else:
            return geo_array(getattr(cls, '__data__')[[i for i in key]], cls.crs)
        
    def __setitem__(cls, name, value):
        from numpy.lib import recfunctions
        ndarray = np.array(value, dtype= [(str(name), value.dtype.descr[0][1])])
        cls.__data__ = geo_array(recfunctions.merge_arrays(
            [cls.__data__, ndarray],
            flatten=True,
            usemask=False
            ), cls.crs)
        return cls.__data__
    
    def __delitem__(cls, key):
        from numpy.lib import recfunctions
        if key not in 'geometry':
            cls.__data__ = geo_array(recfunctions.drop_fields(cls.__data__, key), cls.crs)
            return cls.__data__
        else:
            raise ValueError("'{}' can't be deleted".format(key))
    
    def __len__(cls):
        return len(cls.__data__)
    
    #fix problem
    #ValueError: setting an array element with a sequence. The requested array has an inhomogeneous shape after 1 dimensions. The detected shape was (5349,) + inhomogeneous part.
    def to_crs(cls, _crs_code):
        from numpy.lib import recfunctions
        projection = lambda geog, proj : pyproj.Transformer.from_crs(
            crs_from=pyproj.CRS.from_user_input(geog),
            crs_to=pyproj.CRS.from_user_input(proj),
            always_xy=True
            ).transform
        projected = []
        for i in tqdm(cls.__data__['geometry']):
            projected.append((shapely.ops.transform(projection(cls.crs, int(_crs_code)), i)))
        data = recfunctions.drop_fields(cls.__data__, 'geometry')
        arrays = np.array(projected, dtype = [('geometry', object)])
        cls.__data__ = geo_array(recfunctions.merge_arrays(
            [arrays, data],
            flatten=True,
            usemask=False
            ), int(_crs_code))
        cls.crs = int(_crs_code)
        return cls.__data__
    
    def unique(cls, key):
        """

        Parameters
        ----------
        key : TYPE
            - Atttribute/Column name of the record array

        Returns
        -------
        TYPE
            - Numpy array of unique records

        """
        return np.unique(cls.__getitem__(key))
    
    def __getSwathPoly__(cls, x_length, y_length, rotation):
        arraysd = []
        for i in cls.__data__:
            geoms = utils.swathpoly((i['geometry'].x, i['geometry'].y), i[x_length], i[y_length], i[rotation])
            array_val = [geoms, *[val for val in i][1:]]
            arraysd.append(tuple(array_val))
        return geo_array(np.array(arraysd, dtype = cls.dtype), crs = cls.crs)
    
    @property
    def crs(cls):
        return cls._crs
    
    @crs.setter
    def crs(cls, values):
        cls._crs = values
    
    @crs.deleter
    def crs(cls):
        del cls._crs
    
    @property
    def as_pandas(cls):
        return pd.DataFrame(data = cls.__data__)
    
    @property
    def attribute(cls):
        return [i for i in cls.__data__.dtype.names]
    
    @property
    def geom_type(cls):
        if isinstance(cls.filepath, str): 
            read_file = fiona.open(cls.filepath)
            geo = read_file.schema['geometry']
            read_file.close()
            return geo
        elif isinstance(cls.filepath, geotranslate):
            return cls.filepath.geom_type
        elif isinstance(cls.filepath, geo_array):
            return np.unique([i.geom_type for i in cls.__data__['geometry']])[0]
        else:
            return None
    
    @property
    def dtype(cls):
        return cls.__data__.dtype.descr
    
    @property
    def geometry(cls):
        return np.array(cls.__data__['geometry'], dtype = [('geometry', object)])
    
    @property
    def is_valid(cls):
        for i in cls.geometry:
            if i[0].is_valid:
                return True
            else:
                return False
    
    @property
    def is_empty(cls):
        for i in cls.geometry:
            if i[0].is_empty:
                return True
            else:
                return False
    
    @property
    def unary_union(cls):
        return shapely.ops.unary_union([i[0] for i in list(cls.geometry)])
    
    @property
    def profile(cls):
        read_file = fiona.open(cls.filepath, 'r')
        geo = read_file.profile
        read_file.close()
        return geo
    
    @property
    def centroid(cls):
        return [i.centroid for i in cls.__data__['geometry']]
    
    @property
    def representative_point(cls):
        return [i.representative_point() for i in cls.__data__['geometry']]
    
    @property
    def explain_validity(cls):
        from shapely.validation import explain_validity
        data = {}
        for i, j in enumerate(cls.geometry['geometry']):
            data[i] = explain_validity(j)
        
        validity = {}
        for i, j in data.items():
            if j not in 'Valid Geometry':
                validity[i] = j
        if len(validity) == 0:
            print('No invalid geometry found')
        else:
            print('Invalid geometry found')
        return validity

# import os
# plant_data = '/home/kali/Data/Corn_AsPlanted'
# files = [os.path.join(plant_data, i) for i in os.listdir(plant_data) if os.path.basename(i).split('.', 1)[1] == 'shp'][0]

# dr = geotranslate(files)
