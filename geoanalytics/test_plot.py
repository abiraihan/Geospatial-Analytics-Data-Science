#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 18 21:40:24 2023

@author: kali
"""
import os
import numpy as np

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


