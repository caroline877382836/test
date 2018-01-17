import numpy as np
import os
import struct
import pylab
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from xlsxwriter.workbook import Workbook
import subprocess
from time import gmtime, strftime

import elekta_dvt as dvt
import elekta_dvt.model as model
import elekta_dvt.plots as dvt_plot
import elekta_dvt.dvt_io as dvt_io
import elekta_dvt.dvt_config as dvt_config
from elekta_dvt.calculators.gpumcd_calculator import GpumcdCalculator
from elekta_dvt.model import Dose3D
from elekta_dvt.evaluation.gamma_index import calculate_gamma_index_3d
from dask.dataframe.tests.test_rolling import idx

from GaussianUtility import GaussianERFFitException
from GaussianUtility import WriteDada2Excel
from GaussianUtility import GaussianERFFit
from GaussianUtility import ReadDada

def read_binaryFile(path):
    floatSize = 4
    intSize = 4
    f = open(path, 'rb')
    width = f.read(intSize)
    width = struct.unpack('L',width)
    height = f.read(intSize)
    height = struct.unpack('L',height)
    depth = f.read(intSize)
    depth = struct.unpack('L',depth)
    
    shape = np.array([width[0],height[0],depth[0]])
    len = shape[0]*shape[1]*shape[2]
    data = f.read(floatSize*len)    
    data = struct.unpack(len.astype(str) + 'f',data)
    data = np.array(data) # change tuple to array
    data = data.reshape(shape[2],shape[1],shape[0]) #change to depth,height,width (Tra:width = x, height = z)
    return data

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

def IDD_plot_save_insert_excel(IDD, worksheet,raw_idx):
    plot_idd(IDD)
    pylab.savefig("IDD")
    insert_image2Excel(worksheet,raw_idx,0,"plot IDD",os.path.join(os.getcwd(),"IDD.png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def line_doses_x_plot_save_insert_excel(dose_CS, worksheet,raw_idx,brag_peak_CS,zIndex, doseLabel):  
    dvt_plot.plot_line_doses_x(dose_CS, brag_peak_CS, zIndex, doseLabel)  # line_dose_plots,line_plots
    pylab.savefig("plotDoseXbragPeak_" + str(brag_peak_CS))
    insert_image2Excel(worksheet,raw_idx,0,"plot Dose line",os.path.join(cur_dir,"plotDoseXbragPeak_" + str(brag_peak_CS) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def plane_doseXZ_plot_save_insert_excel(dose_CS, worksheet,raw_idx,brag_peak_CS, doseLabel):
    dvt_plot.plot_plane_dose_xz(dose_CS, brag_peak_CS, doseLabel) # plane_dose_plots
    pylab.savefig("plotDosePlaneXZBragPeak_" + str(brag_peak_CS))
    insert_image2Excel(worksheet,raw_idx,0,"plot Dose Plane ",os.path.join(cur_dir,"plotDosePlaneXZBragPeak_" + str(brag_peak_CS) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def plane_doseXY_plot_save_insert_excel(dose_CS, worksheet,raw_idx,brag_peak_CS, doseLabel):
    dvt_plot.plot_plane_dose_xy(dose_CS, str(brag_peak_CS), doseLabel) # plane_dose_plots
    pylab.savefig("plotDosePlaneXYBragPeak_" + str(brag_peak_CS))
    insert_image2Excel(worksheet,raw_idx,0,"plot Dose Plane",os.path.join(cur_dir,"plotDosePlaneXYBragPeak_" + str(brag_peak_CS) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx
    
def line_diff_histX_plot_save_insert_excel(doses, worksheet,raw_idx,brag_peak_CS, zIndex,doseLabels): #
    dvt_plot.plot_line_diff_hist_x(doses, brag_peak_CS, zIndex, 20, doseLabels)
    pylab.savefig("plotDoseDiffLineXBragPeak_" + str(brag_peak_CS))
    insert_image2Excel(worksheet,raw_idx,0,"plot dose Diff",os.path.join(cur_dir,"plotDoseDiffLineXBragPeak_" + str(brag_peak_CS) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def plane_diff_histXZ_plot_save_insert_excel(doses, worksheet,raw_idx,brag_peak_CS,doseLabels): 
    dvt_plot.plot_plane_diff_hist_xz(doses, brag_peak_CS, 20, doseLabels) # dose_diff_histogram
    pylab.savefig("plotPlaneDiffBrag_peak_" + str(brag_peak_CS))
    insert_image2Excel(worksheet,raw_idx,0,"plot dose plane Diff",os.path.join(cur_dir,"plotPlaneDiffBrag_peak_" + str(brag_peak_CS) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def line_gamma_indexY_plot_save_insert_excel(gamma_result_container, gamma_result_xIndex,worksheet,raw_idx,gamma_result_label):
    dvt_plot.plot_line_gamma_index_y(gamma_result_container, gamma_result_xIndex, gamma_result_zIndex, gamma_result_label)
    pylab.savefig("plotGammerResult")
    insert_image2Excel(worksheet,raw_idx,0,"plot dose plane Diff",os.path.join(cur_dir,"plotGammerResult" + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def cal_sigma(path_benchMark,path_proton,direction,grid,brag_peak_CS):
    data_2DbenchMark = ReadDada(path_benchMark, direction, 5)        
    lay_cnt = data_2DbenchMark._layer_cnt
    benchMarch_sigma = []  # [sigmaX,sigmaY]
    protonCS_sigma = []
    del_sigma = []
    for lay_idx in range(max(0,brag_peak_CS - 10), brag_peak_CS + 10, 1):  # loop for all the layers                
        data_2DbenchMark = ReadDada(path_benchMark, direction, lay_idx)
        data_2Dproton = ReadDada(path_proton, direction, lay_idx)
                
        axx_benchMarch = GaussianERFFit(data_2DbenchMark._data2D, grid)
        axx_proton = GaussianERFFit(data_2Dproton._data2D, grid)
                 
        try:                    
            if hasattr(axx_benchMarch, 'sigmaX'):
                benchMarch_sigma.append([axx_benchMarch.sigmaX, axx_benchMarch.sigmaY])
            else:
                benchMarch_sigma.append([0, 0]) # zero dose case: assign to sigmaX and sigmaY to 0 currently
        except:
            pass
                
        try:
            if hasattr(axx_proton, 'sigmaX'):
                protonCS_sigma.append([axx_proton.sigmaX, axx_proton.sigmaY])
            else:
                protonCS_sigma.append([0, 0]) # zero dose case: assign to sigmaX and sigmaY to 0 currently
        except:
            pass                
        del_sigma.append([axx_benchMarch.sigmaX - axx_proton.sigmaX, axx_benchMarch.sigmaY - axx_proton.sigmaY])    
    return  benchMarch_sigma, protonCS_sigma, del_sigma
       
if __name__ == "__main__" :  
        
    patient_path_CS = "D:/TestData/test_98_Proton/"
    exe_path_CS = "D:/code/Jedi_Proton_CarbonScanning/x64/Release/ProtonScanning.exe"  
    machine_path_CS = "C:/Users/Public/Documents/CMS/FocalData/Installation/2~myfolder/"
    ####TODO: change upsala parameters
    patient_path_Upsala = "D:/TestData/test_98_Upsala/"
    exe_path_Upsala = "D:/code/Jedi_Proton_CarbonScanning/x64/Release/ProtonScanning.exe"  
    machine_path_Upsala = "C:/Users/Public/Documents/CMS/FocalData/Installation/2~myfolder/"
    
    output_excel_path = "D:/TestData/"
    #### setting parameters
    grid_size = 2
    Gy_2_CGy= 100
    BeamDirection = "height"
    Num_of_fraction = 30
    scale_Monaco2DoseEngine = Gy_2_CGy*Num_of_fraction
    image_size = 24 
    os.chdir(output_excel_path)
    cur_dir = os.getcwd()       
    # TODO--  modify request file,save data to another folder
    
    # call ProtonScanning.exe to recal dose   
    re_cal_dose(patient_path_CS,exe_path_CS,machine_path_CS)
    
    # call UpsalaScanning.exe to recal dose   
    re_cal_dose(patient_path_Upsala,exe_path_Upsala,machine_path_Upsala)
    
    #===========================================================================
    # filepath="D:/TestData/ProtonScanDose.bat"
    # p = subprocess.Popen(filepath, shell=True, stdout = subprocess.PIPE)
    # #####check if success
    # stdout, stderr = p.communicate()
    # print p.returncode  ## return 0 success
    #===========================================================================
    
    # Create an new Excel file and add a worksheet.
    excel_name = strftime("%Y-%m-%d %H:%M:%S", gmtime()).replace(':', '-')     # set as current time
    workbook = Workbook(excel_name + '_output.xlsx')
    worksheet = workbook.add_worksheet()
    # Widen the first column to make the text clearer.
    worksheet.set_column('A:A', 10)
    #worksheet.insert_image('B2', 'C:\Users\Cnxuacar\Desktop\Figure_3.png',{'x_scale': 0.5, 'y_scale': 0.5})
    #workbook.close()
    sheet_raw_idx = 1   
    
    data_CS = read_binaryFile(os.path.join(patient_path_CS,"PhysicalDose.00"))
    data_CS = np.multiply(scale_Monaco2DoseEngine, data_CS)
    IDD_CS = Cal_IDD(data_CS,BeamDirection)
    brag_peak_CS = find_blagPeak(IDD_CS)    
    
    [benchMarch_sigma, protonCS_sigma, del_sigma] = cal_sigma(os.path.join(patient_path_Upsala,"PhysicalDose.00"),
                                                              os.path.join(patient_path_CS,"PhysicalDose.00"),
                                                              BeamDirection,
                                                              grid_size,
                                                              brag_peak_CS) 
    sheet_raw_idx = insertSigmaXY2Excel(worksheet,sheet_raw_idx,benchMarch_sigma,protonCS_sigma,del_sigma)
    
    sheet_raw_idx = IDD_plot_save_insert_excel(IDD_CS,worksheet,sheet_raw_idx)
    
    ##TODO: change upsala dose name
    data_Upsala = read_binaryFile(os.path.join(patient_path_Upsala,"PhysicalDose.00"))
    size_in_mm = [grid_size * data_CS.shape[0], grid_size * data_CS.shape[1], grid_size * data_CS.shape[2]]
    doseLabel = 'Gaussian'
# Generate a 3D point grid from the total size [mm] and the number of voxels.
    point_grid = model.PointGrid3D.from_size(size_in_mm , 
                                             number_of_voxels = [data_CS.shape[0], data_CS.shape[1], data_CS.shape[2]], 
                                             is_surface_at_zero = [False, False, False])
    
    dose_CS = re_construct2_Upsaladdata_type(data_CS,point_grid)    
    dose_Upsala = re_construct2_Upsaladdata_type(data_Upsala,point_grid) 
    
    xIndex = np.int(dose_CS.x.size/2)
    yIndex = np.int(dose_CS.y.size/2)
    zIndex = np.int(dose_CS.z.size/2)   
    ####plot
    if BeamDirection.lower() == "height":
        sheet_raw_idx = line_doses_x_plot_save_insert_excel(dose_CS, worksheet,sheet_raw_idx,brag_peak_CS,zIndex, doseLabel)  # line_dose_plots,line_plots
        sheet_raw_idx = plane_doseXZ_plot_save_insert_excel(dose_CS, worksheet,sheet_raw_idx,brag_peak_CS, doseLabel)
    elif BeamDirection.lower() == "width": # Tran plane in Monaco-x direction   
        sheet_raw_idx = line_doses_x_plot_save_insert_excel(dose_CS, worksheet,sheet_raw_idx,brag_peak_CS,yIndex, doseLabel)  # line_dose_plots,line_plots
        sheet_raw_idx = plane_doseXY_plot_save_insert_excel(dose_CS, worksheet,sheet_raw_idx,brag_peak_CS, doseLabel)
        
    doses = [dose_CS, dose_Upsala]
    doseLabels = ['CS', 'Upsala']
    sheet_raw_idx = line_diff_histX_plot_save_insert_excel(doses, worksheet,sheet_raw_idx,brag_peak_CS, zIndex,doseLabels)    
    sheet_raw_idx = plane_diff_histXZ_plot_save_insert_excel(doses, worksheet,sheet_raw_idx,brag_peak_CS,doseLabels)
        
    # calc gamma index
    delta_distance_in_mm = 1       #Enter tolerance distance (mm):
    delta_dose_percentage = 1     #Enter tolerance level (%):  
    ratio_voxels_within_tolerance = 90/100.  #Enter ratio of voxels to be within the tolerance for the test to pass
    search_radius = 5
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
    sheet_raw_idx = line_gamma_indexY_plot_save_insert_excel(gamma_result_container, gamma_result_xIndex,worksheet,sheet_raw_idx,gamma_result_label)    
    workbook.close()

    