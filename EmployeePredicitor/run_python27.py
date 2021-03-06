import numpy as np
import os
import struct
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

import elekta_dvt as dvt
import elekta_dvt.model as model
import elekta_dvt.plots as dvt_plot
import elekta_dvt.dvt_io as dvt_io
import elekta_dvt.dvt_config as dvt_config
from elekta_dvt.calculators.gpumcd_calculator import GpumcdCalculator
from elekta_dvt.model import Dose3D

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
 
def read3Ddose(filename):
    """
    Read and return dose grid including geometry from specified 3Ddose-file (GPUMCD output).

    Parameters
    ----------
    filename : string
        The name, including path, to the 3D dose-file.
    
    Returns
    -------
    doseContainer : Dose3D
        The doseContainer contains the dose grid as well as the x-, y- and z- coordinate vectors, all in the DICOM patient coordinate system.
        """
    floatSize = 4
    intSize = 4
    
    fileHandle = open(filename,'rb')
    doseContainer = Dose3D()
    
    width = fileHandle.read(intSize)
    width = struct.unpack('L',width)
    height = fileHandle.read(intSize)
    height = struct.unpack('L',height)
    depth = fileHandle.read(intSize)
    depth = struct.unpack('L',depth)
    
    #currentline = fileHandle.readline()  
    ndim = [int(i) for i in [width,height,depth]]
    
    # Read the voxel boundaries specified in the internal GPUMCD coordinate system
    currentline = fileHandle.readline()
    xBoundaries = [float(i) for i in currentline.split()]

    currentline = fileHandle.readline()
    yBoundaries = [float(i) for i in currentline.split()]
    
    currentline = fileHandle.readline()
    zBoundaries = [float(i) for i in currentline.split()]
    
    # Convert the geometry from the internal GPUMCD coordinate system to the DICOM patient system
   
    # x-axis in the DICOM patient system corresponds to x-axis in the GPUMCD internal coordinate system
    doseContainer.x = 10 * np.array(xBoundaries[:-1] + np.diff(xBoundaries)/2) # convert from CM to MM
    
    # y-axis in the DICOM patient system corresponds to the z-axis in GPUMCD internal coordinate system 
    doseContainer.y = 10 * np.array(zBoundaries[:-1] + np.diff(zBoundaries)/2) # convert from CM to MM

    # z-axis in the DICOM patient system corresponds to the -y-axis in GPUMCD internal coordinate system 
    doseContainer.z = np.flipud(-10 * np.array(yBoundaries[:-1] + np.diff(yBoundaries)/2)) # convert from CM to MM
   
    # Read and transform the dose stored in the internal GPUMCD coordinate system to the dose matrix in the DICOM patient system
    doseContainer.dose = np.ndarray(shape = (ndim[0], ndim[2], ndim[1]))
    doseContainer.dose.fill(0.0)

    doseContainer.dose_sigma_squared = np.ndarray(shape = (ndim[0], ndim[2], ndim[1]))
    doseContainer.dose_sigma_squared.fill(0.0)

    # Read the rest of the file contents, the dose matrix followed by the matrix of the corresponding standard deviaton, one value per row.
    doseAndStdDev = fileHandle.readlines()
    fileHandle.close()
  
    assert(len(doseAndStdDev) - 1 == 2 * ndim[0] * ndim[1] * ndim[2]) # -1 since last line is the filename

    # Fill the dose matrix from the file contents
    index = 0
    for iz in range(ndim[2]):
        for iy in range(ndim[1]):
            for ix in range(ndim[0]):
                doseContainer.dose[ix, iz, ndim[1]-iy-1] = float(doseAndStdDev[index])
                index += 1

    # Fill the variance matrix from the file contents
    for iz in range(ndim[2]):
        for iy in range(ndim[1]):
            for ix in range(ndim[0]):
                doseContainer.dose_sigma_squared[ix, iz, ndim[1]-iy-1] = float(doseAndStdDev[index])
                index += 1
  
    doseContainer.dose_sigma_squared *= doseContainer.dose * doseContainer.dose   

    return doseContainer

if __name__ == "__main__" :   
    
    #path_Upsala = 'D:\\TestData\\SingleSpot\\test_98\\IDOSELocalFiles.1'
    #path_CS = 'D:\\TestData\\SingleSpot\\test_98_Proton\\PhysicalDose.00'
    path_Upsala = 'C:\Users\Public\Documents\PTW\VeriSoft\Data\test_caro\Upsala\IDOSELocalFiles.1'
    path_CS = 'C:\Users\Public\Documents\PTW\VeriSoft\Data\test_caro\CS\PhysicalDose.00'
    
    beam_dir = "Height"    
    
    data_CS = read_binaryFile(path_CS)
    data_Upsala = read_binaryFile(path_Upsala)
    IDD_CS = Cal_IDD(data_CS,beam_dir)
    IDD_Upsala = Cal_IDD(data_Upsala,beam_dir)
    # Generate a 3D point grid from the total size [mm] and the number of voxels.
    point_grid = model.PointGrid3D.from_size(size_in_mm = [143.0,108.0,150.0], 
                                             number_of_voxels = [data_CS.shape[0], data_CS.shape[1], data_CS.shape[2]], 
                                             is_surface_at_zero = [False, False, False])
    dose = Dose3D(data_CS)
    
    dose.x = point_grid.xs
    dose.y = point_grid.ys
    dose.z = point_grid.zs
    
    xIndex = np.int(dose.x.size/2)
    yIndex = np.int(dose.y.size/2)
    zIndex = np.int(dose.z.size/2)
    doseLabel = 'Gaussian'

    dvt_plot.plot_line_doses_x(dose, 3, 80, 'Gaussian')
    dvt_plot.plot_plane_dose_xz(dose, 3, doseLabel)
    
    #read3Ddose(path_CS)
    
    meas_xprofile_dose = data_CS[:,6,:]
    #[meas_depth_dose, meas_xprofile_dose,meas_zprofile_dose]= data_CS
    calc_dose = data_Upsala
    
    dvt_plot.plot_profile_dose(meas_xprofile_dose, calc_dose, plotDifference=True, hAxisUnit='mm', vAxisUnit='Gy',
                               lineLabels=['Meas.', 'Calc.'])
    calc_plot_gamma(meas_xprofile_dose)
    
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