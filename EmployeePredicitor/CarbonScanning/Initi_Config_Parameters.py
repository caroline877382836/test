# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:34:46 2018
@author: CNXuaCar
This doc is used to get the initial config paras from jason file
"""
import os
import readJason
from readJason import ReadJason
from readJason import ParseSinglePatientConfig
from readJason import MergeFilesFromTwoFolder
  
class InitParameters():  
    
    def __init__(self,json_config_dir,jason_config_name):        
        self.json_config_dir = json_config_dir
        self.jason_config_name = jason_config_name
        self.Jason_data = ReadJason(self.json_config_dir,self.jason_config_name)
        self.patient_path_test = None
        self.exe_path_test = None    
        self.machine_path_test = None
        self.ED_path_test = None
        self.output_path = None
        self.patient_initi_cong_lst = None
        
        self.patient_path_BenchMark = None
        self.exe_path_BenchMark = None  
        self.machine_path_BenchMark = None
        self.ED_path_BenchMark = None
       
        ###  this used to ininit only single specified patient with condition patient_case_name, 
        ###  which got from Json config, as "patient_case_1"
    def init_single_patient_paras(self,patient_case_name):        
        data = self.Jason_data
        if not data.patient_cases_dict.has_key(patient_case_name):
            print 'key with patient_case_name: ' + patient_case_name + ' not exits in jason file.'
        patients_lst_item  = [patient_case_name,data.patient_cases_dict.get(patient_case_name)] 
        patient_initi_cong = ParseSinglePatientConfig(patients_lst_item)
        self.patient_initi_cong_lst = patient_initi_cong   
        ### merge patient data and ED data
        patient_path_test = MergeFilesFromTwoFolder(os.path.join(data._patient_temp_dir, patient_initi_cong.patient_tempfile_name),
                                             os.path.join(data._ED_temp_dir, patient_initi_cong._ED_file_name),
                                             os.path.join(data._output_path,patient_case_name) +'\\' + 'test')
        self.patient_path_test = patient_path_test.OutPut_dir +'\\'
        self.exe_path_test = os.path.join(os.path.join(data._test_exe_root, patient_initi_cong._test_exe_name),"ProtonScanning.exe")                                        
        self.machine_path_test = os.path.join(data._Machine_temp_dir, patient_initi_cong._Machine_file_name) + '\\'   
        self.ED_path_test = os.path.join(data._ED_temp_dir, patient_initi_cong._ED_file_name)
        self.patient_change_condition_lst = patient_initi_cong.patient_change_conditions_lst
        
        patient_path_benchMark = MergeFilesFromTwoFolder(os.path.join(data._patient_temp_dir, patient_initi_cong.patient_tempfile_name),
                                             os.path.join(data._ED_temp_dir, patient_initi_cong._ED_file_name),
                                             os.path.join(data._output_path,patient_case_name) +'\\' + 'benchMark') 
        self.patient_path_benchMark = patient_path_benchMark.OutPut_dir +'\\'  
        self.exe_path_benchMark = os.path.join(os.path.join(data._benchMark_exe_root, patient_initi_cong._BenchMark_exe_name) ,"ProtonPencilBeamExecutable.exe")
        #self.machine_path_benchMark = os.path.join(data._Machine_temp_dir, patient_initi_cong._Machine_file_name) + '\\'   
        #self.ED_path_benchMark =  os.path.join(data._ED_temp_dir, patient_initi_cong._ED_file_name)
        self.output_path = data._output_path