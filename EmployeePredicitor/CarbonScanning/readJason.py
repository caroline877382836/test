# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:34:46 2018
@author: CNXuaCar
This doc is used to read the jason data from the json file
Note: Here is hard coded, please do the corresponding change once you change jason file content
"""
import json
import os
import shutil

class ReadJason(object):

    def __init__(self, rootdir,jason_config_name):
        self.rootdir = rootdir
        self.jason_name = jason_config_name
        self.read()
        self.convert_patient_cases_dict_2_lst()
        self.parse_dir_configuration()
        self.parse_ini_paras_configuration()
        
    # read json file   
    def read(self):
        file_path = os.path.join(self.rootdir,self.jason_name)
        with open(file_path) as f:
            self.data = json.load(f,encoding="UTF-8")
            self.dirs = self.data["dir_configuration"] 
            self.ini_parameters = self.data["ini_paras_configuration"] 
            self.patient_cases_dict =  self.data["patient_cases"]

    def parse_ini_paras_configuration(self):
        init_paras = self.ini_parameters 
        if (len(init_paras.keys()) > 0):             
            self._ini_grid_size = init_paras["ini_grid_size"]
            self._err_delta_sigma_acceptance = init_paras["err_delta_sigma_acceptance"]
            self._min_delta_sigma_acceptPerc = init_paras["min_delta_sigma_acceptPerc"]    
            self._err_IDD_acceptance = init_paras["err_IDD_acceptance"]
            self._min_IDD_acceptPerc = init_paras["min_IDD_acceptPerc"]
            self._err_Dose1D_acceptance = init_paras["err_Dose1D_acceptance"]
            self._min_Dose1D_acceptPerc = init_paras["min_Dose1D_acceptPerc"]
            self._err_Dose3D_acceptance = init_paras["err_Dose3D_acceptance"]
            self._min_Dose3D_acceptPerc = init_paras["min_Dose3D_acceptPerc"]
            self._err_Dose2DGaussian_acceptance = init_paras["err_Dose2DGaussian_acceptance"]  
            self._min_Dose2DGaussian_acceptPerc = init_paras["min_Dose2DGaussian_acceptPerc"]          

    def parse_dir_configuration(self): 
        confg_dir = self.dirs
        if (len(confg_dir.keys()) > 0): 
            self._patient_temp_dir = confg_dir["patient_temp_dir"]
            self._test_exe_root = confg_dir["test_exe_root"]
            self._benchMark_exe_root = confg_dir["BenchMark_exe_root"]
            self._Machine_temp_dir = confg_dir["Machine_temp_dir"]
            self._ED_temp_dir = confg_dir["ED_temp_dir"]
            self._output_path = confg_dir["out_put_dir"]
            self._RequestCS2UppsalaConvertor_dir = confg_dir["RequestCS2UppsalaConvertor_dir"] + "\\" + 'RequestCS2UppsalaConvertor.exe'
            self._ResultUppsala2CSConvertor_dir = confg_dir["ResultUppsala2CSConvertor_dir"]  + "\\" + 'ResultUppsala2CSConvertor.exe'
            self._ModifyProtonRequestFile_dir = confg_dir["ModifyProtonRequestFile_dir"]  + "\\" + 'ModifyProtonRequestFile.exe'
 
    #convert dict to list         
    def convert_patient_cases_dict_2_lst(self):
        self._total_patientCase_counts = len(self.patient_cases_dict.keys())
        patients_config_lst = []
        for key, value in self.patient_cases_dict.iteritems():
            temp = [key, value]           
            patients_config_lst.append(temp)
        self._patients_config_lst = patients_config_lst
        return  patients_config_lst
            
## parse single patient initi config parameters from the item of patients_config_lst
class ParseSinglePatientConfig():
    def __init__(self, patients_config_lst_item):  
        self.patient_confi = patients_config_lst_item 
        self.parse_patients_config()
    
    def parse_patients_config(self):
        patient_cong = self.patient_confi
        values = patient_cong[1]                 
        self.patient_tempfile_name = values["patient_tempfile_name"]
        self._test_exe_name = values["test_exe_name"]
        self._BenchMark_exe_name = values["BenchMark_exe_name"]
        self._ED_file_name = values["ED_file_name"]
        self._Machine_file_name = values["Machine_file_name"]
        patient_change_condition = values["patient_change_condition"]
        self.patient_change_conditions_lst = []
        if (len(patient_change_condition.keys()) > 0):            
            for key , value in patient_change_condition.iteritems():
                temp = [key,value]
                self.patient_change_conditions_lst.append(temp)   
          
        Gammer_initi_config = values["Gammer_initi_configuration"]
        if (len(Gammer_initi_config.keys()) > 0):
            self._Gammer_delta_distance_in_mm = Gammer_initi_config["delta_distance_in_mm"]
            self._Gammer_delta_dose_percentage = Gammer_initi_config["delta_dose_percentage"]
            self._Gammer_ratio_voxels_within_tolerance = Gammer_initi_config["ratio_voxels_within_tolerance"]
            self._Gammer_search_radius = Gammer_initi_config["search_radius"]
                        
        dose_diff_config = values["dose_diff_configuration"]   
        if (len(Gammer_initi_config.keys()) > 0):
            self._dose_diff_config_maxdose_lower = dose_diff_config["maxdose_lower"]
            self._dose_diff_config_maxdose_upper = dose_diff_config["maxdose_upper"]
            self._dose_diff_config_normalize_to_sum = dose_diff_config["normalize_to_sum"]   

# folder1_dir = "D:\TestData\practice\EDTemp\ED_case1" (folder ED_case1 contains file: EffectiveDensity,ROIBitmap,ROITableFile)
# folder2_dir = "D:\TestData\practice\patientData\test_98_Proton"
#                (folder test_98_Proton contains file:CalculationStatus, CarbonScanning_log,ProtonRequest)
# output_dir = "D:\TestData\practice\out_put\patientCase1" (folder patientCase1 contains all the files both in the folder1_dir and folder2_dir)

class MergeFilesFromTwoFolder():
    def __init__(self,folder1_dir,folder2_dir,output_dir): 
        self.Folder1_dir = folder1_dir
        self.Folder2_dir = folder2_dir
        self.OutPut_dir = output_dir
        self.merge()
        
    def merge(self):
        fl1_dir = self.Folder1_dir
        fl2_dir = self.Folder2_dir
        output_dir = self.OutPut_dir 
        if not os.path.exists(output_dir):
            par_path = os.path.abspath(os.path.join(output_dir, os.pardir))
            if not os.path.exists(par_path):
                os.mkdir(par_path)               
            os.mkdir(output_dir)
            print 'Directory created at: ' + output_dir
            #loop through all files in the directory
        for f in os.listdir(fl1_dir): 
            #compute current (old) & new file locations
            oldLoc = fl1_dir + '\\' + f
            newLoc = output_dir + '\\' + f 
            if os.path.isfile(newLoc):
                os.remove(newLoc)          
            try:
                shutil.copy2(oldLoc, newLoc)
                print 'File ' + f + ' copied.'
            except IOError:
                print 'file "' + f + '" already exists'
        for f in os.listdir(fl2_dir): 
            #compute current (old) & new file locations
            oldLoc = fl2_dir + '\\' + f
            newLoc = output_dir + '\\' + f           
            if os.path.isfile(newLoc):
                os.remove(newLoc)                
            try:
                shutil.copy2(oldLoc, newLoc)
                print 'File ' + f + ' copied.'
            except IOError:
                print 'file "' + f + '" already exists'      
            
                   
        
#===============================================================================
# if __name__ == "__main__" :
#     folder1_dir = "D:\\TestData\\practice\\patientData\\test_98_Proton"
#     folder2_dir = "D:\\TestData\\practice\\EDTemp\\ED_case1"
#     out_put_dir = "D:\\TestData\\practice\\out_put\\test1"
#     MergeFilesFromTwoFolder(folder1_dir,folder2_dir,out_put_dir)
#     rootdir = 'D:\\TestData\\practice'     
#     jason_config_name = "init_config.json"
#     data = ReadJason(rootdir,jason_config_name)  
#     parse_patient = ParseSinglePatientConfig(data._patients_config_lst[0])    
#===============================================================================
