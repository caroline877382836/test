import numpy as np
import os
import struct
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

import elekta_dvt as dvt
import elekta_dvt.model as model
import elekta_dvt.plots as dvt_plot
import elekta_dvt.dvt_io as dvt_io
import elekta_dvt.dvt_config as dvt_config
from elekta_dvt.calculators.gpumcd_calculator import GpumcdCalculator

def read_binaryFile(path):
    floatSize = 4
    intSize = 4
    f = open(path, 'rb')
    width = f.read(intSize)
    width = struct.unpack('i',width)
    height = f.read(intSize)
    height = struct.unpack('i',height)
    depth = f.read(intSize)
    depth = struct.unpack('i',depth)
    
    shape = np.array([width[0],height[0],depth[0]])
    len = shape[0]*shape[1]*shape[2]
    data = f.read(floatSize*len)    
    data = struct.unpack(len.astype(str) + 'f',data)
    data = np.array(data) # change tuple to array
    data = data.reshape(shape[2],shape[1],shape[0]) #change to depth,height,width (Tra:width = x, height = z)
    return data

def plot_Gaussian(data, BeamDirection, planeIndex):    
    fig = plt.figure(planeIndex, figsize=(10,10))
    ax = Axes3D(fig)
    ax.set_title(BeamDirection +'_' + str(planeIndex))
    
    if BeamDirection.lower() == "height": # Tran plane in Monaco-z direction 
        
        X = np.arange(0,data.shape[2],1)
        Y = np.arange(0,data.shape[0],1)
        X,Y = np.meshgrid(X,Y)
        ax.plot_surface(X,Y,data[:,planeIndex,:],rstride=1,cstride=1,cmap='rainbow')
        plt.show()
        
    elif BeamDirection.lower() == "width": # Tran plane in Monaco-x direction
        X = np.arange(0,data.shape[1],1)
        Y = np.arange(0,data.shape[0],1)
        X,Y = np.meshgrid(X,Y)
        ax.plot_surface(X,Y,data[:,:,planeIndex],rstride=1,cstride=1,cmap='rainbow')
        plt.show()
 
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

def plot_idd(idd): 
    plt.figure()        
    plt.plot(idd, 'bo')  # 'r--','bs','g^': red dashes, blue squares and green triangles
    plt.show() 
    
def calc_plot_gamma(meas_dose):
    delta_distance = 2.  # 2.0 mm
    delta_dose_fraction = 0.02  # 2.0 %
    gamma_result = dvt.evaluation.calculate_gamma_index_profile(meas_dose, calc_dose,
                                                                delta_distance=delta_distance, 
                                                                delta_dose_fraction=delta_dose_fraction,
                                                                calculate_level2_pass=True)

    dvt.plots.plot_gamma_index_profile(meas_dose, calc_dose, gamma_result, hAxisUnit='mm', vAxisUnit='Gy',
                                       lineLabels = ['Meas.', 'Calc.']);
 
     
 
if __name__ == "__main__" :   
    
    path_Upsala = "D:\TestData\SingleSpot\test_98\IDOSELocalFiles.1"
    path_CS = "D:\TestData\SingleSpot\test_98_Proton\PhysicalDose.00"
    beam_dir = "Height"
    
    data_CS = read_binaryFile(path_CS)
    data_Upsala = read_binaryFile(path_Upsala)
    IDD_CS = Cal_IDD(data_CS,beam_dir)
    IDD_Upsala = Cal_IDD(data_Upsala,beam_dir)
    
    [meas_depth_dose, meas_xprofile_dose,meas_zprofile_dose]= data_CS
    calc_dose = data_Upsala
    
    #===========================================================================
    # dvt_plot.plot_profile_dose(meas_depth_dose, calc_dose, plotDifference=True, hAxisUnit='mm', vAxisUnit='Gy',
    #                            lineLabels=['Meas.', 'Calc.'])
    # calc_plot_gamma(meas_depth_dose)
    #===========================================================================
    
    #===========================================================================
    # dvt_plot.plot_profile_dose(meas_xprofile_dose, calc_dose, plotDifference=True, hAxisUnit='mm', vAxisUnit='Gy',
    #                            lineLabels=['Meas.', 'Calc.']);
    # dvt_plot.plot_profile_dose(meas_zprofile_dose, calc_dose, plotDifference=True, hAxisUnit='mm', vAxisUnit='Gy',
    #                            lineLabels=['Meas.', 'Calc.']);
    #===========================================================================
    
    #===========================================================================
    # calc_plot_gamma(meas_xprofile_dose)
    # calc_plot_gamma(meas_zprofile_dose)
    #===========================================================================
    
    if data_CS.shape == data_Upsala.shape:
        data_delta = data_CS - data_Upsala
        #IDD_delta = IDD_CS - IDD_Upsala
    #plt.plot(X, C, color="blue", linewidth=2.5, linestyle="-", label="cosine")    
    plt.figure()  
    plt.plot(IDD_CS,'r--', label='IDD_CSProton')
    plt.plot(IDD_Upsala,'bo', label='IDD_Upsala')
    plt.legend(loc='best', numpoints=1, handlelength=0)      
    #plt.plot(IDD_CS, 'bo',IDD_Upsala,'r--')  # 'r--','bs','g^': red dashes, blue squares and green triangles
    plt.show()

    
    data = data_delta
    data_size = data.shape #depth, height ,width
    plot_Gaussian(data, beam_dir, 0)
    plot_Gaussian(data, beam_dir, np.round(data_size[1]/2))
    plot_Gaussian(data, beam_dir, data_size[1]-1)
    
    plt.figure()