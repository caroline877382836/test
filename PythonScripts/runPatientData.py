#!usr/bin/python
if __name__ == '__main__':
    #main()
	#runPatientData.py must be locate in the upper directory of patient data
    import os, sys
    import subprocess
	
    patient_data = "D:/AutoTestData/Caro/PatientData"
    NIRS_BeamModel = "D:/AutoTestData/Caro/IDOSE_NewCSPBA/IDOSELocalFiles"
    NIRS_BeamModel_Mag2000 = "D:/AutoTestData/Caro/NewCS_PBAMag2000/IDOSELocalFiles"
    NIRS_BeamModel_HalfPixelSigma = "D:/AutoTestData/Caro/NewCS_PBSAHalfPixel/IDOSELocalFiles"
    NIRS_BeamModel_NewFixedPBSA = "D:/AutoTestData/Caro/IDOSE_NewFixedPBSA_Default/IDOSELocalFiles"
    NIRS_BeamModel_oldPBSAMag= "D:/AutoTestData/Caro/IDOSE_oldPBSA_mag/IDOSELocalFiles"
    NIRS_BeamModel_oldPBSA = "D:/AutoTestData/Caro/IDOSE_oldPBSA/IDOSELocalFiles"
	
    NIRS_BeamModel_NewCSHalfPixelMag = "D:/AutoTestData/Caro/NewCS_PBSAHalfPixelMag2000/IDOSELocalFiles"
	
    exe_1 = "D:/CarbonSpotCalD/x64/release/CarbonScanningNewCS.exe"
    exe_2 = "D:/CarbonSpotCalD/x64/release/CarbonScanningOldPBSA.exe"
    exe_3 = "D:/CarbonSpotCalD/x64/release/CarbonScanningUpdatedCS.exe"
    cwd = os.path.dirname(os.path.abspath(__file__))
	
    from time import gmtime, strftime
    current_time = strftime("%Y%m%d%H%M%S", gmtime())
    new_folder = os.path.join(cwd, current_time)
    os.mkdir(new_folder)
	
    def exec_copy(exe_path,com_path1,com_path2):
	    
		#excuate carbonscanning.exe
        subprocess.check_call([exe_path, com_path1+"/", com_path2+"/"])
		#copy data
        upper_dir = os.path.split(com_path2)
        model_name = os.path.basename(os.path.normpath(upper_dir[0]))
        exe_name = os.path.basename(os.path.normpath(exe_path)).replace('.','_')
        patient_name = os.path.basename(os.path.normpath(com_path1))
        dest_path = os.path.join(new_folder, patient_name+exe_name+model_name)
        os.mkdir(dest_path)
        from distutils.dir_util import copy_tree
        copy_tree(com_path1, dest_path)
        
	
    directories = [ x for x in os.listdir(patient_data) if os.path.isdir(os.path.join(patient_data,x))]
    for mydir in directories:
        com_path = os.path.join(patient_data, mydir)
        #exec_copy(exe_1,com_path,NIRS_BeamModel)
        #exec_copy(exe_1,com_path,NIRS_BeamModel_Mag2000)
        #exec_copy(exe_1,com_path,NIRS_BeamModel_HalfPixelSigma)
        #exec_copy(exe_1,com_path,NIRS_BeamModel_NewFixedPBSA)
        #exec_copy(exe_2,com_path,NIRS_BeamModel_oldPBSAMag)
		
        exec_copy(exe_1,com_path,NIRS_BeamModel_NewCSHalfPixelMag)