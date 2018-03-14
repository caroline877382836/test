# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:34:46 2018

@author: CNXuaCar
"""
import numpy as np
import os
import struct
import shutil
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
from CaclStatistic import CalcStatistic
import xlwt
import time

import elekta_dvt as dvt
import elekta_dvt.model as model
import elekta_dvt.plots as dvt_plot
import elekta_dvt.dvt_io as dvt_io
import elekta_dvt.dvt_config as dvt_config
from elekta_dvt.calculators.gpumcd_calculator import GpumcdCalculator
from elekta_dvt.model import Dose3D
from elekta_dvt.evaluation.gamma_index import calculate_gamma_index_3d
from dask.dataframe.tests.test_rolling import idx

import logging
logger = logging.getLogger(__name__)
#The string that gets the current system time
mdhms=time.strftime('%Y%m%d%H%M',time.localtime(time.time()))

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
    #plt.pause(1)

def plot_idd_2(idd_CS,idd_Upsala): 
    plt.figure()
    p1=plt.subplot(111)
    p1.plot(idd_CS,'r--', label='IDD_Proton: Red')
    p1.plot(idd_Upsala,'b--', label='IDD_Upsala: blue')
    p1.legend(loc='best', numpoints=1, handlelength=1)        
    #plt.plot(idd_CS, 'bo',label = "IDD_CS",idd_Upsala,'g^',label = "IDD_Uppsala")  # 'r--','bs','g^': red dashes, blue squares and green triangles
    p2=p1.twinx()
    Differentials=[]
    if len(idd_CS) == len(idd_Upsala):
        for idx in range(0,len(idd_CS),1):
            if idd_Upsala[idx] > 0.000001 or idd_CS[idx] > 0.000001:   # for not be zero dose
                if idd_Upsala[idx] > 0.000001:
                    temp = idd_Upsala[idx]
                elif idd_CS[idx] > 0.000001:
                    temp = idd_CS[idx]
                tolerance = abs(idd_Upsala[idx] - idd_CS[idx]) / temp
                Differentials.append(tolerance )
            elif abs(idd_Upsala[idx] - idd_CS[idx]) < 0.00000001:  # for layer with zero dose
                Differentials.append(0.0) 
    p2.plot(Differentials,'g--',label=' Differentials percentage: green')
    p2.legend(loc='center right',numpoints=1, handlelength=1) 

def re_cal_dose(patient_path,exe_path,machine_path):
    args = [exe_path, patient_path, machine_path]
    subprocess.call(args)
    
def call_exe(args):
    args = args
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
    book.insert_image2Excel(raw_idx,0,"plot Dose line diff (Uppsala - CS) @ y = brag_peak, z = half_zSize ",os.path.join(cur_dir,"plotDoseXbragPeak_" + str(brag_peak_CS) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def plane_doseXZ_plot_save_insert_excel(dose_CS, book,raw_idx,brag_peak_CS, doseLabel):
    dvt_plot.plot_plane_dose_xz(dose_CS, brag_peak_CS, doseLabel) # plane_dose_plots
    pylab.savefig(doseLabel.replace(" ", ""))
    book.insert_image2Excel(raw_idx,0,"plot Dose Plane @ brag_peak",os.path.join(cur_dir,doseLabel.replace(" ", "") + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def plane_doseXY_plot_save_insert_excel(dose_CS, book,raw_idx,brag_peak_CS, doseLabel):
    dvt_plot.plot_plane_dose_xy(dose_CS, brag_peak_CS, doseLabel) # plane_dose_plots
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

def plane_diff_histXY_plot_save_insert_excel(doses, book,raw_idx,brag_peak_CS,doseLabels): 
    dvt_plot.plot_plane_diff_hist_xy(doses, brag_peak_CS, 20, doseLabels) # dose_diff_histogram
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

def removeDir(dirPath):
    if len(os.listdir(dirPath)) == 0:
        return    
    try:
        for f in os.listdir(dirPath):             
            filePath = os.path.join(dirPath, f)
            if os.path.isfile(filePath):
                os.remove(filePath)
            elif os.path.isdir(filePath):
                #removeDir(filePath)
                shutil.rmtree(filePath)
        logger.info('Cleaning up files successful') 
    except Exception, e:
        logger.error('Cleaning up files failed: Reason is: {}'.format(str(e)), exc_info=True)
        raise e

def plot_delta_sigma(del_sigma): 
    del_sigma_X = []
    del_sigma_Y = []
    for i in range(0,len(del_sigma),1):
        if (abs(del_sigma[i][0]) >= 0.0000001 or abs(del_sigma[i][1]) >= 0.0000001):
            del_sigma_X.append(del_sigma[i][0]) 
            del_sigma_Y.append(del_sigma[i][1])
    plt.figure()
    plt.plot(del_sigma_X,'r--', label='del_sigma_X: Red')
    plt.plot(del_sigma_Y,'g--', label='del_sigma_Y: Green')        
    #plt.plot(idd_CS, 'bo',label = "IDD_CS",idd_Upsala,'g^',label = "IDD_Uppsala")  # 'r--','bs','g^': red dashes, blue squares and green triangles
    plt.legend(loc='best', numpoints=1, handlelength=0) 
    #plt.show() 

def plot_idd_3(idd_CS,idd_Upsala,idd): 
    plt.figure()
    plt.plot(idd_CS,'r--', label='IDD_Proton Red')
    plt.plot(idd_Upsala,'g--', label='IDD_Upsala Green') 
    plt.plot(idd,'b--', label='IDD blue') 
    #plt.plot(idd_CS, 'bo',label = "IDD_CS",idd_Upsala,'g^',label = "IDD_Uppsala")  # 'r--','bs','g^': red dashes, blue squares and green triangles
    plt.legend(loc='best', numpoints=1, handlelength=0) 
                 
if __name__ == "__main__" :  
       
    #### setting parameters    
    BeamDirection = "height"  
    #BeamDirection = "width" 
    image_size = 24        
    
    json_config_dir = 'D:\\TestData\\practice'     
    jason_config_name = "init_config.json"
    patient_case_name = "test"
    
    try:
        init_paras = InitParameters(json_config_dir,jason_config_name)
        # get init parameters
        grid_size = init_paras.Jason_data._ini_grid_size
        min_delta_sigma_accept = init_paras.Jason_data._min_delta_sigma_accept
        ini_IDD_acceptance = init_paras.Jason_data._ini_IDD_acceptance
        ini_Dose3D_acceptance = init_paras.Jason_data._ini_Dose3D_acceptance
        min_Dose3D_acceptPerc = init_paras.Jason_data._mini_Dose3D_acceptPerc
        ini_Dose2DGaussian_acceptance = init_paras.Jason_data._ini_Dose2DGaussian_acceptance
        min_Dose2DGaussian_acceptPerc  = init_paras.Jason_data._mini_Dose2DGaussian_acceptPerc
        logger.info(jason_config_name+" file read successful")
    except Exception,e:
        logger.error('read file {}. failed: Reason is: {}'.format(jason_config_name, str(e)), exc_info=True)
        raise e 
    
    os.chdir(init_paras.Jason_data._output_path)
    cur_dir = os.getcwd() 
    removeDir(cur_dir)
    
    logging.basicConfig(level = logging.INFO,format = '%(asctime)s : %(name)s : %(levelname)s : %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=cur_dir+"\\"+mdhms+"_log",
                        filemode="w")
                
    init_paras.init_single_patient_paras(patient_case_name) 
    
    # modify Ptoton Request file
    patient_initi_cong_lst = init_paras.patient_change_condition_lst   
    try:
        # Modify proton request file
        ModifyProtonRequestFile_args = [init_paras.Jason_data._ModifyProtonRequestFile_dir,
                                    init_paras.patient_path_CS + "ProtonRequest",
                                    init_paras.patient_path_CS + "ProtonRequest"] 
        for lst_item in patient_initi_cong_lst:            
            ModifyProtonRequestFile_args.append(str(lst_item[0]))
            ModifyProtonRequestFile_args.append(str(lst_item[1])) 
            if str(lst_item[0]) == "voxelSizeX" :
                 grid_size = lst_item[1]          
                      
        call_exe(ModifyProtonRequestFile_args)      
          
        # Modify Upslala proton request file
        ModifyProtonRequestFile_args = [init_paras.Jason_data._ModifyProtonRequestFile_dir,
                                        init_paras.patient_path_Upsala + 'ProtonRequest',
                                        init_paras.patient_path_Upsala + 'ProtonRequest'] 
        for lst_item in patient_initi_cong_lst:
            ModifyProtonRequestFile_args.append(str(lst_item[0]))
            ModifyProtonRequestFile_args.append(str(lst_item[1]))
        call_exe(ModifyProtonRequestFile_args)    
        logger.info("modify CS proton request file successful for patient case: " + patient_case_name) 
    except Exception,e:
        logger.error('Modify ProtonRequest file {}. failed: Reason is: {}'.format(patient_initi_cong_lst, str(e)), exc_info=True)
        raise e

    # call ProtonScanning.exe to recal dose   
    
    re_cal_dose(init_paras.patient_path_CS,init_paras.exe_path_CS,init_paras.machine_path_CS)
    data_CS = ReadCSDose(os.path.join(init_paras.patient_path_CS,"PhysicalDose.00"))    
    
    # call UpsalaScanning.exe to recal dose
    # change Proton request file  to Upsala format: RequestCS2UppsalaConvertor
    RequestCS2UppsalaConvertor_args = [init_paras.Jason_data._RequestCS2UppsalaConvertor_dir,
                                    init_paras.patient_path_Upsala  + 'ProtonRequest',
                                    init_paras.patient_path_Upsala  +'EffectiveDensity',                                      
                                    init_paras.patient_path_Upsala  + 'RequestCS2UppsalaConvertor'] 
    call_exe(RequestCS2UppsalaConvertor_args)
    #call upsala exe
    Upsala_exe_args = [init_paras.exe_path_Upsala,
                    "ProtonPencilBeamAlgorithm",
                    init_paras.patient_path_Upsala,
                    "RequestCS2UppsalaConvertor",
                    "DoseResult"]
    call_exe(Upsala_exe_args) 
    time.sleep( 5 )
    #change Upsala dose to Proton dose format    
    ResultUppsala2CSConvertor_args = [init_paras.Jason_data._ResultUppsala2CSConvertor_dir,
                                    init_paras.patient_path_Upsala + 'DoseResult' + '.bin',
                                    str(int(data_CS.Data3D.shape[2])),
                                    str(int(data_CS.Data3D.shape[1])),
                                    str(int(data_CS.Data3D.shape[0])),
                                    init_paras.patient_path_Upsala + 'DoseResultUppsala.00']
    call_exe(ResultUppsala2CSConvertor_args) 
    #===========================================================================
    # filepath="D:/TestData/ProtonScanDose.bat"
    # p = subprocess.Popen(filepath, shell=True, stdout = subprocess.PIPE)
    # #####check if success
    # stdout, stderr = p.communicate()
    # print p.returncode  ## return 0 success
    #===========================================================================
    
    
    excel_name = strftime("%Y-%m-%d %H:%M:%S", gmtime()).replace(':', '-')     # set as current time
    book = WriteDada2Excel(excel_name + '_output.xlsx') 
    #data_CS = np.multiply(scale_Monaco2DoseEngine, data_CS.Data3D)
    
    IDD_CS = Cal_IDD(data_CS.Data3D,BeamDirection)
    brag_peak_CS = find_blagPeak(IDD_CS)    
        
    sigmas = CalcSigmaX_Y(os.path.join(init_paras.patient_path_Upsala,"DoseResultUppsala.00"),
                os.path.join(init_paras.patient_path_CS,"PhysicalDose.00"),
                grid_size)
    # calc the sigma for the whole layers 
    [benchMarch_sigma, protonCS_sigma, del_sigma] = sigmas.Get_sigmas_of_total_Layers(BeamDirection)
    
    # multi_layer_cnt = min(10,len(IDD_CS) - brag_peak_CS)
    # [benchMarch_sigma, protonCS_sigma, del_sigma] = sigmas.Get_sigmas_of_multi_Layers(BeamDirection, brag_peak_CS, 2 * multi_layer_cnt)
    
    sheet_raw_idx = book.add_sheet(patient_case_name,len(benchMarch_sigma))
    sheet_raw_idx = sheet_raw_idx  
    
    # plot_delta_sigma(del_sigma)
    # plt.savefig("del_sigma") 

    sheet_raw_idx = book.write_sigmas_2_sheet(sheet_raw_idx,benchMarch_sigma, protonCS_sigma, del_sigma)
    del_sigma_X = []
    del_sigma_Y = []
    for sigma_idx in range(0,len(del_sigma),1):
        del_sigma_X.append(del_sigma[sigma_idx][0])
        del_sigma_Y.append(del_sigma[sigma_idx][1])
    stat_deltaSigma = CalcStatistic(del_sigma_X,del_sigma_Y,min_delta_sigma_accept) 
    delta_Sigma_err_cnt, total_Sigma_valid_cnt, deltaSigma_result_percentage_passing = stat_deltaSigma.calc_delta_sigma_statistic()
    sheet_raw_idx = book.write(sheet_raw_idx, 0, delta_Sigma_err_cnt,"number of delta sigma bigger than " + str(min_delta_sigma_accept))
    sheet_raw_idx = book.write(sheet_raw_idx, 0, total_Sigma_valid_cnt,"number of total valid sigma without zero dose")
    sheet_raw_idx = book.write(sheet_raw_idx, 0, deltaSigma_result_percentage_passing,"percentage_passing: delta_Sigma_err_cnt / total_Sigma_valid_cnt")
    # sheet_raw_idx = book.insert_image2Excel(sheet_raw_idx, 0, "plot del_sigma", os.path.join(os.getcwd(),"del_sigma.png")) 
    if not np.amax(data_CS.Data3D)== 0.0:    
        # plot_idd(IDD_CS)
        # plt.savefig("IDD_CS")
        # sheet_raw_idx = book.insert_image2Excel(sheet_raw_idx, 0, "plot IDD_CS", os.path.join(os.getcwd(),"IDD_CS.png"))       
        
        data_Upsala = ReadCSDose(os.path.join(init_paras.patient_path_Upsala,"DoseResultUppsala.00"))
        IDD_Upsala = Cal_IDD(data_Upsala.Data3D,BeamDirection)    
        brag_peak_Upsala = find_blagPeak(IDD_Upsala)

        # plot_idd(IDD_Upsala)
        # pylab.savefig("IDD_Upsala")
        # sheet_raw_idx = book.insert_image2Excel(sheet_raw_idx, 0, "plot IDD_Upsala", os.path.join(os.getcwd(),"IDD_Upsala.png"))
        
        stat_idd = CalcStatistic(IDD_Upsala,IDD_CS,ini_IDD_acceptance)
        delta_idd_err_cnt, total_valid_cnt,max_diff_norm_val = stat_idd.calc_IDD_statistic()  
    
        sheet_raw_idx = book.write(sheet_raw_idx, 0, ini_IDD_acceptance,"idd acceptance tolerance value")
        sheet_raw_idx = book.write(sheet_raw_idx, 0, delta_idd_err_cnt,"error count of IDD")
        sheet_raw_idx = book.write(sheet_raw_idx, 0, total_valid_cnt,"total count of IDD without zero dose")
        sheet_raw_idx = book.write(sheet_raw_idx, 0, max_diff_norm_val,"max difference normalization value: (new_dose[i] - ref_dose[i]) / ref_dose[i]")

        plot_idd_2(IDD_CS,IDD_Upsala)
        pylab.savefig("IDD_CS_Upsala")
        sheet_raw_idx = book.insert_image2Excel(sheet_raw_idx, 0, "plot IDD_CS_Upsala", os.path.join(os.getcwd(),"IDD_CS_Upsala.png"))

        # find IDD linear fit intersection point
        intersec_point_Upsala_X, intersec_point_Upsala_Y = stat_idd.calc_IDD_polyfit_intersection_point(IDD_Upsala,brag_peak_CS, os.path.join(os.getcwd(),"IDD_linearFit_Upsala.png")) 
        intersec_point_CS_X, intersec_point_CS_Y = stat_idd.calc_IDD_polyfit_intersection_point(IDD_CS,brag_peak_CS, os.path.join(os.getcwd(),"IDD_linearFit_CS.png")) 
        sheet_raw_idx = book.write(sheet_raw_idx, 0, intersec_point_Upsala_X,"Upsala: IDD_X (pixel unit) of linear fit intersection point ")
        sheet_raw_idx = book.write(sheet_raw_idx, 0, intersec_point_Upsala_Y,"Upsala: IDD_Y of linear fit intersection point")
        sheet_raw_idx = book.write(sheet_raw_idx, 0, intersec_point_CS_X,"CS: IDD_X (pixel unit) of linear fit intersection point")
        sheet_raw_idx = book.write(sheet_raw_idx, 0, intersec_point_CS_Y,"CS: IDD_Y of linear fit intersection point")
        
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
        doses = [dose_CS, dose_Upsala]
        doseLabels = ['CS', 'Upsala'] 
        doses_diff_CS_Upsala =  re_construct2_Upsaladdata_type(data_Upsala.Data3D - data_CS.Data3D,point_grid) 
        ####plot
        if BeamDirection.lower() == "height":        
            sheet_raw_idx = line_doses_x_plot_save_insert_excel(doses_diff_CS_Upsala, book,sheet_raw_idx,brag_peak_CS,zIndex, "data_Upsala - data_CS")  # line_dose_plots,line_plots
            sheet_raw_idx = line_diff_histX_plot_save_insert_excel(doses, book,sheet_raw_idx,brag_peak_CS, zIndex,doseLabels)   
            #sheet_raw_idx = plane_doseXZ_plot_save_insert_excel(dose_CS, book,sheet_raw_idx,brag_peak_CS, doseLabel)
            sheet_raw_idx = plane_doseXZ_plot_save_insert_excel(dose_CS, book,sheet_raw_idx,brag_peak_CS, "data_CS Gaussian with brag Peak_" + str(brag_peak_CS))
            sheet_raw_idx = plane_doseXZ_plot_save_insert_excel(dose_Upsala, book,sheet_raw_idx,brag_peak_Upsala, "data_Upsala Profile with brag Peak_" + str(brag_peak_Upsala))
            if not brag_peak_CS == brag_peak_Upsala:
                sheet_raw_idx = plane_doseXZ_plot_save_insert_excel(doses_diff_CS_Upsala, book,sheet_raw_idx,brag_peak_CS, "Upsala - CS Profile with brag Peak_" + str(brag_peak_CS))
                sheet_raw_idx = plane_doseXZ_plot_save_insert_excel(doses_diff_CS_Upsala, book,sheet_raw_idx,brag_peak_Upsala, "Upsala - CS Profile with brag Peak_" + str(brag_peak_Upsala))
            else:
                
                stat_Dose2D = CalcStatistic(dose_Upsala.dose[:,brag_peak_CS,:],dose_CS.dose[:,brag_peak_CS,:],ini_Dose2DGaussian_acceptance)
                delta_err_cnt, total_valid_cnt,max_refDose,max_diff_norm_val = stat_Dose2D.calc_Dose_statistic(min_Dose2DGaussian_acceptPerc)
                sheet_raw_idx = book.write(sheet_raw_idx, 0, delta_err_cnt,"error count of Dose 2D Gaussian")
                sheet_raw_idx = book.write(sheet_raw_idx, 0, total_valid_cnt,"total count of dose bigger than max_refDose * " + str(min_Dose2DGaussian_acceptPerc))
                sheet_raw_idx = book.write(sheet_raw_idx, 0, max_refDose,"max dose of reference_dose")
                sheet_raw_idx = book.write(sheet_raw_idx, 0, max_diff_norm_val,"max difference normalization dose: abs(new_dose[i] - ref_dose[i]) / ref_dose[i]")

                sheet_raw_idx = plane_doseXZ_plot_save_insert_excel(doses_diff_CS_Upsala, book,sheet_raw_idx,brag_peak_CS, "Upsala - CS Profile with brag Peak_" + str(brag_peak_CS))
            
            sheet_raw_idx = plane_diff_histXZ_plot_save_insert_excel(doses, book,sheet_raw_idx,brag_peak_CS,doseLabels)
        elif BeamDirection.lower() == "width": # Tran plane in Monaco-x direction   
            sheet_raw_idx = line_doses_x_plot_save_insert_excel(dose_CS, book,sheet_raw_idx,yIndex,brag_peak_CS, doseLabel)  # line_dose_plots,line_plots
            if brag_peak_CS > dose_CS.z.size:
                index = zIndex
            else:
                index = brag_peak_CS
            sheet_raw_idx = plane_doseXY_plot_save_insert_excel(dose_CS, book,sheet_raw_idx,index, doseLabel)
            sheet_raw_idx = line_diff_histX_plot_save_insert_excel(doses, book,sheet_raw_idx,yIndex,brag_peak_CS, doseLabels)    
            sheet_raw_idx = plane_diff_histXY_plot_save_insert_excel(doses, book,sheet_raw_idx,brag_peak_CS,doseLabels)
            
        # calc gamma index
        delta_distance_in_mm = init_paras.patient_initi_cong_lst._Gammer_delta_distance_in_mm       #Enter tolerance distance (mm):
        delta_dose_percentage = init_paras.patient_initi_cong_lst._Gammer_delta_dose_percentage      #Enter tolerance level (%):  
        ratio_voxels_within_tolerance = init_paras.patient_initi_cong_lst._Gammer_ratio_voxels_within_tolerance  #Enter ratio of voxels to be within the tolerance for the test to pass
        search_radius = init_paras.patient_initi_cong_lst._Gammer_search_radius
        result_as_booleans = False
        gamma_result = calculate_gamma_index_3d(dose_Upsala,
                                            dose_CS, 
                                            delta_distance_in_mm, 
                                            delta_dose_percentage/100., 
                                            search_radius, 
                                            result_as_booleans,
                                            ratio_voxels_within_tolerance)
        #test_passed = gamma_result._percentage_passing
        gamma_result_count_voxels_not_satisfied = gamma_result._count_voxels_not_satisfied
        gamma_result_count_voxels_tested = gamma_result._count_voxels_tested
        gamma_result_percentage_passing = gamma_result._percentage_passing
        sheet_raw_idx = book.write(sheet_raw_idx, 0, gamma_result_count_voxels_not_satisfied,"count_voxels_not_satisfied")
        sheet_raw_idx = book.write(sheet_raw_idx, 0, gamma_result_count_voxels_tested,"count_voxels_tested")
        sheet_raw_idx = book.write(sheet_raw_idx, 0, gamma_result_percentage_passing,"percentage_passing")
            
        gamma_result_label = 'Gamma index'
        gamma_result_container = gamma_result._gamma_result_container
        gamma_result_xIndex = np.int(gamma_result_container.x.size/2)
        gamma_result_yIndex = np.int(gamma_result_container.y.size/2)
        gamma_result_zIndex = np.int(gamma_result_container.z.size/2)
        
        #dvt_plot.interact_line_gamma_index(gamma_result_container, gamma_result_label)
        sheet_raw_idx = line_gamma_indexY_plot_save_insert_excel(gamma_result_container, gamma_result_xIndex,book,sheet_raw_idx,gamma_result_label)    
        
        stat_Dose3D = CalcStatistic(dose_Upsala.dose,dose_CS.dose,ini_Dose3D_acceptance)
        delta_err_cnt, total_valid_cnt,max_refDose,max_diff_norm_val = stat_Dose3D.calc_Dose_statistic(min_Dose3D_acceptPerc)
        sheet_raw_idx = book.write(sheet_raw_idx, 0, ini_Dose3D_acceptance,"Dose acceptance tolerance")
        sheet_raw_idx = book.write(sheet_raw_idx, 0, delta_err_cnt,"error count of Dose 3D Gaussian")
        sheet_raw_idx = book.write(sheet_raw_idx, 0, total_valid_cnt,"total count of dose bigger than max_refDose * " + str(min_Dose3D_acceptPerc))
        sheet_raw_idx = book.write(sheet_raw_idx, 0, max_refDose,"max dose of reference_dose")
        sheet_raw_idx = book.write(sheet_raw_idx, 0, max_diff_norm_val,"max difference normalization dose: abs(new_dose[i] - ref_dose[i]) / ref_dose[i]")

    book.save_book()

    