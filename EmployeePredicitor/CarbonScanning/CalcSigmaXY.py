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
        del_sigma = [axx_benchMarch.sigmaX - axx_proton.sigmaX, axx_benchMarch.sigmaY - axx_proton.sigmaY]
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
            