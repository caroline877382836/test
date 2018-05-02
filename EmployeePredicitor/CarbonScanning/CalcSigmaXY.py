import struct
import numpy as np
from ReadDose import ReadCSDose
from GaussianErrorFit import GaussianERFFit

class CalcSigmaX_Y():
    
    def __init__(self,ref_dose_path,new_dose_path,grid_size):
        self.ref_dose_path = ref_dose_path
        self.new_dose_path = new_dose_path
        self.gridSize = grid_size
       
    def Get_Dose3D(self): 
        path_benchMark =  self.ref_dose_path
        path_proton = self.new_dose_path
        data_3DbenchMark = ReadCSDose(path_benchMark)
        data_3Dproton =  ReadCSDose(path_proton)
        return data_3DbenchMark,data_3Dproton
         
    def Get_sigmas_of_total_Layers(self,BeamDirection):                
        data_3DbenchMark, data_3Dproton = self.Get_Dose3D()           
        lay_cnt = data_3DbenchMark.Get_layCnt(BeamDirection)
        benchMarch_sigma = []  # [sigmaX,sigmaY]
        protonCS_sigma = []
        del_sigma = []
        for lay_idx in range(0, lay_cnt, 1):  # loop for all the layers  
            benchMarch_sigma_temp, protonCS_sigma_temp, del_sigma_temp = self.Get_sigmas_of_single_Layer(data_3DbenchMark, 
                                                                                       data_3Dproton, 
                                                                                       lay_idx, 
                                                                                       BeamDirection)              
            benchMarch_sigma.append(benchMarch_sigma_temp)
            protonCS_sigma.append(protonCS_sigma_temp)
            del_sigma.append(del_sigma_temp)            
        return  benchMarch_sigma, protonCS_sigma, del_sigma
    
    def Get_sigmas_of_single_Layer(self,data_3DbenchMark, data_3Dproton, lay_idx, BeamDirection):        
        grid = self.gridSize    
        data_2DbenchMark = data_3DbenchMark.Get_Dose2D_with_LayerIdx(lay_idx, BeamDirection)
        data_2Dproton = data_3Dproton.Get_Dose2D_with_LayerIdx(lay_idx, BeamDirection)
                
        axx_benchMarch = GaussianERFFit(data_2DbenchMark, grid)
        axx_proton = GaussianERFFit(data_2Dproton, grid)
                 
        try:                    
            if hasattr(axx_benchMarch, 'sigmaX'):
                benchMarch_sigma = [axx_benchMarch.sigmaX, axx_benchMarch.sigmaY]
            else:
                benchMarch_sigma = [0, 0]  # zero dose case: assign to sigmaX and sigmaY to 0 currently
        except:
            pass
                
        try:
            if hasattr(axx_proton, 'sigmaX'):
                protonCS_sigma = [axx_proton.sigmaX, axx_proton.sigmaY]
            else:
                protonCS_sigma = [0, 0]  # zero dose case: assign to sigmaX and sigmaY to 0 currently
        except:
            pass                
        del_sigma = [benchMarch_sigma[0] - protonCS_sigma[0], benchMarch_sigma[1] - protonCS_sigma[1]]
        return benchMarch_sigma,protonCS_sigma,del_sigma
    
    # loop for all the layers,[brag_peak_idx - half_layer_cnt,brag_peak_idx + half_layer_cnt]
    def Get_sigmas_of_multi_Layers(self,BeamDirection,brag_peak_idx,multi_layer_cnt):    
        half_layer_cnt = int(np.math.ceil(multi_layer_cnt/2))      
        data_3DbenchMark, data_3Dproton = self.Get_Dose3D()
        benchMarch_sigma = []  # [sigmaX,sigmaY]
        protonCS_sigma = []
        del_sigma = []
        for lay_idx in range(max(0,brag_peak_idx - half_layer_cnt), brag_peak_idx + half_layer_cnt, 1):
            benchMarch_sigma_temp, protonCS_sigma_temp, del_sigma_temp = self.Get_sigmas_of_single_Layer(data_3DbenchMark, 
                                                                                       data_3Dproton, 
                                                                                       lay_idx, 
                                                                                       BeamDirection)              
            benchMarch_sigma.append(benchMarch_sigma_temp)
            protonCS_sigma.append(protonCS_sigma_temp)
            del_sigma.append(del_sigma_temp)            
        return  benchMarch_sigma, protonCS_sigma, del_sigma
    
    # for special case: the brag_peak_idx + half_layer_cnt > len_IDD_CS
    def Get_sigmas_of_multi_Layers_avoid_transgression(self,BeamDirection,brag_peak_idx,len_IDD_CS,multi_layer_cnt):    
        half_layer_cnt = int(np.math.ceil(multi_layer_cnt/2))      
        data_3DbenchMark, data_3Dproton = self.Get_Dose3D()
        benchMarch_sigma = []  # [sigmaX,sigmaY]
        protonCS_sigma = []
        del_sigma = []
        for lay_idx in range(max(0,brag_peak_idx - half_layer_cnt), min(brag_peak_idx + half_layer_cnt,len_IDD_CS), 1):
            benchMarch_sigma_temp, protonCS_sigma_temp, del_sigma_temp = self.Get_sigmas_of_single_Layer(data_3DbenchMark, 
                                                                                       data_3Dproton, 
                                                                                       lay_idx, 
                                                                                       BeamDirection)              
            benchMarch_sigma.append(benchMarch_sigma_temp)
            protonCS_sigma.append(protonCS_sigma_temp)
            del_sigma.append(del_sigma_temp)            
        return  benchMarch_sigma, protonCS_sigma, del_sigma
    
    def Calc_sigmas_statistical_probability(self,del_sigma):
        cnt = 0
        for idx in range(0,del_sigma.size,1):
            for i , j in del_sigma[idx]:
                if abs(i) >= 0.00001 | abs(j) >= 0.00001:
                    cnt += 1
        return cnt, cnt/del_sigma.size

    def Get_sigmas_of_80Perc_layers(self,BeamDirection,brag_peak_idx,idd):
        perc_benchMarch_sigma = []
        perc_test_sigma = []
        perc_del_sigma = []       
        benchMarch_sigma, protontest_sigma, del_sigma = self.Get_sigmas_of_total_Layers(BeamDirection)
        lay_cnt = len(benchMarch_sigma)
        # find idx: amp = max(idd) * 0.8
        idx_idd_pre,idx_idd_aft = self.find_idd_80perc(idd,brag_peak_idx)
        perc_bef_idx = max(2,idx_idd_pre)
        perc_aft_idx = min(lay_cnt-2, idx_idd_aft)
        # the first two layers
        perc_benchMarch_sigma.append(benchMarch_sigma[0])
        perc_benchMarch_sigma.append(benchMarch_sigma[1])
        perc_test_sigma.append(protontest_sigma[0])
        perc_test_sigma.append(protontest_sigma[1])
        perc_del_sigma.append(del_sigma[0])
        perc_del_sigma.append(del_sigma[1])
        # layers:   0.8*brag_peak_idx ---  1.2* brag_peak_idx
        if perc_bef_idx < perc_aft_idx:
            for i in range(perc_bef_idx,perc_aft_idx+1):            
                perc_benchMarch_sigma.append(benchMarch_sigma[i])
                perc_test_sigma.append(protontest_sigma[i])
                perc_del_sigma.append(del_sigma[i])
              
        # the last two layers
        perc_benchMarch_sigma.append(benchMarch_sigma[lay_cnt-2])
        perc_benchMarch_sigma.append(benchMarch_sigma[lay_cnt-1])
        perc_test_sigma.append(protontest_sigma[lay_cnt-2])
        perc_test_sigma.append(protontest_sigma[lay_cnt-1])
        perc_del_sigma.append(del_sigma[lay_cnt-2])
        perc_del_sigma.append(del_sigma[lay_cnt-1])

        return perc_benchMarch_sigma, perc_test_sigma, perc_del_sigma, del_sigma

    def find_idd_80perc(self,idd,bragpeak):
        perc80_amp_idd = 0.8 * idd[bragpeak]
        idx_idd_pre = 0
        idx_idd_aft = 0
        amp_idd_pre = 0.0
        amp_idd_aft = 0.0
        for i in range(max(0,bragpeak - 5),min(bragpeak +5,len(idd))):
            amp_idd_aft = idd[i]
            if amp_idd_pre < perc80_amp_idd and perc80_amp_idd < amp_idd_aft:
                idx_idd_pre = max(0,i - 1 )               
            elif amp_idd_pre > perc80_amp_idd and perc80_amp_idd > amp_idd_aft:
                idx_idd_aft = min(i,len(idd)-1)
            amp_idd_pre = idd[i]                       
        return idx_idd_pre,idx_idd_aft








                    
                   
