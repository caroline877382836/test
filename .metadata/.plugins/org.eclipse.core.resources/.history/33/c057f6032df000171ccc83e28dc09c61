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
from elekta_dvt.evaluation.gamma_index import calculate_gamma_index_3d

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

if __name__ == "__main__" :   
    path_CS = 'D:\\TestData\\SingleSpot\\test_98_Proton\\PhysicalDose.00'
    path_Upsala = 'D:\\TestData\\SingleSpot\\test_98\\IDOSELocalFiles.1'
    data_CS = read_binaryFile(path_CS)
    data_Upsala = read_binaryFile(path_Upsala)
    doseLabel = 'Gaussian'
# Generate a 3D point grid from the total size [mm] and the number of voxels.
    point_grid = model.PointGrid3D.from_size(size_in_mm = [143.0,108.0,150.0], 
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
    dvt_plot.plot_line_doses_x(dose_CS, yIndex, zIndex, doseLabel)  # line_dose_plots,line_plots
    dvt_plot.plot_plane_dose_xz(dose_CS, 3, doseLabel) # plane_dose_plots
    doses = [dose_CS, dose_Upsala]
    doseLabels = ['CS', 'Upsala']
    dvt_plot.plot_line_diff_hist_x(doses, 3, 80, 20, doseLabels)
    dvt_plot.plot_plane_diff_hist_xz(doses, 3, 20, doseLabels) # dose_diff_histogram
    # calc gamma index
    delta_distance_in_mm = 1        #Enter tolerance distance (mm):
    delta_dose_percentage = 1       #Enter tolerance level (%):  
    ratio_voxels_within_tolerance = 1  #Enter ratio of voxels to be within the tolerance for the test to pass
    search_radius = 5
    result_as_booleans = False
    gamma_result = calculate_gamma_index_3d(dose_CS,
                                        dose_Upsala, 
                                        delta_distance_in_mm, 
                                        delta_dose_percentage/100., 
                                        search_radius, 
                                        result_as_booleans)
    gamma_result_label = 'Gamma index'
    gamma_result_container = gamma_result._gamma_result_container
    gamma_result_xIndex = np.int(gamma_result_container.x.size/2)
    gamma_result_yIndex = np.int(gamma_result_container.y.size/2)
    gamma_result_zIndex = np.int(gamma_result_container.z.size/2)
    
    dvt_plot.interact_line_gamma_index(gamma_result_container, gamma_result_label)
    dvt_plot.plot_line_gamma_index_y(gamma_result_container, gamma_result_xIndex, gamma_result_zIndex, gamma_result_label)

    