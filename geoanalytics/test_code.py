# -*- coding: utf-8 -*-

# from base.base import geoprocessing as gpr
# from core.core import cores
# import os
# os.chdir(os.path.abspath(os.getcwd()))
# data_dirs = "/home/kali/MyJD_Data/doc"

# filepaths = [os.path.join(data_dirs, i) for i in os.listdir(data_dirs) if os.path.basename(i).split('.', 1)[1] == 'shp'][0]

# planting = cores.remove_identical(filepaths, xycoords = True)
# pointdata = gpr.structured_numpy_array(filepaths)
# import os

# from reporting.assets.baseprocess import Basemap

# rx_data = '/home/kali/LearnPDF/rx_data'
# rxfiles = [os.path.join(rx_data, i) for i in os.listdir(rx_data) if os.path.basename(i).split('.', 1)[1] == 'shp']

# creds_path = "/home/kali/geolytics/Geospatial-Analytics-Data-Science/credentials.json"
# outpaths = '/home/kali/spark_out'

# data_path = {}
# for i in rxfiles:
#     polys = Basemap.Extent(i, creds_path, width_increase = 3, height_increase = 1)
#     rxmap = Basemap.Rxmap(polys, 'Target_Rat', outpaths)
#     data_path.update(rxmap)

from fpdf import FPDF

test_data  = {'double': {'filepath': '/home/kali/LearnPDF/rx_data/double.shp',
  'legend': '/home/kali/spark_out/double_legend.png',
  'map': '/home/kali/spark_out/double.png'},
 'single': {'filepath': '/home/kali/LearnPDF/rx_data/single.shp',
  'legend': '/home/kali/spark_out/single_legend.png',
  'map': '/home/kali/spark_out/single.png'},
 'third': {'filepath': '/home/kali/LearnPDF/rx_data/third.shp',
  'legend': '/home/kali/spark_out/third_legend.png',
  'map': '/home/kali/spark_out/third.png'}}

import geopandas as gpd

data = gpd.read_file(test_data['double']['filepath'])
# pdf = FPDF(unit = 'mm', format = 'Letter')
# pdf.add_page(orientation = 'P')
# pdf.add_font('Avenir', '', '/home/kali/LearnPDF/font_family/Avenir LT Std/Avenir LT Std 35 Light/Avenir-LT-Std-35-Light.ttf', uni=True)
# pdf.set_font('Avenir', '', 13)
# # pdf.set_font(family = 'Avenir LT std', style = 'B', size = 35)
# pdf.cell(10, 10, 'This is my first pdf In Front of House')
# wid = pdf.get_string_width('This is my first pdf In Front of House') + 10 + 10
# pdf.line(wid, 10, wid, 20)
# pdf.image('/home/kali/LearnPDF/Wilkins_Hoffman_Hoffman_NO Year_NO Product_1_poly.png',
#           x = 15, y = 70, w = 180, h = 120, type = 'PNG')
# pdf.output('/home/kali/LearnPDF/test.pdf', 'F')

