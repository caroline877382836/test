import numpy as np
import os
import struct
import pylab
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from xlsxwriter.workbook import Workbook
import subprocess

import elekta_dvt as dvt
import elekta_dvt.model as model
import elekta_dvt.plots as dvt_plot
import elekta_dvt.dvt_io as dvt_io
import elekta_dvt.dvt_config as dvt_config
from elekta_dvt.calculators.gpumcd_calculator import GpumcdCalculator
from elekta_dvt.model import Dose3D
from elekta_dvt.evaluation.gamma_index import calculate_gamma_index_3d
from dask.dataframe.tests.test_rolling import idx

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
    worksheet.insert_image(raw + 20, column,img_path,{'x_scale': 0.5, 'y_scale': 0.5})
    return 0

if __name__ == "__main__" :   
    
    path_CS = 'C:\\Users\\Public\\Documents\\PTW\\VeriSoft\\Data\\test_caro\\CS\\PhysicalDose.00'
    path_Upsala = 'C:\\Users\\Public\\Documents\\PTW\\VeriSoft\\Data\\test_caro\\Upsala\\IDOSELocalFiles.1'
    
    #===========================================================================
    # filepath="D:/TestData/ProtonScanDose.bat"
    # p = subprocess.Popen(filepath, shell=True, stdout = subprocess.PIPE)
    # #####check if success
    # stdout, stderr = p.communicate()
    # print p.returncode  ## return 0 success
    #===========================================================================
    
    #===========================================================================
    # # call exe
    # args = ["D:/code/Jedi_Proton_CarbonScanning/x64/Release/ProtonScanning.exe", "D:/TestData/SingleSpot/test_98_Proton/", "C:/Users/Public/Documents/CMS/FocalData/Installation/2~myfolder/"]
    # subprocess.call(args)
    #===========================================================================
    
    INPUT_FOLDER = 'D:\\'
    os.chdir(INPUT_FOLDER)
    cur_dir = os.getcwd()
    base_dir = os.path.abspath(os.path.join(cur_dir, os.pardir))  
    
    # Create an new Excel file and add a worksheet.
    workbook = Workbook('images.xlsx')
    worksheet = workbook.add_worksheet()
    # Widen the first column to make the text clearer.
    worksheet.set_column('A:A', 30)
    # Insert an image.
    worksheet.write('A2', 'Insert an image in a cell:')
    worksheet.insert_image('B2', 'C:\Users\Cnxuacar\Desktop\Figure_3.png',{'x_scale': 0.5, 'y_scale': 0.5})
    workbook.close()
    
    grid_size = 2
    BeamDirection = "height"
    Num_of_fraction = 30 
    Gy_2_CGy= 100   
    data_CS = read_binaryFile(path_CS)
    data_CS = np.multiply(Num_of_fraction * Gy_2_CGy, data_CS)
    IDD_CS = Cal_IDD(data_CS,BeamDirection)
    brag_peak_CS = find_blagPeak(IDD_CS)
    plot_idd(IDD_CS)
    data_Upsala = read_binaryFile(path_Upsala)
    size_in_mm = [grid_size * data_CS.shape[0], grid_size * data_CS.shape[1], grid_size * data_CS.shape[2]]
    doseLabel = 'Gaussian'
# Generate a 3D point grid from the total size [mm] and the number of voxels.
    point_grid = model.PointGrid3D.from_size(size_in_mm , 
                                             number_of_voxels = [data_CS.shape[0], data_CS.shape[1], data_CS.shape[2]], 
                                             is_surface_at_zero = [False, False, False])
    dose_CS = Dose3D(data_CS)    
    dose_CS.x = point_grid.xs
    dose_CS.y = point_grid.ys
    dose_CS.z = point_grid.zs
    
    dose_Upsala = Dose3D(data_Upsala) 
    dose_Upsala.x = point_grid.xs
    dose_Upsala.y = point_grid.ys
    dose_Upsala.z = point_grid.zs
    
    xIndex = np.int(dose_CS.x.size/2)
    yIndex = np.int(dose_CS.y.size/2)
    zIndex = np.int(dose_CS.z.size/2)   #[80,3,80]
    ####plot
    if BeamDirection.lower() == "height":
        dvt_plot.plot_line_doses_x(dose_CS, brag_peak_CS, zIndex, doseLabel)  # line_dose_plots,line_plots
        pylab.savefig("plot line brag_peak:" + brag_peak_CS + zIndex)
        dvt_plot.plot_plane_dose_xz(dose_CS, brag_peak_CS, doseLabel) # plane_dose_plots
        pylab.savefig("plot plane brag_peak:" + brag_peak_CS)
    elif BeamDirection.lower() == "width": # Tran plane in Monaco-x direction   
        dvt_plot.plot_line_doses_x(dose_CS, yIndex, brag_peak_CS, doseLabel)  # line_dose_plots,line_plots
        pylab.savefig("plot line brag_peak:" + brag_peak_CS + zIndex)
        dvt_plot.plot_plane_dose_xy(dose_CS, brag_peak_CS, doseLabel) # plane_dose_plots
        pylab.savefig("plot plane brag_peak:" + brag_peak_CS)
        
    doses = [dose_CS, dose_Upsala]
    doseLabels = ['CS', 'Upsala']
    dvt_plot.plot_line_diff_hist_x(doses, brag_peak_CS, zIndex, 20, doseLabels)
    pylab.savefig("plot line diff hist:" + brag_peak_CS + zIndex)
    dvt_plot.plot_plane_diff_hist_xz(doses, brag_peak_CS, 20, doseLabels) # dose_diff_histogram
    pylab.savefig("plot plane brag_peak:" + brag_peak_CS)
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
    dvt_plot.plot_line_gamma_index_y(gamma_result_container, gamma_result_xIndex, gamma_result_zIndex, gamma_result_label)

    