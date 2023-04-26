# -*- coding: utf-8 -*-

import fiona
import os
from shapely.ops import shape
class analytics(type):
    
    def __new__(cls, name, base, dicts):
        return super().__new__(cls, name, base, dicts)

class MyClass(metaclass=analytics):
    
    def read_file(files):
        geoms = []
        rt = fiona.open(files, 'r')
        for file in rt:
            geoms.append(shape(file['geometry']))
        rt.close()
        return geoms

        
rx_data = '/home/kali/LearnPDF/boundary'
rxfiles = [os.path.join(rx_data, i) for i in os.listdir(rx_data) if os.path.basename(i).split('.', 1)[1] == 'shp'][0]

x = MyClass.read_file(rxfiles)
