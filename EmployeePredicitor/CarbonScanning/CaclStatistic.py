# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:34:46 2018
@author: CNXuaCar
This doc is used to calculate the statistic results
"""
import struct
import numpy as np
from ReadDose import ReadCSDose
from GaussianErrorFit import GaussianERFFit
import matplotlib.pyplot as plt
import logging
logger = logging.getLogger(__name__)

class CalcStatistic():
    
    def __init__(self,ref_values,new_values,acceptance_error):
        self.ref_values = ref_values
        self.new_values = new_values
        self.acceptance_error = acceptance_error       
    
    def calc_IDD_statistic_1(self,min_IDD_acceptPerc):
        delta_idd_err_cnt = 0
        total_valid_cnt = 0
        max_diff_norm_val = 0           
        new_value = self.new_values
        ref_value = self.ref_values
        accep_err = self.acceptance_error 
        max_refIDD = max(ref_value)
        min_acepDose = max_refIDD * min_IDD_acceptPerc  # less this value,will not considered
        try:
            for i in range(0,len(new_value),1):
                if(ref_value[i] > 0.00001 or new_value[i] > 0.00001):
                    total_valid_cnt += 1
                    if ref_value[i] > min_acepDose or new_value[i] > min_acepDose:
                        if ref_value[i] > min_acepDose: 
                            temp = ref_value[i]
                        elif new_value[i] > min_acepDose:
                            temp = new_value[i]
                        tolerance = abs(new_value[i] - ref_value[i]) / temp
                    else:
                        tolerance = abs(new_value[i] - ref_value[i])
                    if tolerance > accep_err:
                        delta_idd_err_cnt += 1
                    if tolerance > max_diff_norm_val:
                        max_diff_norm_val = tolerance                        
            return delta_idd_err_cnt, total_valid_cnt,100 *max_diff_norm_val         
        except Exception,e:
            logger.error('calculate IDD statistic pentage failed: Reason is: {}'.format(str(e)), exc_info=True)
            raise e    

    def calc_IDD_statistic(self,min_IDD_acceptPerc):
        delta_idd_err_cnt = 0
        total_valid_cnt = 0
        max_diff_norm_val = 0           
        new_value = self.new_values
        ref_value = self.ref_values
        accep_err = self.acceptance_error 
        max_refIDD = max(ref_value)
        min_acepDose = max_refIDD * min_IDD_acceptPerc  # less this value, will use absolute diff
        try:
            for i in range(0,len(new_value),1):
                total_valid_cnt += 1
                if(ref_value[i] > min_acepDose):                   
                    tolerance = abs(new_value[i] - ref_value[i]) / ref_value[i]
                else:
                    tolerance = abs(new_value[i] - ref_value[i])
                if tolerance > accep_err:
                    delta_idd_err_cnt += 1
                if tolerance > max_diff_norm_val:
                    max_diff_norm_val = tolerance                        
            return delta_idd_err_cnt, total_valid_cnt, 100 * max_diff_norm_val         
        except Exception,e:
            logger.error('calculate IDD statistic pentage failed: Reason is: {}'.format(str(e)), exc_info=True)
            raise e 
    
    # accep_err : 0.001
    # delta_err_cnt: > 0.001
    # total_valid_cnt : bigger than max_refDose * mini_acceptPerc
    # max_refDose : max(ref_value)
    # max_diff_norm_val : max(tolerance)
    def calc_Dose_statistic(self,mini_acceptPerc):
        delta_err_cnt = 0
        max_diff_norm_val = 0
        total_valid_cnt = 0
        try:
            new_value = self.new_values.flatten()
            ref_value = self.ref_values.flatten()
            accep_err = self.acceptance_error
            max_refDose = max(ref_value)
            min_acepDose = max_refDose * mini_acceptPerc  # less this value,will not considered
            for i in range(0,len(new_value),1):
                total_valid_cnt += 1
                if(ref_value[i] > min_acepDose):    
                    tolerance = abs(new_value[i] - ref_value[i]) / ref_value[i]
                else:
                    tolerance = abs(new_value[i] - ref_value[i])
                if tolerance > accep_err:
                    delta_err_cnt += 1
                if tolerance > max_diff_norm_val:
                    max_diff_norm_val = tolerance                        
            return delta_err_cnt, total_valid_cnt,max_refDose,100 * max_diff_norm_val 
        except Exception,e:
            logger.error('calculate Dose statistic percentage failed: Reason is: {}'.format(str(e)), exc_info=True)
            raise e

    def calc_IDD_polyfit_intersection_point(self,idd,bragPeak,path):
        y_befBragPeak = []
        x_befBragPeak = []
        y_aftBragPeak = []
        x_aftBragPeak = []
        z_befBragPeak = np.array([])
        z_aftBragPeak = np.array([])
        idd_ref = idd
        # linnear fit before bragPeak
        try:
            for idx in range(max(0,bragPeak - 2),bragPeak + 1, 1):
                y_befBragPeak.append(idd_ref[idx])
                x_befBragPeak.append(idx) 
            if len(y_befBragPeak) >= 2 and len(x_befBragPeak) >= 2 :    # make sure at least 2 points          
                z_befBragPeak = np.polyfit(x_befBragPeak, y_befBragPeak, 1)
                p_befBragPeak = np.poly1d(z_befBragPeak)
            
            # linnear fit after bragPeak
            for idx in range(bragPeak, min(len(idd_ref)-1,bragPeak + 3),1):             
                y_aftBragPeak.append(idd_ref[idx])
                x_aftBragPeak.append(idx)
            if len(x_aftBragPeak) >= 2 and len(y_aftBragPeak) >= 2 :  
                z_aftBragPeak = np.polyfit(x_aftBragPeak, y_aftBragPeak, 1)            
                p_aftBragPeak = np.poly1d(z_aftBragPeak)
            # test 
            if (len(z_befBragPeak)== 2):
                if (len(z_aftBragPeak) == 2):
                    p_b = []
                    p_a = []
                    for i in range(0,len(idd_ref),1):
                        p_b.append(p_befBragPeak(i))
                        p_a.append(p_aftBragPeak(i)) 
                    self.plot_idd_3(p_b,p_a,idd_ref,path)

                    # get intersection point
                    p1 = np.array( [bragPeak - 1,p_befBragPeak(bragPeak - 1)] )
                    p2 = np.array( [bragPeak - 2,p_befBragPeak(bragPeak - 2)] )

                    p3 = np.array( [bragPeak + 1,p_aftBragPeak(bragPeak + 1)] )
                    p4 = np.array( [bragPeak + 2,p_aftBragPeak(bragPeak + 2)] )
                    intersection_point = self.seg_intersect( p1,p2, p3,p4)
                    return intersection_point[0],intersection_point[1]
            else:
                logger.info('Check whether the idx of bragPeak is zero OR the last ')
                return 0,0
        except Exception, e:
            logger.error('Linear fit IDD failed: Reason is: {}'.format(str(e)), exc_info=True)
            logger.info('Check whether the idx of bragPeak is zero OR the last ')
            raise e

    def perp(self,a) :
        b = np.empty_like(a)
        b[0] = -a[1]
        b[1] = a[0]
        return b

    # line segment a given by endpoints a1, a2
    # line segment b given by endpoints b1, b2
    # return 
    def seg_intersect(self,a1,a2, b1,b2):
        da = a2-a1
        db = b2-b1
        dp = a1-b1
        dap = self.perp(da)
        denom = np.dot( dap, db)
        num = np.dot( dap, dp )
        return (num / denom.astype(float))*db + b1  

    def plot_idd_3(self,idd_CS,idd_Upsala,idd,path): 
        plt.figure()
        plt.plot(idd_CS,'r--', label='linear fit Before IDD brag peak')
        plt.plot(idd_Upsala,'g--', label='linear fit After IDD brag peak') 
        plt.plot(idd,'b--', label='IDD profile') 
        #plt.plot(idd_CS, 'bo',label = "IDD_CS",idd_Upsala,'g^',label = "IDD_Uppsala")  # 'r--','bs','g^': red dashes, blue squares and green triangles
        plt.legend(loc='best', numpoints=1, handlelength=1)   
        #plt.show()  #block function
        plt.savefig(path)
        plt.close() 
# new_value = [delta_sigma_X], ref_value = [delta_sigma_Y]
    def calc_delta_sigma_statistic(self,min_delta_sigma_acceptPerc):  
        delta_idd_err_cnt = 0
        total_valid_cnt = 0 
        max_diff_norm_val = 0
        new_value = self.new_values
        ref_value = self.ref_values
        accep_err = self.acceptance_error
        max_refDose = max(ref_value)
        min_acepDose = max_refDose * min_delta_sigma_acceptPerc  # less this value,will not considered 
        try:
            for i in range(0,len(new_value),1):
                total_valid_cnt += 1
                if(ref_value[i] > min_acepDose):                   
                    tolerance = abs(new_value[i] - ref_value[i]) / ref_value[i]
                else:
                    tolerance = abs(new_value[i] - ref_value[i])
                if tolerance > accep_err:
                    delta_idd_err_cnt += 1
                if tolerance > max_diff_norm_val:
                    max_diff_norm_val = tolerance
            if not total_valid_cnt == 0:
                temp = round(100*(float(delta_idd_err_cnt)/float(total_valid_cnt)),2)                
            else:
                temp = 0.0
            return delta_idd_err_cnt, total_valid_cnt, temp, 100 * max_diff_norm_val
        except Exception,e:
            logger.error('calculate Dose statistic percentage failed: Reason is: {}'.format(str(e)), exc_info=True)
            raise e
    