# -*- coding: utf-8 -*-

creds_path = "../../credentials.json"


# ==============Script==============Boundary==============Test===================
# import os
# from geoanalytics.reporting.assets.baseprocess import Basemap
# boundary_data = '/home/kali/WorkEasy/2022 Investor Report Data/organized_by_investor/Eden and Steven Romick Trust/boundary'
# files = [os.path.join(boundary_data, i) for i in os.listdir(boundary_data) if os.path.basename(i).split('.', 1)[1] == 'shp']
# outpaths = '/home/kali/spark_out'
# data_path = {}
# for i in files:
#     print(f" -- Reading File: {i}")
#     polys = Basemap.Extent(i, creds_path, width_increase = 5, height_increase = 5, padding = 5)
#     boundMap = Basemap.Boundary(polys, outpaths)
#     data_path.update(boundMap)
# =============================================================================

# ==============Script==============RxMaps==============Test===================
# import os
# from geoanalytics.reporting.assets.baseprocess import Basemap
# rx_data = '/home/kali/LearnPDF/rx_data'
# rxfiles = [os.path.join(rx_data, i) for i in os.listdir(rx_data) if os.path.basename(i).split('.', 1)[1] == 'shp'][0:2]
# outpaths = '/home/kali/spark_out'
# data_path = {}
# for i in rxfiles:
#     print(f" -- Reading File: {i}")
#     polys = Basemap.Extent(i, creds_path, width_increase = 40, height_increase = 0)
#     rxmap = Basemap.Rxmap(polys, outpaths, target_rate_attr='TgtRat_L')
#     data_path.update(rxmap)
# =============================================================================


# =========Script=========Planting====Variety====Map==============Test=========
# import os
# from geoanalytics.reporting.assets.baseprocess import Basemap
# plant_data = '/home/kali/Data/Corn_AsPlanted'
# files = [os.path.join(plant_data, i) for i in os.listdir(plant_data) if os.path.basename(i).split('.', 1)[1] == 'shp']
# outpaths = '/home/kali/spark_out'

# args = dict(
#     ratio = 0.6,
#     padding = 10,
#     target_attr = 'Product',
#     xaxis_length_attr = 'Swth_Wdth_', # Swath length
#     yaxis_length_attr = 'Distance_f', # Distance
#     rotation_attr = 'Track_deg_', #Rotation
#     attributes = ['Grower___N', 'Farm___Nam', 'Field___Na', 'Product___'],
#     data_type = 'Planting',
#     num_variety = 9,
#     font_name = 'Avenir LT Std 65 Medium Oblique',
#     plt_margin = 0.0,
#     font_size = 12,
#     font_style = 'oblique',
#     width = 2,
#     height = 0.16,
#     alpha = 1,
#     pad = 4,
#     font_length_limit = 11,
#     variety_font_size = 10,
#     auto_font_dicts = {'start': 9, 'stop': 30, 'interval': 5},
#     dpi = 300,
#     color = 'tab20',
#     transparent = True,
#     bbox_inches = 'tight',
#     pad_inches = 0.00,
#     image_border_width = 2,
#     image_border_color = 'black',
#     figsize = (10, 10),
#     frameon = False,
#     markerscale = 1.5,
#     markerfirst =  True,
#     alignment = 'left',
#     labelspacing = 0.4,
#     framealpha = 1,
#     handlelength = 0.3,
#     handleheight = 0.0,
#     borderaxespad = 0.1
#     )
# data_dict = {}
# for i in files:
#     print(f" -- Reading File: {i}")
#     swath_polys = Basemap.PlantingVarietySwaths(
#         i, creds_path,
#         *args['attributes'], **args)
#     plantVarietymap = Basemap.PlantingVarietyMap(swath_polys, outpaths, **args)
# =============================================================================


# =========Script=========Planting======Rate=====Map==============Test=========
import os
from geoanalytics.reporting.assets.baseprocess import Basemap

plant_data = '/home/kali/Data/Corn_AsPlanted'
filepath = [os.path.join(plant_data, i) for i in os.listdir(plant_data)
            if os.path.basename(i).split('.', 1)[1] == 'shp']

args = dict(
    ratio = 0.5,
    padding = 10,
    target_attr = 'Rt_Apd_Ct_',
    xaxis_length_attr = 'Swth_Wdth_', # Swath length
    yaxis_length_attr = 'Distance_f', # Distance
    rotation_attr = 'Track_deg_',
    font_name = 'Avenir LT Std 55 Oblique',
    image_border_width = 2,
    image_border_color = 'black',
    mapsWidth = 10,
    mapsHeight = 10,
    font_size = 14,
    font_style = 'oblique',
    plt_margin = 0.0,
    width = 12,
    bar_height = 0.6,
    cmaps_height = 0.2,
    alpha = 0.9,
    pad = 0,
    bar_label_box_width = 0.97,
    cmaps_label_box_width = 1.0,
    bar_color = 'lightgrey',
    cmaps_color = 'RdYlGn',
    dpi = 300,
    transparent = True,
    bbox_inches = 'tight',
    pad_inches = 0.00
    )

outpaths = '/home/kali/spark_out'

# data_dict = {}
for i in filepath:
    print(f" -- Reading File: {i}")
    extent_info = Basemap.PlantingRateSwaths(i, creds_path, **args)
    ds = Basemap.PlantingRateMap(extent_info, outpaths, **args)
# =============================================================================
