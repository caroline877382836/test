# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:34:46 2018
@author: CNXuaCar
This doc is used to test single patient case, need to specify the patient_case_name
"""
import numpy as np
import os
import struct
import shutil
import pylab
import matplotlib.pyplot as plt
import subprocess
import collections

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

def plot_idd_2_c(idd_CS,idd_Upsala): 
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

def line_doses_x_plot_save_insert_excel(dose_test, book,raw_idx,brag_peak_test,zIndex, doseLabel,cur_dir):  
    dvt_plot.plot_line_doses_x(dose_test, brag_peak_test, zIndex, doseLabel)  # line_dose_plots,line_plots
    plt.savefig(cur_dir +'\\' + "plotDoseXbragPeak_" + str(brag_peak_test) + ".png")
    plt.pause(1)
    plt.close()
    msg = ' 1D lateral profile difference @ y= brag_peak:' + str(brag_peak_test) + ', z=' + str(zIndex)
    book.insert_image2Excel(raw_idx ,8,msg ,
                            os.path.join(cur_dir,"plotDoseXbragPeak_" + str(brag_peak_test) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def plane_doseXZ_plot_save_insert_excel(dose_test, book,raw_idx,brag_peak_test, doseLabel,cur_dir):
    dvt_plot.plot_plane_dose_xz(dose_test, brag_peak_test, doseLabel) # plane_dose_plots
    plt.savefig(cur_dir +'\\' + doseLabel.replace(" ", "") + ".png")
    plt.pause(1)
    plt.close()
    msg = ' '
    book.insert_image2Excel(raw_idx, 8, msg,
                            os.path.join(cur_dir,doseLabel.replace(" ", "") + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def plane_doseXY_plot_save_insert_excel(dose_test, book,raw_idx,brag_peak_test, doseLabel,cur_dir):
    dvt_plot.plot_plane_dose_xy(dose_test, brag_peak_test, doseLabel) # plane_dose_plots
    plt.savefig(cur_dir +'\\' + "plotDosePlaneXYBragPeak_" + str(brag_peak_test)+ ".png")
    plt.pause(1)
    plt.close()
    msg = ' '
    book.insert_image2Excel(raw_idx,8, msg,
                            os.path.join(cur_dir,"plotDosePlaneXYBragPeak_" + str(brag_peak_test) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx
    
def line_diff_histX_plot_save_insert_excel(doses, book,raw_idx,brag_peak_test, zIndex,doseLabels,cur_dir): #
    dvt_plot.plot_line_diff_hist_x(doses, brag_peak_test, zIndex, 20, doseLabels)
    plt.savefig(cur_dir +'\\' + "plotDoseDiffLineXBragPeak_" + str(brag_peak_test)+ ".png")
    plt.pause(1)
    plt.close()
    msg = ' 1D lateral profile difference @ y= brag_peak:' + str(brag_peak_test) + ', z=' + str(zIndex)   
    book.insert_image2Excel(raw_idx,8,msg,
                            os.path.join(cur_dir,"plotDoseDiffLineXBragPeak_" + str(brag_peak_test) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def plane_diff_histXZ_plot_save_insert_excel(doses, book,raw_idx,brag_peak_test,doseLabels,cur_dir): 
    dvt_plot.plot_plane_diff_hist_xz(doses, brag_peak_test, 20, doseLabels) # dose_diff_histogram
    plt.savefig(cur_dir +'\\' + "plotPlaneDiffBrag_peak_" + str(brag_peak_test)+ ".png")
    plt.pause(1)
    plt.close()
    msg = ' 2D lateral profile difference @ brag_peak:' + str(brag_peak_test)
    book.insert_image2Excel(raw_idx,8,msg,
                            os.path.join(cur_dir,"plotPlaneDiffBrag_peak_" + str(brag_peak_test) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def plane_diff_histXY_plot_save_insert_excel(doses, book,raw_idx,brag_peak_test,doseLabels,cur_dir): 
    dvt_plot.plot_plane_diff_hist_xy(doses, brag_peak_test, 20, doseLabels) # dose_diff_histogram
    plt.savefig(cur_dir +'\\' + "plotPlaneDiffBrag_peak_" + str(brag_peak_test)+ ".png")
    plt.pause(1)
    plt.close()
    book.insert_image2Excel(raw_idx,8,"plot dose plane Diff",
                            os.path.join(cur_dir,"plotPlaneDiffBrag_peak_" + str(brag_peak_test) + ".png"))
    raw_idx = raw_idx + image_size
    return raw_idx

def line_gamma_indexY_plot_save_insert_excel(gamma_result_container, gamma_result_xIndex,book,raw_idx,gamma_result_label,cur_dir):
    dvt_plot.plot_line_gamma_index_y(gamma_result_container, gamma_result_xIndex, gamma_result_zIndex, gamma_result_label)
    plt.savefig(cur_dir +'\\' + "plotGammerResult.png")
    plt.pause(1)
    plt.close()
    msg = ' Gammer Index line @ x= :' + str(gamma_result_xIndex) + ', z=' + str(gamma_result_zIndex)
    book.insert_image2Excel(raw_idx, 8, msg,
                            os.path.join(cur_dir,"plotGammerResult" + ".png"))
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

def find_idd_diffs(IDD_test,IDD_BenchMark):
    Rel_Differentials=[] 
    abs_Differentials=[]   
    max_dif = 0.0
    max_idx = 0
    max_CS = 0.0
    max_Upsala = 0.0
    if len(IDD_test) == len(IDD_BenchMark):
        for idx in range(0,len(IDD_test),1):
            temp = abs(IDD_BenchMark[idx] - IDD_test[idx])
            abs_Differentials.append(temp)
            if IDD_BenchMark[idx] > 0.0 or IDD_test[idx] > 0.0:   # for not be zero dose
                if IDD_BenchMark[idx] > 0.0:
                    temp = IDD_BenchMark[idx]
                elif IDD_test[idx] > 0.0:
                    temp = IDD_test[idx]
                tolerance = abs(IDD_BenchMark[idx] - IDD_test[idx]) / temp                
                if tolerance > max_dif:
                    max_dif = tolerance
                    max_idx = idx
                    max_CS = IDD_test[idx]
                    max_Upsala = IDD_BenchMark[idx]
                Rel_Differentials.append(tolerance )
            else:  # for layer with zero dose
                Rel_Differentials.append(0.0) 
    return Rel_Differentials,max_idx,max_CS,max_Upsala,abs_Differentials

def plot_idd_2(IDD_test,IDD_BenchMark,idd_path_name,idd_diffs,label_name): 
    if label_name == ' Relative difference (%)':   
        idd_diffs_new = [i * 100 for i in idd_diffs]  #change to % unit
    else:
        idd_diffs_new = idd_diffs
    plt.figure()
    p1=plt.subplot(111)
    p1.plot(IDD_test,'r--', label='IDD_test')
    p1.plot(IDD_BenchMark,'b--', label='IDD_BenchMark')
    p1.legend(loc='best', numpoints=1, handlelength=1)        
    #plt.plot(IDD_test, 'bo',label = "IDD_test",IDD_BenchMark,'g^',label = "IDD_Uppsala")  # 'r--','bs','g^': red dashes, blue squares and green triangles
    p2=p1.twinx()    
    p2.plot(idd_diffs_new,'g--',label=label_name)
    min_ylim = np.mean(idd_diffs_new) - np.std(idd_diffs_new)
    max_ylim = np.mean(idd_diffs_new) + np.std(idd_diffs_new)
    p2.set_ylim(min_ylim, max_ylim)
    p2.legend(loc='center right',numpoints=1, handlelength=1)
    plt.savefig(idd_path_name)
    plt.close()  

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
    jason_config_name = "init_config_test.json"
    patient_case_name = "18"
    
    try:
        init_paras = InitParameters(json_config_dir,jason_config_name)
        # get init parameters
         # get init parameters
        grid_size = init_paras.Jason_data._ini_grid_size
        err_delta_sigma_acceptance = init_paras.Jason_data._err_delta_sigma_acceptance
        min_delta_sigma_acceptPerc = init_paras.Jason_data._min_delta_sigma_acceptPerc
        err_IDD_acceptance = init_paras.Jason_data._err_IDD_acceptance
        min_IDD_acceptPerc = init_paras.Jason_data._min_IDD_acceptPerc
        err_Dose1D_acceptance = init_paras.Jason_data._err_Dose1D_acceptance
        min_Dose1D_acceptPerc = init_paras.Jason_data._min_Dose1D_acceptPerc
        err_Dose3D_acceptance = init_paras.Jason_data._err_Dose3D_acceptance
        min_Dose3D_acceptPerc = init_paras.Jason_data._min_Dose3D_acceptPerc
        err_Dose2DGaussian_acceptance = init_paras.Jason_data._err_Dose2DGaussian_acceptance
        min_Dose2DGaussian_acceptPerc  = init_paras.Jason_data._min_Dose2DGaussian_acceptPerc
        logger.info(jason_config_name + " Json file read successful")
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
    excel_name = mdhms
    try:     # set as current time
        book = WriteDada2Excel(excel_name + '_output.xlsx')
        logger.info("a new xls file with name "+excel_name + '_output.xlsx'+" create successful")
    except Exception,e:
        logger.error('create file {}. failed: Reason is: {}'.format(excel_name + '_output.xlsx', str(e)), exc_info=True)
        raise e
    font_color=book.change_font('red')
    font=book.format()
    number_change=0

    init_paras.init_single_patient_paras(patient_case_name) 
    
    # modify Ptoton Request file
    patient_initi_cong_lst = init_paras.patient_change_condition_lst   
    # modify Ptoton Request file   
    patient_change_cong_lst = init_paras.patient_change_condition_lst 
    patient_config_lst = init_paras.patient_initi_cong_lst
    if len(patient_change_cong_lst) > 0:
        ModifyProtonRequestFile_args = [init_paras.Jason_data._ModifyProtonRequestFile_dir,
                                        init_paras.patient_path_test +  "ProtonRequest",
                                        init_paras.patient_path_test +  "ProtonRequest"]
        for lst_item in patient_change_cong_lst:
                ModifyProtonRequestFile_args.append(str(lst_item[0]))
                ModifyProtonRequestFile_args.append(str(lst_item[1]))
                if str(lst_item[0]) == "voxelSizeX" :  # change Grid Size
                    grid_size = lst_item[1] 
        try:
            change_content=[]
            change_content=ModifyProtonRequestFile_args[3:]
            call_exe(ModifyProtonRequestFile_args)
            time.sleep(5) 
            logger.info("modify CS proton request file successful for patient case: " + patient_case_name) 
        except Exception,e:
            logger.error('modify CS proton request file failed for patient case: {}, Reason is: {}'.format(patient_case_name,str(e)), exc_info=True)
            raise e
        
        # Modify Upslala proton request file
        ModifyProtonRequestFile_args = [init_paras.Jason_data._ModifyProtonRequestFile_dir,
                                        init_paras.patient_path_benchMark +  "ProtonRequest",
                                        init_paras.patient_path_benchMark +  "ProtonRequest",] 
        
        for lst_item in patient_change_cong_lst:
                ModifyProtonRequestFile_args.append(str(lst_item[0]))
                ModifyProtonRequestFile_args.append(str(lst_item[1]))
        try:
            call_exe(ModifyProtonRequestFile_args)
            time.sleep(5) 
            logger.info("modify Upslala proton request file successful for patient case: " + patient_case_name) 
        except Exception,e:
            logger.error('modify Upslala proton request file failed for patient case: {}, Reason is: {}'.format(patient_case_name,str(e)), exc_info=True)
            raise e      
    else:               
        try:
            change_content=[]
            logger.info("Not modify CS and uppsala proton request file for patient case: " + patient_case_name) 
        except Exception,e:
            logger.error(' {}, Reason is: {}'.format(patient_case_name,str(e)), exc_info=True)
            raise e

    # call ProtonScanning.exe to recal dose  
    try: 
        re_cal_dose(init_paras.patient_path_test,init_paras.exe_path_test,init_paras.machine_path_test)
        time.sleep(5)
        #os.path.join(init_paras.patient_path_test,"PhysicalDose.00")
        data_test = ReadCSDose(os.path.join(init_paras.patient_path_test,"PhysicalDose.00")) 
        logger.info("call ProtonScanning.exe to recal dose sucessful") 
    except Exception,e:
        logger.error('call ProtonScanning.exe to recal dose failed: Reason is: {}'.format(str(e)), exc_info=True)
        raise e
    
    benchMark_path = init_paras.exe_path_benchMark.upper()
    if 'UPPSALA' in benchMark_path:
        # change Proton request file  to Upsala format: RequestCS2BenchMarkConvertor
        RequestCS2UppsalaConvertor_args = [init_paras.Jason_data._RequestCS2UppsalaConvertor_dir,
                                        init_paras.patient_path_benchMark + "ProtonRequest",
                                        init_paras.patient_path_benchMark + "EffectiveDensity",                                      
                                        init_paras.patient_path_benchMark + "RequestCS2UppsalaConvertor"] 
        try:                                  
            call_exe(RequestCS2UppsalaConvertor_args)
            time.sleep(5) 
            logger.info("change Proton request file  to Upsala format successful")
        except Exception,e:
            logger.error('change Proton request file to Upsala format failed: Reason is: {}'.format(str(e)), exc_info=True)
            raise e
        #call upsala exe
        Upsala_exe_args = [init_paras.exe_path_benchMark,
                        "ProtonPencilBeamAlgorithm",
                        init_paras.patient_path_benchMark,
                        "RequestCS2UppsalaConvertor",
                        "DoseResult"]
        try:
            call_exe(Upsala_exe_args)
            time.sleep(5) 
            logger.info("call upsala exe successful")
        except Exception,e:
            logger.error('call upsala exe failed: Reason is: {}'.format(str(e)), exc_info=True)
            raise e
        #change Upsala dose to Proton dose format    
        ResultUppsala2CSConvertor_args = [init_paras.Jason_data._ResultUppsala2CSConvertor_dir,
                                        init_paras.patient_path_benchMark + 'DoseResult' + '.bin',
                                        str(int(data_test.Data3D.shape[2])),
                                        str(int(data_test.Data3D.shape[1])),
                                        str(int(data_test.Data3D.shape[0])),
                                        init_paras.patient_path_benchMark + 'DoseResultUppsala.00']
        try:                                  
            call_exe(ResultUppsala2CSConvertor_args) 
            time.sleep(5) 
            logger.info("change Upsala dose to Proton dose format successful")
        except Exception,e:
            logger.error('change Upsala dose to Proton dose format failed: Reason is: {}'.format(str(e)), exc_info=True)
            raise e                                 
    
    #data_test = np.multiply(scale_Monaco2DoseEngine, data_test.Data3D)
    else:
        # call ProtonScanning.exe to recal dose  
        try:
            exe_path_benchMark = init_paras.exe_path_benchMark
            exe_path_benchMark = exe_path_benchMark.replace('ProtonPencilBeamExecutable.exe','ProtonScanning.exe') 
            re_cal_dose(init_paras.patient_path_benchMark,exe_path_benchMark,init_paras.machine_path_test)
            time.sleep(5) 
            #os.path.join(init_paras.patient_path_test,"PhysicalDose.00")            
            logger.info("call ProtonScanning.exe to recal dose sucessful") 
        except Exception,e:
            logger.error('call ProtonScanning.exe to recal dose failed: Reason is: {}'.format(str(e)), exc_info=True)
            raise e

    IDD_test = Cal_IDD(data_test.Data3D,BeamDirection)
    brag_peak_test = find_blagPeak(IDD_test)
    
    if 'UPPSALA' in benchMark_path:    
        sigmas = CalcSigmaX_Y(os.path.join(init_paras.patient_path_benchMark,"DoseResultUppsala.00"),
                    os.path.join(init_paras.patient_path_test,"PhysicalDose.00"),
                    grid_size)
    else:
        sigmas = CalcSigmaX_Y(os.path.join(init_paras.patient_path_benchMark,"PhysicalDose.00"),
                    os.path.join(init_paras.patient_path_test,"PhysicalDose.00"),
                    grid_size) 
    # calc the sigma for the whole layers 
    #[benchMarch_sigma_total, test_sigma_total, del_sigma_total] = sigmas.Get_sigmas_of_total_Layers(BeamDirection)

    # calc the sigma for the layers : 0.8*brag_peak_idx ---  1.2* brag_peak_idx
    [benchMarch_sigma, test_sigma, del_sigma,del_sigma_total] = sigmas.Get_sigmas_of_80Perc_layers(BeamDirection,brag_peak_test,IDD_test) 
    
    # [benchMarch_sigma, test_sigma, del_sigma] = sigmas.Get_sigmas_of_multi_Layers_avoid_transgression(BeamDirection, brag_peak_test,len(IDD_test),20)    
      
    sheet_raw_idx = book.add_sheet(patient_case_name,len(benchMarch_sigma))
    sheet_raw_idx = sheet_raw_idx
    result_raw_idx = sheet_raw_idx
    image_raw_idx = 31
    Analysis_results = dict()
    #write patient case detail infor to sheet
    try:
        patient_case_content=collections.OrderedDict
        patient_case_content=init_paras.Jason_data._patients_config_lst[0][1]
        #sheet_raw_idx = book.write_single(sheet_raw_idx+1,3,"Patient testing conditions Infor:")
        sheet_raw_idx=book.write(sheet_raw_idx,0,"case_name",patient_case_name)
             
        sheet_raw_idx=book.write(sheet_raw_idx,0,"BenchMark_exe",  \
                            os.path.join(init_paras.Jason_data._benchMark_exe_root, patient_config_lst._BenchMark_exe_name))
        sheet_raw_idx=book.write(sheet_raw_idx,0,"test_exe", \
                            os.path.join(init_paras.Jason_data._test_exe_root, patient_config_lst._test_exe_name))
        sheet_raw_idx=book.write(sheet_raw_idx,0,"ED_file_name", \
                            os.path.join(init_paras.Jason_data._ED_temp_dir, patient_config_lst._ED_file_name))
        
        # write beam model parameters
        sheet_raw_idx = book.write_beam_model_paras_2_sheet(sheet_raw_idx)
          
        # read proton request file, write to sheet
        proton_request_contents = book.read_proton_request_file(os.path.join(init_paras.patient_path_test,"ProtonRequest"))
        
        sheet_raw_idx = book.write_request_paras_2_sheet(sheet_raw_idx,proton_request_contents,patient_change_cong_lst)

        # write init acceptance tolerance
        sheet_raw_idx = book.write_single(sheet_raw_idx,0,"Threshold tolerance")
        sheet_raw_idx=book.write(sheet_raw_idx - 1,1, "sigma_diff_thre", err_delta_sigma_acceptance)
        sheet_raw_idx=book.write(sheet_raw_idx,1, "idd_relative_diff_thre", err_IDD_acceptance)        
        sheet_raw_idx=book.write(sheet_raw_idx,1, "lateral_2D_profile_diff_thre", err_Dose2DGaussian_acceptance)
        sheet_raw_idx=book.write(sheet_raw_idx,1, "lateral_3D_profile_diff_thre", err_Dose3D_acceptance)
        # write gama index config
        sheet_raw_idx = book.write_single(sheet_raw_idx,0,"gamma index parameters")
        sheet_raw_idx=book.write(sheet_raw_idx-1,1, "maxdose_upper", patient_config_lst._dose_diff_config_maxdose_lower)
        sheet_raw_idx=book.write(sheet_raw_idx,1, "maxdose_lower", patient_config_lst._dose_diff_config_maxdose_upper)
        sheet_raw_idx=book.write(sheet_raw_idx,1, "normalize_to_sum", patient_config_lst._dose_diff_config_normalize_to_sum)
        sheet_raw_idx=book.write(sheet_raw_idx,1, "search_radius", patient_config_lst._Gammer_search_radius)
        sheet_raw_idx=book.write(sheet_raw_idx,1, "ratio_voxels_within_tolerance", patient_config_lst._Gammer_ratio_voxels_within_tolerance)
        sheet_raw_idx=book.write(sheet_raw_idx,1, "delta_dose_percentage", patient_config_lst._Gammer_delta_dose_percentage)
        sheet_raw_idx=book.write(sheet_raw_idx,1, "delta_distance_in_mm", patient_config_lst._Gammer_delta_distance_in_mm)      
        logger.info("write patient case contents to sheet successful")
    except Exception,e:
        logger.error('write patient case content to sheet failed: Reason is: {}'.format(str(e)), exc_info=True)
        raise e  
# write sigma statistics
    del_sigma_X = []
    del_sigma_Y = []
    for sigma_idx in range(0,len(del_sigma_total),1):
        del_sigma_X.append(del_sigma_total[sigma_idx][0])
        del_sigma_Y.append(del_sigma_total[sigma_idx][1])
    stat_deltaSigma = CalcStatistic(del_sigma_X,del_sigma_Y,err_delta_sigma_acceptance) 
    delta_Sigma_err_cnt, total_Sigma_valid_cnt, deltaSigma_result_percentage_NOpassing,deltaSigma_max_diff_norm_val = stat_deltaSigma.calc_delta_sigma_statistic(min_delta_sigma_acceptPerc)
    Analysis_results.update({ "Delta Sigma Analysis Result": {
                                                 "number of failed slices:": delta_Sigma_err_cnt, \
                                                 "number of total slices: not only non-zero:" : total_Sigma_valid_cnt, \
                                                 "percentage_err(%):": deltaSigma_result_percentage_NOpassing,
                                                 "max difference(%):": deltaSigma_max_diff_norm_val }})
    image_column_idx = 8
    image_raw_idx = book.write_single(image_raw_idx + 2,8,"Delta Sigma Statistic Infor:")
    image_raw_idx = book.write(image_raw_idx, image_column_idx, "number of failed slices:",delta_Sigma_err_cnt)
    image_raw_idx = book.write(image_raw_idx, image_column_idx, "number of total slices:", total_Sigma_valid_cnt)    
    image_raw_idx = book.write(image_raw_idx, image_column_idx, "percentage_err(%):", deltaSigma_result_percentage_NOpassing)
    image_raw_idx = book.write(image_raw_idx, image_column_idx,"max difference(%):", deltaSigma_max_diff_norm_val)
    # write detail sigma values   
    image_raw_idx = book.write_sigmas_2_sheet(image_raw_idx + 1,image_column_idx,benchMarch_sigma, test_sigma, del_sigma,0.001)
    
    if 'UPPSALA' in benchMark_path:
        data_benchMark = ReadCSDose(os.path.join(init_paras.patient_path_benchMark,"DoseResultUppsala.00"))
    else:
        data_benchMark = ReadCSDose(os.path.join(init_paras.patient_path_benchMark,"PhysicalDose.00")) 
    IDD_BenchMark = Cal_IDD(data_benchMark.Data3D,BeamDirection)    
    brag_peak_BenchMark = find_blagPeak(IDD_BenchMark)

    stat_idd = CalcStatistic(IDD_BenchMark,IDD_test,err_IDD_acceptance)
    delta_idd_err_cnt, idd_total_valid_cnt,max_diff_norm_val_idd = stat_idd.calc_IDD_statistic(min_IDD_acceptPerc)

    rel_Differentials,max_idx,max_CS,max_Upsala,abs_Differentials = find_idd_diffs(IDD_test,IDD_BenchMark)
    plot_idd_2(IDD_test,IDD_BenchMark,
                os.path.join(init_paras.output_path + '\\' + patient_case_name,"relaDiff_IDD_test_benchMark.png"),
                rel_Differentials,
                ' Relative difference (%)')
    plot_idd_2(IDD_test,IDD_BenchMark,
                os.path.join(init_paras.output_path + '\\' + patient_case_name,"absDiff_IDD_test_benchMark.png"),
                abs_Differentials,
                ' absolute difference')
        # find IDD linear fit intersection point, write to excel
    try:
        intersec_point_benchMark_X, intersec_point_benchMark_Y = stat_idd.calc_IDD_polyfit_intersection_point(IDD_BenchMark,brag_peak_test, \
                                                            os.path.join(init_paras.output_path + '\\' + patient_case_name,"IDD_linearFit_BenchMark.png")) 
        intersec_point_test_X, intersec_point_test_Y = stat_idd.calc_IDD_polyfit_intersection_point(IDD_test,brag_peak_test, \
                                                            os.path.join(init_paras.output_path + '\\' + patient_case_name,"IDD_linearFit_test.png")) 
        if not idd_total_valid_cnt == 0:
            idd_percentage_err = round(100*(float(delta_idd_err_cnt)/float(idd_total_valid_cnt)),2) 
        else:
            idd_percentage_err = 100

        Analysis_results["IDD Analysis Result"] = { "number of failed points:" : delta_idd_err_cnt, \
                                                    "number of total points:": idd_total_valid_cnt, \
                                                    "percentage_err(%):": idd_percentage_err, \
                                                    "max difference(%):": max_diff_norm_val_idd , \
                                                    "max difference @ (pixel unit): ": max_idx , \
                                                    "IDD_test value at max difference:": max_CS , \
                                                    "IDD_BenchMark value at max difference:": max_Upsala }

        Analysis_results["IDD linear fitting Analysis Result"] = {"Benchmark: Bragg Peak position (pixel unit):":intersec_point_benchMark_X, \
                                                "Benchmark: Bragg Peak height:": intersec_point_benchMark_Y,  \
                                                "Test: Bragg Peak position (pixel unit):": intersec_point_test_X, \
                                                "Test: Bragg Peak height:": intersec_point_test_Y }

        image_raw_idx = book.write_single(image_raw_idx+1,image_column_idx,"IDD statistic Info")
        image_raw_idx = book.write(image_raw_idx , image_column_idx," number of failed points:" ,delta_idd_err_cnt)
        image_raw_idx = book.write(image_raw_idx , image_column_idx," number of total points:", idd_total_valid_cnt)
        image_raw_idx = book.write(image_raw_idx , image_column_idx, "percentage_err(%)", idd_percentage_err)
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"max difference(%)", max_diff_norm_val_idd)
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"max difference @ (pixel unit) ", max_idx)
        image_raw_idx = book.write(image_raw_idx, image_column_idx," IDD_test value at max difference: ", max_CS)
        image_raw_idx = book.write(image_raw_idx, image_column_idx," IDD_BenchMark value at max difference: ", max_Upsala)
        # brag peak intersection point
        image_raw_idx = book.write_single(image_raw_idx+1, image_column_idx, "Bragg Peak position by linear fitting ")
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"Benchmark: Bragg Peak position (pixel unit)", intersec_point_benchMark_X)
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"Benchmark: Bragg Peak height", intersec_point_benchMark_Y)
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"Test: Bragg Peak position (pixel unit)", intersec_point_test_X)
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"Test: Bragg Peak height", intersec_point_test_Y)
    except Exception,e:
        logger.error('Linear fit IDD failed: Reason is: {}'.format(str(e)), exc_info=True)
        logger.info('Check whether the idx of bragPeak is zero OR the last ')
        raise e  
    finally:
        pass
    # inset IDD image    
    try:
        image_raw_idx = book.insert_image2Excel(image_raw_idx + 1, image_column_idx, "Figure: relative diff IDD_test_benchMark",
                                                os.path.join(init_paras.output_path + '\\' + patient_case_name,"relaDiff_IDD_test_benchMark.png"))
        image_raw_idx = book.insert_image2Excel(image_raw_idx + 1, image_column_idx, "Figure: absolute diff IDD_test_benchMark",
                                                os.path.join(init_paras.output_path + '\\' + patient_case_name,"absDiff_IDD_test_benchMark.png"))

        logger.info("create image and insert it to the sheet successful")
    except Exception,e:
        logger.error('create image and insert it to the sheet failed: Reason is: {}'.format(str(e)), exc_info=True)
        raise e      
    
    size_in_mm = [grid_size * data_test.Data3D.shape[0], 
                  grid_size * data_test.Data3D.shape[1],
                  grid_size * data_test.Data3D.shape[2]]
    doseLabel = 'Gaussian'
# Generate a 3D point grid from the total size [mm] and the number of voxels.
    point_grid = model.PointGrid3D.from_size(size_in_mm , 
                                             number_of_voxels = [data_test.Data3D.shape[0], data_test.Data3D.shape[1], data_test.Data3D.shape[2]], 
                                             is_surface_at_zero = [False, False, False])
    
    dose_test = re_construct2_Upsaladdata_type(data_test.Data3D,point_grid)    
    dose_BenchMark = re_construct2_Upsaladdata_type(data_benchMark.Data3D,point_grid) 
    
    xIndex = np.int(dose_test.x.size/2)
    yIndex = np.int(dose_test.y.size/2)
    zIndex = np.int(dose_test.z.size/2) 
    doses = [dose_test, dose_BenchMark]
    doseLabels = ['test', 'BenchMark'] 
    doses_diff_test_BenchMark =  re_construct2_Upsaladdata_type(data_benchMark.Data3D - data_test.Data3D,point_grid) 
    ####plot
    if BeamDirection.lower() == "height":        
        image_raw_idx = line_doses_x_plot_save_insert_excel(doses_diff_test_BenchMark, book,image_raw_idx +2,brag_peak_test,zIndex, "data_benchMark - data_test",
                                                            os.path.join(init_paras.output_path , patient_case_name))  # line_dose_plots,line_plots
        image_raw_idx = line_diff_histX_plot_save_insert_excel(doses, book,image_raw_idx+2,brag_peak_test, zIndex,doseLabels,
                                                               os.path.join(init_paras.output_path , patient_case_name))  
        # write 1D dose statistic         
        stat_Dose1D = CalcStatistic(dose_BenchMark.dose[:,brag_peak_test,zIndex],dose_test.dose[:,brag_peak_test,zIndex],err_Dose1D_acceptance)
        Dose1D_delta_err_cnt, Dose1D_total_valid_cnt,Dose1D_max_refDose,Dose1D_max_diff_norm_val = stat_Dose1D.calc_Dose_statistic(min_Dose1D_acceptPerc)
        if not Dose1D_total_valid_cnt== 0:
            Dose1D_percentage_err = round(100*(float(Dose1D_delta_err_cnt)/float(Dose1D_total_valid_cnt)),2) 
        else:
            Dose1D_percentage_err = 100

        Analysis_results["Lateral 1D Profile Analysis Result"] = {"number of failed points:": Dose1D_delta_err_cnt, \
                                            "number of total points:": Dose1D_total_valid_cnt, \
                                            "percentage_err(%):": Dose1D_percentage_err, \
                                            "max difference(%):": Dose1D_max_diff_norm_val}

        image_raw_idx = book.write_single(image_raw_idx+1,image_column_idx,"Dose 1D Profile statistic Info:")
        image_raw_idx = book.write(image_raw_idx, image_column_idx," threshold tolerance",err_Dose1D_acceptance )
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"max dose of benchMark", Dose1D_max_refDose)
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"number of failed points:", Dose1D_delta_err_cnt)
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"number of total points:", Dose1D_total_valid_cnt)
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"percentage_err(%)", Dose1D_percentage_err)            
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"max difference(%)", Dose1D_max_diff_norm_val)                                                     
        #image_raw_idx = plane_doseXZ_plot_save_insert_excel(dose_test, book,image_raw_idx,brag_peak_test, doseLabel)
        image_raw_idx = plane_doseXZ_plot_save_insert_excel(dose_test, book,image_raw_idx+2,brag_peak_test, "dose_test 2D lateral Profile with brag Peak_ " + str(brag_peak_test),
                                                            os.path.join(init_paras.output_path , patient_case_name))
        image_raw_idx = plane_doseXZ_plot_save_insert_excel(dose_BenchMark, book,image_raw_idx+2,brag_peak_BenchMark, "dose_benchMark 2D lateral Profile with brag Peak_" + str(brag_peak_BenchMark),
                                                            os.path.join(init_paras.output_path , patient_case_name))
        if not brag_peak_test == brag_peak_BenchMark:
            image_raw_idx = plane_doseXZ_plot_save_insert_excel(doses_diff_test_BenchMark, book,image_raw_idx + 2,brag_peak_test, "2D lateral Profile difference with brag Peak_" + str(brag_peak_test),
                                                                os.path.join(init_paras.output_path , patient_case_name))
            image_raw_idx = plane_doseXZ_plot_save_insert_excel(doses_diff_test_BenchMark, book,image_raw_idx+2,brag_peak_BenchMark, "2D lateral Profile difference with brag Peak_" + str(brag_peak_BenchMark),
                                                                os.path.join(init_paras.output_path , patient_case_name))
        else:
            image_raw_idx = plane_doseXZ_plot_save_insert_excel(doses_diff_test_BenchMark, book,image_raw_idx+2,brag_peak_test, "2D lateral Profile difference with brag Peak_" + str(brag_peak_test),
                                                                os.path.join(init_paras.output_path , patient_case_name))
        # write Gaussian dose statistics
        stat_Dose2D = CalcStatistic(dose_BenchMark.dose[:,brag_peak_test,:],dose_test.dose[:,brag_peak_test,:],err_Dose2DGaussian_acceptance)
        dose2D_delta_err_cnt, dose2D_total_valid_cnt,dose2D_max_refDose,dose2D_max_diff_norm_val = stat_Dose2D.calc_Dose_statistic(min_Dose2DGaussian_acceptPerc)
        if not dose2D_total_valid_cnt == 0:
            Dose2D_percentage_err = round(100*(float(dose2D_delta_err_cnt)/float(dose2D_total_valid_cnt)),2) 
        else:
            Dose2D_percentage_err = 100

        Analysis_results["Lateral 2D Profile Analysis Result"] = {"number of failed points:": dose2D_delta_err_cnt, \
                                            "number of total points:": dose2D_total_valid_cnt, \
                                            "percentage_err(%):": Dose2D_percentage_err, \
                                            "max difference(%):": dose2D_max_diff_norm_val}

        image_raw_idx = book.write_single(image_raw_idx+1,image_column_idx,"Dose 2D Gaussian statistic Info:")
        image_raw_idx = book.write(image_raw_idx, image_column_idx," threshold tolerance", err_Dose2DGaussian_acceptance)
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"max dose of benchMark", dose2D_max_refDose)
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"number of failed points:", dose2D_delta_err_cnt)
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"number of total points:", dose2D_total_valid_cnt)
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"percentage_err(%)", Dose2D_percentage_err)            
        image_raw_idx = book.write(image_raw_idx, image_column_idx,"max difference(%)", dose2D_max_diff_norm_val)

        image_raw_idx = plane_diff_histXZ_plot_save_insert_excel(doses, book,image_raw_idx + 1,brag_peak_test,doseLabels,
                                                                 os.path.join(init_paras.output_path , patient_case_name))
    elif BeamDirection.lower() == "width": # Tran plane in Monaco-x direction   
        image_raw_idx = line_doses_x_plot_save_insert_excel(dose_test, book,image_raw_idx,yIndex,brag_peak_test, doseLabel,
                                                            os.path.join(init_paras.output_path , patient_case_name))  # line_dose_plots,line_plots
        if brag_peak_test > dose_test.z.size:
            index = zIndex
        else:
            index = brag_peak_test
        image_raw_idx = plane_doseXY_plot_save_insert_excel(dose_test, book,image_raw_idx,index, doseLabel,
                                                            os.path.join(init_paras.output_path , patient_case_name))
        image_raw_idx = line_diff_histX_plot_save_insert_excel(doses, book,image_raw_idx,yIndex,brag_peak_test, doseLabels,
                                                               os.path.join(init_paras.output_path , patient_case_name))    
        image_raw_idx = plane_diff_histXY_plot_save_insert_excel(doses, book,image_raw_idx,brag_peak_test,doseLabels,
                                                                 os.path.join(init_paras.output_path , patient_case_name))
        
    # calc gamma index
    delta_distance_in_mm = patient_config_lst._Gammer_delta_distance_in_mm       #Enter tolerance distance (mm):
    delta_dose_percentage = patient_config_lst._Gammer_delta_dose_percentage      #Enter tolerance level (%):  
    ratio_voxels_within_tolerance = patient_config_lst._Gammer_ratio_voxels_within_tolerance  #Enter ratio of voxels to be within the tolerance for the test to pass
    search_radius = patient_config_lst._Gammer_search_radius
    result_as_booleans = False
    gamma_result = calculate_gamma_index_3d(dose_BenchMark,
                                        dose_test, 
                                        delta_distance_in_mm, 
                                        delta_dose_percentage/100., 
                                        search_radius, 
                                        result_as_booleans,
                                        ratio_voxels_within_tolerance)
    #test_passed = gamma_result._percentage_passing
    gamma_result_count_voxels_not_satisfied = gamma_result._count_voxels_not_satisfied
    gamma_result_count_voxels_tested = gamma_result._count_voxels_tested    
    gamma_result_percentage_passing = 100 - round(100*(float(gamma_result_count_voxels_not_satisfied)/float(gamma_result_count_voxels_tested)),2)

    Analysis_results["Gamma Index Analysis Result"] = { "count_voxels_not_satisfied:": gamma_result_count_voxels_not_satisfied, \
                                                "count_voxels_tested:": gamma_result_count_voxels_tested, \
                                                "percentage_passing:": gamma_result_percentage_passing}

    image_raw_idx = book.write_single(image_raw_idx+1,image_column_idx,"Gammer Result statistic Info")
    image_raw_idx = book.write(image_raw_idx, image_column_idx,"count_voxels_not_satisfied", gamma_result_count_voxels_not_satisfied)
    image_raw_idx = book.write(image_raw_idx, image_column_idx,"count_voxels_tested", gamma_result_count_voxels_tested)
    image_raw_idx = book.write(image_raw_idx, image_column_idx,"percentage_passing", gamma_result_percentage_passing)
        
    gamma_result_label = 'Gamma index'
    gamma_result_container = gamma_result._gamma_result_container
    gamma_result_xIndex = np.int(gamma_result_container.x.size/2)
    gamma_result_yIndex = np.int(gamma_result_container.y.size/2)
    gamma_result_zIndex = np.int(gamma_result_container.z.size/2)
    
    #dvt_plot.interact_line_gamma_index(gamma_result_container, gamma_result_label)
    image_raw_idx = line_gamma_indexY_plot_save_insert_excel(gamma_result_container, gamma_result_xIndex,book,image_raw_idx,gamma_result_label,
                                                             os.path.join(init_paras.output_path , patient_case_name))     
    # total dose statistic infor
    stat_Dose3D = CalcStatistic(dose_BenchMark.dose,dose_test.dose,err_Dose3D_acceptance)
    Dose3D_delta_err_cnt, Dose3D_total_valid_cnt,Dose3D_max_refDose,Dose3D_max_diff_norm_val = stat_Dose3D.calc_Dose_statistic(min_Dose3D_acceptPerc)
    if not Dose3D_total_valid_cnt == 0:
        Dose3D_percentage_err = round(100*(float(Dose3D_delta_err_cnt)/float(Dose3D_total_valid_cnt)),2)
    else:
        Dose3D_percentage_err = 100

    Analysis_results["3D Dose Matrix Analysis"] = { "number of failed points:": Dose3D_delta_err_cnt, \
                                                "number of total points:": Dose3D_total_valid_cnt, \
                                                "percentage_err(%):": Dose3D_percentage_err , \
                                                "max difference(%):": Dose3D_max_diff_norm_val}

    image_raw_idx = book.write_single(image_raw_idx+1,image_column_idx,"Total Dose3D statistic Info:")
    image_raw_idx = book.write(image_raw_idx, image_column_idx,"threshold tolerance", err_Dose3D_acceptance)
    image_raw_idx = book.write(image_raw_idx , image_column_idx,"max dose of reference_dose: max(ref_dose)", Dose3D_max_refDose)
    image_raw_idx = book.write(image_raw_idx, image_column_idx,"number of failed points:", Dose3D_delta_err_cnt )
    image_raw_idx = book.write(image_raw_idx, image_column_idx,"number of total points:", Dose3D_total_valid_cnt) 
    image_raw_idx = book.write(image_raw_idx, image_column_idx,"percentage_err(%):", Dose3D_percentage_err)    
    image_raw_idx = book.write(image_raw_idx, image_column_idx,"max difference(%)", Dose3D_max_diff_norm_val)

    # write Analysis Result     
    result_raw_idx = book.write_Analysis_Result(result_raw_idx,8,Analysis_results)
    book.save_book()

    