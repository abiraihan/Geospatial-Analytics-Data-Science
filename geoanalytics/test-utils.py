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
import numpy as np
from osgeo import osr
from collections import OrderedDict
from core import geoprocessing


dirPath = '/home/raihan/2018'
outDirs = '/home/raihan/ExportData'
findFile = lambda dirs, ext:[os.path.join(dirPath, i) for i in os.listdir(dirs) if os.path.splitext(i)[1] == str('.'+(ext))]

# filesname = OrderedDict()
# filesname['inpath'] = findFile(dirPath, 'shp')[random.randint(0, len(findFile(dirPath, 'shp'))-1)]
# filesname['outputDirs'] = outDirs
# filesname['fileNames'] = None
# filesname['targetEPSG'] = None
# filesname['xycoords'] = True
# filesname['removeIdentical'] = True
# filesname['attribute'] = ['Product', 'Distance_f', 'Track_deg_', 'Swth_Wdth_', 'Y_Offset_f', 'Rt_Apd_Ct_', 'Date']
# filesname['outpath'] = geoprocessing.remove_identical_point(filesname['inpath'], *filesname['attribute'], **filesname)

files = OrderedDict(
    [('inpath', '/home/raihan/2018/Z3 AG_Homeplace_Green House_2018_DKC67-44_1.shp'),
      ('outputDirs', '/home/raihan/ExportData'),
      ('fileNames', None),
      ('targetEPSG', 3857),
      ('xycoords', True),
      ('removeIdentical', True),
      ('attribute', ['Rt_Apd_Ct_', 'Date', 'Time', 'Field']),
      ('outpath', '/home/raihan/ExportData/Z3 AG_Homeplace_Green House_2018_DKC67-44_1.shp')]
    )

array, profile = geoprocessing.structured_numpy_array(files['outpath'])

s = np.array([array['Distance_f'], array['Track_deg_']]).T


