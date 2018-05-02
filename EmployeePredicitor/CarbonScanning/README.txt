For the first time to use this test tool, plese configure the environment according to the following steps.

NOTE: 
# this test tool depends on the another Elekta test tool "elektadoseverificationtool", please make sure to install it correctly.
  
# this tool depends on these .exe programs, please make sure to get the latest version: 
	ModifyProtonRequestFile.exe
	RequestCS2UppsalaConvertor.exe
	ResultUppsala2CSConvertor.exe
	
**************configure running environment*****************

1. Install Anaconda version 4.4.0 (based on Python 2.7 version):

	1.1 download from website:  https://repo.continuum.io/archive/
	1.2 install:  will be defaultly installed on your local directory :  C:\Users\"CNAccount"\AppData\Local\Continuum\Anaconda2 
	1.3 Update the Anaconda packages in the Anaconda installation:  	
		* use CMD to go to Anaconda2 directory:        * cd "C:\Users\"CNAccount"\AppData\Local\Continuum\Anaconda2 "
       		* go to "..\Anaconda2\Scripts" folder:         * cd Scripts
       		* Update packages:    * conda update --all 

2. Installation of dependencies --- all the packages are installed in the folder: ..\Anaconda2\Lib\site-packages\

       * use CMD to go to Anaconda2 directory:      * cd "C:\Users\"CNAccount"\AppData\Local\Continuum\Anaconda2"
       * go to "..\Anaconda2\Scripts" folder:       * cd Scripts
       * Install "elektadoseverificationtool":

		### install NotitiaReponoClient ###
		1. download an .egg file from website: http://seudvpypkg01.dev.elekta.com:8080/simple/notitiareponoclient/, 
						   like "NotitiaReponoClient-1.13.0.341a0-py2.7.egg"
		2. Note the location of NotitiaReponoClient egg file, 
						   like "C:\Users\"CNAccount"\Downloads\"
		3. Go to CMD window, input the following command,  
			* easy_install "C:\Users\"CNAccount"\Downloads\NotitiaReponoClient-1.13.0.341a0-py2.7.egg"

		### install shapely, elekta_dcc, elekta_dvt ###
		* pip install --trusted-host seudvpypkg01.dev.elekta.com --index-url http://seudvpypkg01.dev.elekta.com:8080 shapely
		* pip install --trusted-host seudvpypkg01.dev.elekta.com --index-url http://seudvpypkg01.dev.elekta.com:8080 elekta_dcc
		* pip install --trusted-host seudvpypkg01.dev.elekta.com --extra-index-url http://seudvpypkg01.dev.elekta.com:8080 elekta_dvt
		 


3. Install VScode --- "VSCodeSetup-x64-1.22.2"
	download from website:  https://code.visualstudio.com/Download 

	###### configuration ##### 
	3.1 Install Python extension if you donot have in your VScode:
		# Press shortcut key "Ctrl + Shift + X" to open Extensions Window 
		# Search "Python", Click Install   
	3.2 specify your python interpreter path to the Anaconda2 directory: 
		# Select View > Command Palette..., Enter into "Python:Select Interpreter" in the search window,
			select "C:\\Users\\"CNAccount"\\AppData\\Local\\Continuum\\Anaconda2\\python.exe"
		# Select the File > Preferences > Settings command (Ctrl+,) to open your User Settings.
		# Add or modify "python.pythonPath" in the "User Settings" tag, NOT the "Default Settings" tab. 
			windows: 
				"python.pythonPath": "C:\\Users\\"CNAccount"\\AppData\\Local\\Continuum\\Anaconda2\\python.exe"
	3.3 Debug config:
		# Select the Debug > Open Configration , to open your launch.json
		# Add the bellow dic to the top part in the "Configurations":
			{
       
				"name": "Python",
            
				"type": "python",
            
				"request": "launch",
            
				"stopOnEntry": true,
            
				"pythonPath": "${config:python.pythonPath}",
            
				"program": "${file}",
            
				"cwd": "C://Users//"CNAccount"//AppData//Local//Continuum//Anaconda2",
           
				"env": {},
           
				"envFile": "${workspaceFolder}/.env",
            
				"debugOptions": [
                
						"RedirectOutput"
            
						]
        
			}, 


************** testing tool using mannual *****************

       **** Main function ****
1. testPatients.py:  run the whole patient cases specified in the json file
   ***parameters need to be specified to your local json config file before you run testPatients.py:
   ### specify the json config file dir:	
	  json_config_dir = 'D:\\TestData\\practice'    
    	  jason_config_name = "init_config_test.json"   
   ### specify the BeamDirection: height OR width, only support those two direction
	BeamDirection = "height"

2. testSinglePatient.py:  only run single patient case with specified patient_case_name
   ***parameters need to be specified to your local json config file before you run testSinglePatient.py:
   # specify the json config file dir:	
	json_config_dir = 'D:\\TestData\\practice'    
    	jason_config_name = "init_config_test.json"   
   # specify the BeamDirection: height OR width, only support those two direction
	BeamDirection = "height" 
   # specify the patient_case_name:  get value from the json file, should be same with patient name in the json file
	patient_case_name = "18"



************** json config File parameters instruction**********

1. "dir_configuration":
	"patient_temp_dir":   the root directory of patient datas, 
				
	"ED_temp_dir":        the root directory of  ED datas
				
	"Machine_temp_dir":   the root directory of Machine file datas
	"test_exe_root":      the root directory of test excutable program datas
	"BenchMark_exe_root": the root directory of benchMarch excutable program datas
	"out_put_dir":        the root directory for the test results
	"RequestCS2UppsalaConvertor_dir":  the local directory of RequestCS2UppsalaConvertor.exe 
	"ResultUppsala2CSConvertor_dir":   the local directory of ResultUppsala2CSConvertor.exe 
	"ModifyProtonRequestFile_dir":     the local directory of ModifyProtonRequestFile.exe 	

2. "ini_paras_configuration":		
	"ini_grid_size":  set to the value used on the case of "patient_cases == 0"
	"err_delta_sigma_acceptance": 1e-05,  
			  used to set a threshold to count the error number of delta sigma: diff bigger than this value, err_count++ 
			  
	"min_delta_sigma_acceptPerc": 0.001,
			  used to set a threshold: thre = Max_benchMarch_value * min_delta_sigma_acceptPerc
			  less than thre, cal the absolute difference
			  more than thre, cal the relative difference
			  detailed implementation method can check the python file "CalcStatistic.py", 
				NOTE: similar implementation method for IDD,Dose1D,Dose2DGaussian,Dose3D
	"err_IDD_acceptance": 1e-05, 
	"min_IDD_acceptPerc": 0.001,
	"err_Dose1D_acceptance": 1e-05,
	"min_Dose1D_acceptPerc": 0.001,
	"err_Dose3D_acceptance": 1e-05,
	"min_Dose3D_acceptPerc": 0.001,
	"err_Dose2DGaussian_acceptance": 1e-05,
	"min_Dose2DGaussian_acceptPerc": 0.001

3. "patient_cases":
	"patient_tempfile_name": patient foldername located in the patient_temp_dir
				 contains three files "ProtonRequest","CalculationStatus","CarbonScanning_log"
	"test_exe_name": Proton release version foldername located in the test_exe_root
	"BenchMark_exe_name": benchMark excutable program foldername located in the BenchMark_exe_root
	"ED_file_name":  ED foldername located in the patient_temp_dir
	"Machine_file_name": machine foldername located in the Machine_temp_dir			
	"patient_change_condition":{
					parameters need be changed in the request file,like GridSize... 
					hard coded, thus should use the name spesified in the file "ProtonRequest_compare"				
				},			
	"Gammer_initi_configuration":{ used to calculate Gamma_index, please check
				       elekta_dvt.evaluation.gamma_index.py-->calculate_gamma_index_3d to see the detail implementation method,
				       still some issues exits, not quite clearly.
				"delta_distance_in_mm": 1,
				"delta_dose_percentage": 1,
				"ratio_voxels_within_tolerance" : 0.9,
				"search_radius": 2
				},
	"dose_diff_configuration": { curently this paras not be be used.
				"maxdose_lower": 0.05, 
				"maxdose_upper": 1.0, 
				"normalize_to_sum": false
				}
	
4. !!!!!!!!---Attention---!!!!!!!!!! 

	4.1. patient case with name "0" must be containted, used as the baseline reference patient data, 
		for other patient cases, base on this reference data "0",change the parameters specified on the part patient_change_condition.

	4.2. For "patient_cases == 0":
		# designed to compare "Latest Proton release Version" with "last Proton release Version",thus you can set like:
 
				"0":{
					"patient_tempfile_name": "test_98_Proton_5",
					"test_exe_name": "Release_25161", ----> latest proton build version
					"BenchMark_exe_name": "Release_25154",  ----> last version have the better dose   
					"ED_file_name": "ED_case5",
					"Machine_file_name": "tele",			
					"patient_change_condition":{					
						},			
					"Gammer_initi_configuration":{
						"delta_distance_in_mm": 1,
						"delta_dose_percentage": 1,
					"ratio_voxels_within_tolerance" : 0.9,
						"search_radius": 2
						},
					"dose_diff_configuration": {
						"maxdose_lower": 0.05, 
						"maxdose_upper": 1.0, 
						"normalize_to_sum": false
						}
				    },

	4.3. "BenchMark_exe_name": if benchMark excutable program is 'ProtonPencilBeamExecutable.exe', the folder name must contain specical word "Uppsala**"
		
	4.4. "patient_change_condition": use the name specified in the file "ProtonRequest_compare" when you want to change Request file

	4.5. Please refer to " swap(\\10.140.115.108):\Jedi\Tools\Python Scripts test tool\practice\", to see the detail folder infor.
	




