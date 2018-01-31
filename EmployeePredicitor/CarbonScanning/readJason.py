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
        
    # read json file   
    def read(self):
        file_path = os.path.join(self.rootdir,self.jason_name)
        with open(file_path) as f:
            self.data = json.load(f,encoding="UTF-8")
            self.dirs = self.data["dir_configuration"] 
            self.patient_cases_dict =  self.data["patient_cases"]
             
    def parse_dir_configuration(self): 
        confg_dir = self.dirs
        if (len(confg_dir.keys()) > 0):         
            self._patient_temp_dir = confg_dir["patient_temp_dir"]
            self._CS_exe_root = confg_dir["CS_exe_root"]
            self._Upsala_exe_root = confg_dir["Upsala_exe_root"]
            self._Machine_temp_dir = confg_dir["Machine_temp_dir"]
            self._ED_temp_dir = confg_dir["ED_temp_dir"]
            self._output_path = confg_dir["out_put_dir"]   
 
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
        self._CS_exe_name = values["CS_exe_name"]
        self._Upsala_exe_name = values["Upsala_exe_name"]
        self._ED_file_name = values["ED_file_name"]
        self._Machine_file_name = values["Machine_file_name"]
        self._BeamDirectons = values["Beam Directons"]
        self._patient_change_condition = values["patient_change_condition"]      
          
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
# output_dir = "D:\TestData\practice\out_put\patientCase1" (folder patientCase1 contains all the files in the folder1_dir/folder2_dir)

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
            os.mkdir(output_dir)
            print 'Directory created at: ' + output_dir
            #loop through all files in the directory
        for f in os.listdir(fl1_dir): 
            #compute current (old) & new file locations
            oldLoc = fl1_dir + '\\' + f
            newLoc = output_dir + '\\' + f           
            if not os.path.isfile(newLoc):                
                try:
                    shutil.copy2(oldLoc, newLoc)
                    print 'File ' + f + ' copied.'
                except IOError:
                    print 'file "' + f + '" already exists'
        for f in os.listdir(fl2_dir): 
            #compute current (old) & new file locations
            oldLoc = fl2_dir + '\\' + f
            newLoc = output_dir + '\\' + f           
            if not os.path.isfile(newLoc):                
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