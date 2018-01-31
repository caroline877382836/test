import os
import readJason
from readJason import ReadJason
from readJason import ParseSinglePatientConfig
from readJason import MergeFilesFromTwoFolder
  
class InitParameters():  
    
    def __init__(self,json_config_dir,jason_config_name):
        self.json_config_dir = json_config_dir
        self.jason_config_name = jason_config_name
        self.patient_path_CS = None
        self.exe_path_CS = None    
        self.machine_path_CS = None
        self.ED_path_CS = None
        self.output_path = None
        
        self.patient_path_Upsala = None
        self.exe_path_Upsala = None  
        self.machine_path_Upsala = None
        self.ED_path_Upsala = None
       
        ###  this used to ininit only single specified patient with condition patient_case_name, 
        ###  which got from Json config, as "patient_case_1"
    def init_single_patient_paras(self,patient_case_name):
        
        data = ReadJason(self.json_config_dir,self.jason_config_name)
        if not data.patient_cases_dict.has_key(patient_case_name):
            print 'key with patient_case_name: ' + patient_case_name + ' not exits in jason file.'
        patients_lst_item  = [patient_case_name,data.patient_cases_dict.get(patient_case_name)] 
        patient_initi_cong = ParseSinglePatientConfig(patients_lst_item)   
        ### merge patient data and ED data
        patient_path_CS = MergeFilesFromTwoFolder(os.path.join(data._patient_temp_dir, patient_initi_cong.patient_tempfile_name),
                                             os.path.join(data._ED_temp_dir, patient_initi_cong._ED_file_name),
                                             os.path.join(data._output_path,patient_case_name) +'\\' + 'CS')
        self.patient_path_CS = patient_path_CS.OutPut_dir +'\\'
        self.exe_path_CS = os.path.join(os.path.join(data._CS_exe_root, patient_initi_cong._CS_exe_name),"ProtonScanning.exe")                                        
        self.machine_path_CS = os.path.join(data._Machine_temp_dir, patient_initi_cong._Machine_file_name) + '\\'   
        self.ED_path_CS = os.path.join(data._ED_temp_dir, patient_initi_cong._ED_file_name)
        
        #### TODO: modify to Upsala patient data: currently use same as CS data
        patient_path_Upsala = MergeFilesFromTwoFolder(os.path.join(data._patient_temp_dir, patient_initi_cong.patient_tempfile_name),
                                             os.path.join(data._ED_temp_dir, patient_initi_cong._ED_file_name),
                                             os.path.join(data._output_path,patient_case_name) +'\\' + 'Upsala') 
        self.patient_path_Upsala = self.patient_path_CS   
        self.exe_path_Upsala = self.exe_path_CS ##TODO: change to upsala exe     
        self.machine_path_Upsala = self.machine_path_CS  
        self.ED_path_Upsala =  self.ED_path_CS
        self.output_path = data._output_path