#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:22:19 2022

@author: raihan
"""

import os
import re
import fiona
import pyproj
import numpy as np
from osgeo import osr
from tqdm import tqdm
from collections import OrderedDict
from shapely.geometry import Point, mapping



class geoprocessing:
    
    @staticmethod
    def get_attribute_index():
        pass
