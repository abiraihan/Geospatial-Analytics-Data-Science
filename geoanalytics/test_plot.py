#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 21:40:24 2023

@author: kali
"""
import os
import numpy as np
import shapely
import pyproj
import os
import fiona
import tempfile
import numpy as np
import geopandas as gpd
import pandas as pd
import warnings
from geoanalytics.utils.utils import utils
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager, colormaps
from matplotlib.colors import ListedColormap

from matplotlib import font_manager, colormaps


def fonts():
    """
    Returns
    -------
    dict
        - fontpath values with font name as key

    """
    font_dirs ='/home/kali/geolytics/Geospatial-Analytics-Data-Science/geoanalytics/reporting/fonts/'
    return {
        os.path.basename(i).split('.', 1)[0]:i
        for i in [
                os.path.join(
                    font_dirs, i
                    )
                for i in os.listdir(font_dirs)
                if os.path.basename(i).split('.', 1)[1] == 'ttf'
                ]
             }



from statistics import mean

def dict_values_update(dict_obj):
    
    dft, val_log = {}, 0
    for i, j in dict_obj.items():
        if len(dict_obj) > 10:
            if j < 0.3:
                val_log += j
            else:
                dft[i] = j+val_log
                val_log = 0
        else:
            if j < 0.1:
                val_log += j
            else:
                dft[i] = j+val_log
                val_log = 0
    return dict(reversed(dft.items()))

def rate_area_sorting(rate_value_dict):
    value_dict = {
        m: round(n, 1)
        for m, n in
        dict_values_update(
            dict_values_update(
                {i:j for i, j in dict(
                        sorted({k:v for k, v in rate_value_dict.items()}.items())
                        ).items() if any([j!=0])})).items()
        }
    
    dx = {
          i:value_dict[i]
          for i in np.arange(
                  min([i for i, j in
                       value_dict.items()]
                      ),
                  max([i for i, j in
                       value_dict.items()]) + 1,
              1) if i in list(value_dict.keys())
          }
    
    return {
          i:int(v)
          if v.is_integer()
          else v
          for i, v in dx.items()
          }
rates_data = {33: 1.9, 34: 4.9, 35: 41.1, 36: 8.7, 37: 1.3, 38: 0, 39: 1.3}


data = {36: 8.74241162113261,
        25: 0.039427838901283714,
        30: 0.12557480625419176,
        32: 0.36048482990495645,
        33: 0.9573523004618171,
        34: 4.882318273660064,
        35: 41.08671928295422,
        37: 1.2727697325717366,
        38: 0.3657923899838434,
        39: 0.9451507698955186,
        31: 0.13063733596384963,
        29: 0.0865445545395895,
        27: 0.0499951292038606,
        24: 0.016012600457062355,
        44: 0.014470298159117646,
        47: 0.004913476078328718,
        41: 0.054676722981497984,
        46: 0.0053073538156198025,
        42: 0.07429510560281405,
        28: 0.06472127358212847,
        23: 0.008577745121138697,
        26: 0.025950241986404207,
        40: 0.1470910938011622,
        22: 0.006910381801447532,
        43: 0.03415485025696055,
        49: 0.003885412227464671}

sorted_data = dict(sorted({k:v for k, v in data.items()}.items()))

dft, val_log = {}, 0
for i, j in sorted_data.items():
    if j < 0.5:
        val_log += sorted_data[i]
    else:
        dft[i] = val_log + sorted_data[i]
        val_log = 0
        print(sorted_data[i], dft[i])
    
    print(val_log)

df_max = max(list(dft.keys()))

if max(list(sorted_data.keys())) > df_max:
    for i, j in sorted_data.items():
        if i > df_max: 
            dft[df_max] += sorted_data[i]

# fg = dict_values_update(data)


# value_dict = rate_area_sorting(data)
# dx = {
#       i:value_dict[i]
#       if i in list(value_dict.keys())
#       else value_dict[i+1] 
#       for i in np.arange(
#               min([i for i, j in
#                    value_dict.items()]
#                   ),
#               max([i for i, j in
#                    value_dict.items()]) + 1,
#           1)
#       }


# db = PlantingRateBarLegend(data, bar_legend_filepath = './bar_def.png')

# dc = PlantingRateColorLegend(data, cmaps_legend_filepath = './bar_def.png')






