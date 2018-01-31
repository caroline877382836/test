import numpy as np
import os
import struct
import pylab
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from xlsxwriter.workbook import Workbook
import subprocess
from time import gmtime, strftime
import readJason
from readJason import ReadJason
from readJason import ParseSinglePatientConfig
import shutil
from readJason import MergeFilesFromTwoFolder
from Initi_Config_Parameters import InitParameters
from ReadDose import ReadCSDose
import CalcSigmaXY
from CalcSigmaXY import CalcSigmaX_Y
import WriteToExcel
from WriteToExcel import WriteDada2Excel
import xlwt

import elekta_dvt as dvt
import elekta_dvt.model as model
import elekta_dvt.plots as dvt_plot
import elekta_dvt.dvt_io as dvt_io
import elekta_dvt.dvt_config as dvt_config
from elekta_dvt.calculators.gpumcd_calculator import GpumcdCalculator
from elekta_dvt.model import Dose3D
from elekta_dvt.evaluation.gamma_index import calculate_gamma_index_3d
from dask.dataframe.tests.test_rolling import idx



def Cal_IDD(data,BeamDirection):
    data_shape = data.shape
    idd = []
    if BeamDirection.lower() == "height": # Tran plane in Monaco-z direction
        for index in range(data_shape[1]):
            idd.append(np.sum(data[:,index,:]))
    elif BeamDirection.lower() == "width": # Tran plane in Monaco-x direction
        for index in range(data_shape[2]):
            idd.append(np.sum(data[:,:,index]))   
    return idd 

def find_blagPeak(idd):
    max_value = max(idd)
    for idx in range(len(idd)):
        if idd[idx] == max_value:
            brag_peak = idx
    return brag_peak

def plot_idd(idd): 
    plt.figure()        
    plt.plot(idd, 'bo')  # 'r--','bs','g^': red dashes, blue squares and green triangles
    plt.show()
    
def insert_image2Excel(worksheet,raw,column,msg,img_path):
    worksheet.write(raw,column, msg)
    worksheet.insert_image(raw + 1, column,img_path)
    return 0

def insertSigmaXY2Excel(worksheet,raw_idx,benchMarch_sigma_lst,protonCS_sigma_lst,del_sigma_lst):  
    worksheet.write(raw_idx, 0, "benchMarch_sigmaX") 
    worksheet.write(raw_idx, 1, "benchMarch_sigmaY") 
    worksheet.write(raw_idx, 2, "protonCS_sigmaX") 
    worksheet.write(raw_idx, 3, "protonCS_sigmaY")
    worksheet.write(raw_idx, 4, "delta_sigmaX")  # bench - Proton
    worksheet.write(raw_idx, 5, "delta_sigmaY") 
    for idx in range(0,len(benchMarch_sigma_lst),1):
        worksheet.write(raw_idx + idx + 2, 0, benchMarch_sigma_lst[idx][0])
        worksheet.write(raw_idx + idx + 2, 1, benchMarch_sigma_lst[idx][1])
        worksheet.write(raw_idx + idx + 2, 2, protonCS_sigma_lst[idx][0])
        worksheet.write(raw_idx + idx + 2, 3, protonCS_sigma_lst[idx][1])
        worksheet.write(raw_idx + idx + 2, 4, del_sigma_lst[idx][0])
        worksheet.write(raw_idx + idx + 2, 5, del_sigma_lst[idx][1])
    raw_idx = raw_idx + len(benchMarch_sigma_lst) + 2
    return raw_idx 

def re_cal_dose(patient_path,exe_path,machine_path):
    args = [exe_path, patient_path, machine_path]
    subprocess.call(args)

def re_construct2_Upsaladdata_type(dose_3D,point_grid):
    dose = Dose3D(dose_3D)    
    dose.x = point_grid.xs
    dose.y = point_grid.ys
    dose.z = point_grid.zs
    return dose

def IDD_plot_save_insert_excel(IDD, book,raw_idx):
    plot_idd(IDD)
    pylab.savefig("IDD")
    book.insert_image2Excel(raw_idx,0,"plot IDD",os.path.join(os.getcwd(),"IDD.png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def line_doses_x_plot_save_insert_excel(dose_CS, book,raw_idx,brag_peak_CS,zIndex, doseLabel):  
    dvt_plot.plot_line_doses_x(dose_CS, brag_peak_CS, zIndex, doseLabel)  # line_dose_plots,line_plots
    pylab.savefig("plotDoseXbragPeak_" + str(brag_peak_CS))
    book.insert_image2Excel(raw_idx,0,"plot Dose line",os.path.join(cur_dir,"plotDoseXbragPeak_" + str(brag_peak_CS) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def plane_doseXZ_plot_save_insert_excel(dose_CS, book,raw_idx,brag_peak_CS, doseLabel):
    dvt_plot.plot_plane_dose_xz(dose_CS, brag_peak_CS, doseLabel) # plane_dose_plots
    pylab.savefig("plotDosePlaneXZBragPeak_" + str(brag_peak_CS))
    book.insert_image2Excel(raw_idx,0,"plot Dose Plane ",os.path.join(cur_dir,"plotDosePlaneXZBragPeak_" + str(brag_peak_CS) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def plane_doseXY_plot_save_insert_excel(dose_CS, book,raw_idx,brag_peak_CS, doseLabel):
    dvt_plot.plot_plane_dose_xy(dose_CS, str(brag_peak_CS), doseLabel) # plane_dose_plots
    pylab.savefig("plotDosePlaneXYBragPeak_" + str(brag_peak_CS))
    book.insert_image2Excel(raw_idx,0,"plot Dose Plane",os.path.join(cur_dir,"plotDosePlaneXYBragPeak_" + str(brag_peak_CS) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx
    
def line_diff_histX_plot_save_insert_excel(doses, book,raw_idx,brag_peak_CS, zIndex,doseLabels): #
    dvt_plot.plot_line_diff_hist_x(doses, brag_peak_CS, zIndex, 20, doseLabels)
    pylab.savefig("plotDoseDiffLineXBragPeak_" + str(brag_peak_CS))
    book.insert_image2Excel(raw_idx,0,"plot dose Diff",os.path.join(cur_dir,"plotDoseDiffLineXBragPeak_" + str(brag_peak_CS) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def plane_diff_histXZ_plot_save_insert_excel(doses, book,raw_idx,brag_peak_CS,doseLabels): 
    dvt_plot.plot_plane_diff_hist_xz(doses, brag_peak_CS, 20, doseLabels) # dose_diff_histogram
    pylab.savefig("plotPlaneDiffBrag_peak_" + str(brag_peak_CS))
    book.insert_image2Excel(raw_idx,0,"plot dose plane Diff",os.path.join(cur_dir,"plotPlaneDiffBrag_peak_" + str(brag_peak_CS) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def line_gamma_indexY_plot_save_insert_excel(gamma_result_container, gamma_result_xIndex,book,raw_idx,gamma_result_label):
    dvt_plot.plot_line_gamma_index_y(gamma_result_container, gamma_result_xIndex, gamma_result_zIndex, gamma_result_label)
    pylab.savefig("plotGammerResult")
    book.insert_image2Excel(raw_idx,0,"plot dose plane Diff",os.path.join(cur_dir,"plotGammerResult" + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx
       
if __name__ == "__main__" :  
    
    json_config_dir = 'D:\\TestData\\practice'     
    jason_config_name = "init_config.json"
    init_paras = InitParameters(json_config_dir,jason_config_name)
    init_paras.init_single_patient_paras("patient_case_2")     
    
    #### setting parameters
    grid_size = 2
    Gy_2_CGy= 100
    BeamDirection = "height"
    Num_of_fraction = 30
    scale_Monaco2DoseEngine = Gy_2_CGy*Num_of_fraction
    image_size = 24 
    os.chdir(init_paras.output_path)
    cur_dir = os.getcwd()       
    # TODO--  modify request file,save data to another folder
    
    # call ProtonScanning.exe to recal dose   
    re_cal_dose(init_paras.patient_path_CS,init_paras.exe_path_CS,init_paras.machine_path_CS)
    
    # call UpsalaScanning.exe to recal dose   
    re_cal_dose(init_paras.patient_path_Upsala,init_paras.exe_path_Upsala,init_paras.machine_path_Upsala)
    
    #===========================================================================
    # filepath="D:/TestData/ProtonScanDose.bat"
    # p = subprocess.Popen(filepath, shell=True, stdout = subprocess.PIPE)
    # #####check if success
    # stdout, stderr = p.communicate()
    # print p.returncode  ## return 0 success
    #===========================================================================
    
    
    excel_name = strftime("%Y-%m-%d %H:%M:%S", gmtime()).replace(':', '-')     # set as current time
    
    #===========================================================================
    # # Create an new Excel file and add a worksheet.
    # workbook = Workbook(excel_name + '_output1.xlsx')
    # worksheet = workbook.add_worksheet()
    # # Widen the first column to make the text clearer.
    # worksheet.set_column('A:A', 10)
    # #worksheet.insert_image('B2', 'C:\Users\Cnxuacar\Desktop\Figure_3.png',{'x_scale': 0.5, 'y_scale': 0.5})
    # #workbook.close()
    #===========================================================================
     
    
    data_CS = ReadCSDose(os.path.join(init_paras.patient_path_CS,"PhysicalDose.00"))    
    #data_CS = np.multiply(scale_Monaco2DoseEngine, data_CS.Data3D)
    
    IDD_CS = Cal_IDD(data_CS.Data3D,BeamDirection)
    brag_peak_CS = find_blagPeak(IDD_CS)
    
        
    sigmas = CalcSigmaX_Y(os.path.join(init_paras.patient_path_Upsala,"PhysicalDose.00"),
                 os.path.join(init_paras.patient_path_CS,"PhysicalDose.00"),
                 grid_size)
    [benchMarch_sigma, protonCS_sigma, del_sigma] = sigmas.Get_sigmas_of_multi_Layers(BeamDirection, brag_peak_CS, 20)
    
    book = WriteDada2Excel(excel_name + '_output1.xlsx')
    sheet_raw_idx = book.add_sheet("patient_case_2",len(benchMarch_sigma))
    sheet_raw_idx = sheet_raw_idx  
    
    sheet_raw_idx = book.write_sigmas_2_sheet(sheet_raw_idx,benchMarch_sigma, protonCS_sigma, del_sigma)
    
    plot_idd(IDD_CS)
    pylab.savefig("IDD_CS")
    sheet_raw_idx = book.insert_image2Excel(sheet_raw_idx, 0, "plot IDD_CS", os.path.join(os.getcwd(),"IDD_CS.png"))    
            
    #sheet_raw_idx = insertSigmaXY2Excel(worksheet,sheet_raw_idx,benchMarch_sigma,protonCS_sigma,del_sigma)
    
    #sheet_raw_idx = IDD_plot_save_insert_excel(IDD_CS,worksheet,sheet_raw_idx)
    
    ##TODO: change upsala dose name
    data_Upsala = ReadCSDose(os.path.join(init_paras.patient_path_Upsala,"PhysicalDose.00"))
    IDD_Upsala = Cal_IDD(data_Upsala.Data3D,BeamDirection)    
    brag_peak_Upsala = find_blagPeak(IDD_Upsala)
    plot_idd(IDD_Upsala)
    pylab.savefig("IDD_Upsala")
    sheet_raw_idx = book.insert_image2Excel(sheet_raw_idx, 0, "plot IDD_Upsala", os.path.join(os.getcwd(),"IDD_Upsala.png"))
    
    size_in_mm = [grid_size * data_CS.Data3D.shape[0], 
                  grid_size * data_CS.Data3D.shape[1],
                  grid_size * data_CS.Data3D.shape[2]]
    doseLabel = 'Gaussian'
# Generate a 3D point grid from the total size [mm] and the number of voxels.
    point_grid = model.PointGrid3D.from_size(size_in_mm , 
                                             number_of_voxels = [data_CS.Data3D.shape[0], data_CS.Data3D.shape[1], data_CS.Data3D.shape[2]], 
                                             is_surface_at_zero = [False, False, False])
    
    dose_CS = re_construct2_Upsaladdata_type(data_CS.Data3D,point_grid)    
    dose_Upsala = re_construct2_Upsaladdata_type(data_Upsala.Data3D,point_grid) 
    
    xIndex = np.int(dose_CS.x.size/2)
    yIndex = np.int(dose_CS.y.size/2)
    zIndex = np.int(dose_CS.z.size/2)   
    ####plot
    if BeamDirection.lower() == "height":
        sheet_raw_idx = line_doses_x_plot_save_insert_excel(dose_CS, book,sheet_raw_idx,brag_peak_CS,zIndex, doseLabel)  # line_dose_plots,line_plots
        sheet_raw_idx = plane_doseXZ_plot_save_insert_excel(dose_CS, book,sheet_raw_idx,brag_peak_CS, doseLabel)
    elif BeamDirection.lower() == "width": # Tran plane in Monaco-x direction   
        sheet_raw_idx = line_doses_x_plot_save_insert_excel(dose_CS, book,sheet_raw_idx,brag_peak_CS,yIndex, doseLabel)  # line_dose_plots,line_plots
        sheet_raw_idx = plane_doseXY_plot_save_insert_excel(dose_CS, book,sheet_raw_idx,brag_peak_CS, doseLabel)
        
    doses = [dose_CS, dose_Upsala]
    doseLabels = ['CS', 'Upsala']
    sheet_raw_idx = line_diff_histX_plot_save_insert_excel(doses, book,sheet_raw_idx,brag_peak_CS, zIndex,doseLabels)    
    sheet_raw_idx = plane_diff_histXZ_plot_save_insert_excel(doses, book,sheet_raw_idx,brag_peak_CS,doseLabels)
        
    # calc gamma index
    delta_distance_in_mm = 1       #Enter tolerance distance (mm):
    delta_dose_percentage = 1     #Enter tolerance level (%):  
    ratio_voxels_within_tolerance = 90/100.  #Enter ratio of voxels to be within the tolerance for the test to pass
    search_radius = 3
    result_as_booleans = False
    gamma_result = calculate_gamma_index_3d(dose_Upsala,
                                        dose_CS, 
                                        delta_distance_in_mm, 
                                        delta_dose_percentage/100., 
                                        search_radius, 
                                        result_as_booleans,
                                        ratio_voxels_within_tolerance)
    gamma_result_label = 'Gamma index'
    gamma_result_container = gamma_result._gamma_result_container
    gamma_result_xIndex = np.int(gamma_result_container.x.size/2)
    gamma_result_yIndex = np.int(gamma_result_container.y.size/2)
    gamma_result_zIndex = np.int(gamma_result_container.z.size/2)
    
    #dvt_plot.interact_line_gamma_index(gamma_result_container, gamma_result_label)
    sheet_raw_idx = line_gamma_indexY_plot_save_insert_excel(gamma_result_container, gamma_result_xIndex,book,sheet_raw_idx,gamma_result_label)    
    
    book.save_sheet()

    