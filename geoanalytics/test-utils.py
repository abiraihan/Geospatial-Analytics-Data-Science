#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 18:23:09 2022

@author: raihan
"""

import os
import re
import fiona
import random
import pyproj
import numpy as np
from osgeo import osr
from tqdm import tqdm
from collections import OrderedDict
from core import geoprocessing
from shapely.geometry import Polygon, mapping, MultiPolygon
from shapely.ops import transform
from sklearn.linear_model import LinearRegression
import zipfile


dirPath = '/home/raihan/2018'
outDirs = '/home/raihan/ExportData'
findFile = lambda dirs, ext:[os.path.join(dirs, i) for i in os.listdir(dirs) if os.path.splitext(i)[1] == str('.'+(ext))]

# zipExtract = lambda zipfiles, outDirs : zipfile.ZipFile(zipfiles, 'r').extractall(outDirs)
# zipfiledirs = '/home/raihan/Data'
# fileZip = findFile(zipfiledirs, 'zip')
# zipExtract(fileZip[0], out)

# filesname = OrderedDict()
# filesname['inpath'] = findFile(dirPath, 'shp')[random.randint(0, len(findFile(dirPath, 'shp'))-1)]
# filesname['outputDirs'] = outDirs
# filesname['fileNames'] = None
# filesname['targetEPSG'] = None
# filesname['xycoords'] = True
# filesname['removeIdentical'] = True
# filesname['attribute'] = None
# filesname['outpath'] = geoprocessing.remove_identical_point(filesname['inpath'], **filesname)

# array, profile = geoprocessing.structured_numpy_array(filesname['outpath'])
# example of manual way to create a numpy unstructured array from structured numpy array
# example = np.array([array['attr1'], array['attr2']]).T
# attr = [i for i, j in profile['schema']['properties'].items() if re.split(r":", j)[0] == 'float']
# y = np.array([array['attr3']]).T
# for i in attr:
#     X = np.array([array[i]]).T
#     reg = LinearRegression().fit(X, y)
#     print(f" r-square : {reg.score(X, y)} : {i}")
# coords = np.array([array['lat'], array['lon']]).T


dataDirs = '/home/raihan/output_dirs'


