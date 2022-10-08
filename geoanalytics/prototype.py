#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 04:42:24 2022

@author: araihan
"""
import matplotlib.pyplot as plt
import numpy as np
# import os
# os.chdir(os.path.abspath(os.getcwd()))
from sklearn.neighbors import KNeighborsRegressor
def KNeighborArray(multiArray):
    
    nrow, ncol = multiArray.shape
    frow, fcol = np.where(np.isfinite(multiArray))
    
    train_X, train_y = [[frow[i], fcol[i]] for i in range(len(frow))], multiArray[frow, fcol]
    
    knn = KNeighborsRegressor(n_neighbors= 5, weights='distance', algorithm='ball_tree', p=2)
    knn.fit(train_X, train_y)
    
    r2 = knn.score(train_X, train_y)
    print("R2- {}".format(r2))
    X_pred = [[r, c] for r in range(int(nrow)) for c in range(int(ncol))]
    
    y_pred = knn.predict(X_pred)
    karray = np.zeros((nrow, ncol))
    i=0
    for r in range(int(nrow)):
        for c in range(int(ncol)):
            karray[r, c] = y_pred[i]
            i += 1
    return karray
# arrays = np.array([1, 2, np.nan, 4, 5, 6, np.nan, 8, 9, np.nan, np.nan, 12, 13, np.nan, 15, np.nan, 17, 18, 19, 20])


# xd = np.flipud(np.reshape(arrays, (4, -1)).T)


# nx = KNeighborArray(xd)
# print(arrays)
# print(xd)
# print(nx)

# cd = np.fliplr(nx.T).reshape([len(arrays), 1]).flatten()

# print(cd)

# dtypes= [('geometry', '|O'),
#  ('R4_m___mean', '<f8'),
#  ('rWTC__mean', '<f8'),
#  ('D2I___mean', '<f8'),
#  ('Yld_o_r_mean', '<f8')]
a = {'Field': ('Fiel_major', '<U254'), 'Dataset': ('Datae_major', '<U254'), 'Product': ('Prodc_major', '<U254'), 'Obj__Id': ('Obj_I_mean', '<f8'), 'Sample_ID': ('SampeI_major', '<U254'), 'Soil_pH__1': ('Soilp_1_mean', '<f8'), 'Soil_BpH__': ('SoilBH__mean', '<f8'), 'P_lb_ac_': ('P_lba__mean', '<f8'), 'K_lb_ac_': ('K_lba__mean', '<f8'), 'Mg_lb_ac_': ('Mg_l_c_mean', '<f8'), 'Ca_lb_ac_': ('Ca_l_c_mean', '<f8'), 'S_lb_ac_': ('S_lba__mean', '<f8'), 'Zn_lb_ac_': ('Zn_l_c_mean', '<f8'), 'Mn_lb_ac_': ('Mn_l_c_mean', '<f8'), 'Cu_lb_ac_': ('Cu_l_c_mean', '<f8'), 'Soil_CEC_m': ('SoilCCm_mean', '<f8'), 'Soil___K__': ('Soil_K__mean', '<f8'), 'Soil___MG_': ('Soil_M__mean', '<f8'), 'Soil___CA_': ('Soil_C__mean', '<f8'), 'Soil___NA_': ('Soil_N__mean', '<f8'), 'H_Soil____': ('H_Sol___mean', '<f8'), 'Soil_OM___': ('SoilO___mean', '<f8'), 'Na_lb_ac_': ('Na_l_c_mean', '<f8'), 'Soil___H__': ('Soil_H__mean', '<f8'), 'Grower___N': ('Growr_N_majo', '<U254'), 'Farm___Nam': ('Farm_Nm_majo', '<U254'), 'Field___Na': ('Fiel__a_majo', '<U254'), 'Product___': ('Prodc___majo', '<U254'), 'Year___Nam': ('Year_Nm_majo', '<U254'), 'Year___Yea': ('Year_Ya_mean', '<f8')}


b = ('Fiel_major1', '<U254'), 'Datae_major1': ('Datae_major1', '<U254'), 'Prodc_major1': ('Prodc_major1', '<U254'), 'Obj_I_mean1': ('Obj_I_mean1', '<f8'), 'SampeI_major': ('SampeI_major', '<U254'), 'Soilp_1_mean': ('Soilp_1_mean', '<f8'), 'SoilBH__mean': ('SoilBH__mean', '<f8'), 'P_lba__mean': ('P_lba__mean', '<f8'), 'K_lba__mean': ('K_lba__mean', '<f8'), 'Mg_l_c_mean': ('Mg_l_c_mean', '<f8'), 'Ca_l_c_mean': ('Ca_l_c_mean', '<f8'), 'S_lba__mean': ('S_lba__mean', '<f8'), 'Zn_l_c_mean': ('Zn_l_c_mean', '<f8'), 'Mn_l_c_mean': ('Mn_l_c_mean', '<f8'), 'Cu_l_c_mean': ('Cu_l_c_mean', '<f8'), 'SoilCCm_mean': ('SoilCCm_mean', '<f8'), 'Soil_K__mean': ('Soil_K__mean', '<f8'), 'Soil_M__mean': ('Soil_M__mean', '<f8'), 'Soil_C__mean': ('Soil_C__mean', '<f8'), 'Soil_N__mean': ('Soil_N__mean', '<f8'), 'H_Sol___mean': ('H_Sol___mean', '<f8'), 'SoilO___mean': ('SoilO___mean', '<f8'), 'Na_l_c_mean': ('Na_l_c_mean', '<f8'), 'Soil_H__mean': ('Soil_H__mean', '<f8'), 'Growr_N_majo1': ('Growr_N_majo1', '<U254'), 'Farm_Nm_majo1': ('Farm_Nm_majo1', '<U254'), 'Fiel__a_majo1': ('Fiel__a_majo1', '<U254'), 'Prodc___majo1': ('Prodc___majo1', '<U254'), 'Year_Nm_majo1': ('Year_Nm_majo1', '<U254'), 'Year_Ya_mean1': ('Year_Ya_mean1', '<f8')}

