# -*- coding: utf-8 -*-

import os
from geoanalytics.reporting.assets.baseprocess import Basemap

rx_data = '/home/kali/LearnPDF/rx_data'
rxfiles = [os.path.join(rx_data, i) for i in os.listdir(rx_data) if os.path.basename(i).split('.', 1)[1] == 'shp']

creds_path = "../../credentials.json"
outpaths = '/home/kali/spark_out'
root_path = os.getcwd()
data_path = {}
for i in rxfiles:
    print(f" -- Reading File: {i}")
    polys = Basemap.Extent(i, creds_path, width_increase = 40, height_increase = 0)
    os.chdir(f"{os.getcwd()}/assets")
    rxmap = Basemap.Rxmap(polys, 'TgtRat_L', outpaths)
    os.chdir(root_path)
    data_path.update(rxmap)
# import json

# file = json.load(open('test_filepath.json'))

# from fpdf import Template


