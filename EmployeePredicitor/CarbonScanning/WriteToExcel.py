# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:34:46 2018
@author: CNXuaCar
This doc is used to write those analysing results and images into excel sheet
"""
from xlsxwriter.workbook import Workbook
import logging
import xlwt
import os
import re

logger = logging.getLogger(__name__)

class WriteDada2Excel:  #each patient correspond to one sheet
    def __init__(self,excel_name):   # init create excel file: if exits / not        
        self.excel_name = excel_name
        if os.path.exists(excel_name):
            #book = open_workbook(excel_name,on_demand=True)
            #self._book = copy(book)
            os.remove(excel_name)
            logger.info('Delete the existing old excel file named:' + excel_name)        
        self._book = Workbook(excel_name)
        self.book_format = self._book.add_format({'bold': True, 'font_color': 'red'})  
        self.format_bold = self._book.add_format({'bold': True})  
        self.raw_idx = 0

    def change_font(self,font_color):
        font=self._book.add_format({'font_color':font_color})
        return font

    def format(self):
        font=self._book.add_format({'font_size':11,'bold':True})
        return font
     
    def add_sheet(self,testPatientName,lay_cnt):
        #Add a sheet with one line of data  
        #value = "This sheet with patient named: %s" % testPatientName
        book = self._book
        try:
            sheet = book.add_worksheet(name = testPatientName)
            logger.info('worsheet with name: ' + testPatientName + 'created')
        except Exception,e:
            logger.error('create new worksheet {}. failed: Reason is: {}'.format(testPatientName, str(e)), exc_info=True)
            raise e        
        sheet.set_column('A:A', 30)
        #sheet.col_width(10)
        sheet.write(0,0, "Testing Information",self.book_format)
        #sheet.write(0, 1, "total_LayerCnt : %s" %  lay_cnt)
        self._sheet = sheet
        raw_idx = 1
        self.raw_idx = raw_idx
        return raw_idx

    def add_sum_sheet(self,summary_name):
        book = self._book
        try:
            sum_sheet = book.add_worksheet(name = summary_name)
            logger.info('worsheet with name: ' + summary_name + ' created')
        except Exception,e:
            logger.error('create new   {}. failed: Reason is: {}'.format(summary_name, str(e)), exc_info=True)
            raise e
        sum_sheet.set_column('A:B', 15)
        sum_sheet.set_column('B:B', 20)
        sum_sheet.set_column('C:C', 35)
        sum_sheet.set_column('E:J', 25)
        font=self._book.add_format({'font_size':11,'bold':True,'align':'center'})
        sum_sheet.merge_range(0,0,0,2,"General Information",font)
        sum_sheet.merge_range(0,4,0,9,"Testing Result Overview",font)
        #sum_sheet.write(0,0, "General Information",font)
        self._sheet = sum_sheet
        raw_idx = 1
        self.raw_idx = raw_idx
        return sum_sheet,raw_idx
     
    def write_sigmas_2_sheet(self,raw_idx,column_idx,benchMarch_sigma, protonCS_sigma, del_sigma,err_delta_sigma_acceptance):  
        self._sheet.write(raw_idx, column_idx, "benchMarch_sigmaX",self.format_bold) 
        self._sheet.write(raw_idx, column_idx+1, "benchMarch_sigmaY",self.format_bold) 
        self._sheet.write(raw_idx, column_idx+2, "protonCS_sigmaX",self.format_bold) 
        self._sheet.write(raw_idx, column_idx+3, "protonCS_sigmaY",self.format_bold)
        self._sheet.write(raw_idx, column_idx+4, "delta_sigmaX",self.format_bold)  # bench - Proton
        self._sheet.write(raw_idx, column_idx+5, "delta_sigmaY",self.format_bold) 
        for idx in range(0,len(benchMarch_sigma),1):
            self._sheet.write(raw_idx + idx + 2, column_idx, benchMarch_sigma[idx][0])
            self._sheet.write(raw_idx + idx + 2, column_idx+1, benchMarch_sigma[idx][1])
            self._sheet.write(raw_idx + idx + 2, column_idx+2, protonCS_sigma[idx][0])
            self._sheet.write(raw_idx + idx + 2, column_idx+3, protonCS_sigma[idx][1])
            if abs(del_sigma[idx][0]) >= err_delta_sigma_acceptance:
                self._sheet.write(raw_idx + idx + 2, column_idx+4, del_sigma[idx][0], self.book_format)
            else:
                self._sheet.write(raw_idx + idx + 2, column_idx+4, del_sigma[idx][0])
            if abs(del_sigma[idx][1]) >= err_delta_sigma_acceptance:
                self._sheet.write(raw_idx + idx + 2, column_idx+5, del_sigma[idx][1], self.book_format)
            else:
                self._sheet.write(raw_idx + idx + 2, column_idx+5, del_sigma[idx][1])
        raw_idx = raw_idx + len(benchMarch_sigma) + 2
        self.raw_idx = raw_idx
        return raw_idx

       # TODO:the detail beam model paras needed be changes, currently hard coded
    def write_beam_model_paras_2_sheet(self,raw_idx):     
        self._sheet.write(raw_idx,0,"beam_model_parameters", self.format_bold)
        self._sheet.write(raw_idx,1,"FermiEygesMomentsX.ThetaSquared") 
        self._sheet.write(raw_idx,2, 3.2679055655063508E-05) 
        self._sheet.write(raw_idx + 1,1, "FermiEygesMomentsX.RadiusTheta") 
        self._sheet.write(raw_idx + 1,2, 0.00532537652464779) 
        self._sheet.write(raw_idx + 2,1,"FermiEygesMomentsX.RadiusSquare") 
        self._sheet.write(raw_idx + 2,2, 9.685868421894394) 
        self._sheet.write(raw_idx + 3,1,"FermiEygesMomentsX.DefinitionPlane") 
        self._sheet.write(raw_idx + 3,2, 430) 
        self._sheet.write(raw_idx + 4,1,"FermiEygesMomentsY.ThetaSquared") 
        self._sheet.write(raw_idx + 4,2, 3.191065138211672E-05) 
        self._sheet.write(raw_idx + 5,1,"FermiEygesMomentsY.RadiusTheta") 
        self._sheet.write(raw_idx + 5,2, -0.0061629491637689819) 
        self._sheet.write(raw_idx + 6,1,"FermiEygesMomentsY.RadiusSquare")
        self._sheet.write(raw_idx + 6,2, 31.053750010832385)
        self._sheet.write(raw_idx + 7,1,"FermiEygesMomentsY.DefinitionPlane") 
        self._sheet.write(raw_idx + 7,2, 430) 
        raw_idx=raw_idx+8
        self.raw_idx=raw_idx
        return raw_idx

    # TODO:patient_change_cong_lst: item = [key,value]
    def write_request_paras_2_sheet(self,raw_idx,contents,patient_change_cong_lst):        
        raw_idx = self._sheet.write(raw_idx,0,"request_parameter",self.format_bold)       
        len_ct = len(contents)
        # convert list to dict
        patient_change_cong_dict = {}
        for item in range(0,len(patient_change_cong_lst),1):
            temp = patient_change_cong_lst[item]
            patient_change_cong_dict[temp[0]] = temp[1]

        for i in range(0,len_ct,1) :  
            if not contents[i] == '':
                if contents[i].keys()[0] == "nGridDimX,nGridDimY,nGridDimZ":  # maybe change GridSize
                    if patient_change_cong_dict.has_key("nGridDimX"):                        
                        self._sheet.write(self.raw_idx ,1,"nGridDimX",self.book_format) 
                        self._sheet.write(self.raw_idx ,2,float(patient_change_cong_dict["nGridDimX"]),self.book_format)
                        self._sheet.write(self.raw_idx + 1,1,"nGridDimY",self.book_format)
                        self._sheet.write(self.raw_idx + 1,2,float(patient_change_cong_dict["nGridDimY"]),self.book_format)  
                        self._sheet.write(self.raw_idx + 2,1,"nGridDimZ",self.book_format)
                        self._sheet.write(self.raw_idx + 2,2,float(patient_change_cong_dict["nGridDimZ"]),self.book_format)                  
                        self.raw_idx = self.raw_idx + 3
                    else:
                        vals = contents[i].values()
                        self._sheet.write(self.raw_idx ,1, "nGridDimX") 
                        self._sheet.write(self.raw_idx ,2, float(vals[0][0]))
                        self._sheet.write(self.raw_idx + 1,1, "nGridDimY") 
                        self._sheet.write(self.raw_idx + 1,2, float(vals[0][1]))
                        self._sheet.write(self.raw_idx + 2,1, "nGridDimZ" ) 
                        self._sheet.write(self.raw_idx + 2,2, float(vals[0][2]))
                        self.raw_idx = self.raw_idx + 3  
                elif contents[i].keys()[0] == "voxelSizeX,voxelSizeY,voxelSizeZ": 
                    if patient_change_cong_dict.has_key("voxelSizeX"):                        
                        self._sheet.write(self.raw_idx ,1,"voxelSizeX",self.book_format) 
                        self._sheet.write(self.raw_idx ,2,patient_change_cong_dict["voxelSizeX"],self.book_format)
                        self._sheet.write(self.raw_idx + 1,1,"voxelSizeY",self.book_format)
                        self._sheet.write(self.raw_idx + 1,2,patient_change_cong_dict["voxelSizeY"],self.book_format)  
                        self._sheet.write(self.raw_idx + 2,1,"voxelSizeZ",self.book_format) 
                        self._sheet.write(self.raw_idx + 2,2,patient_change_cong_dict["voxelSizeZ"],self.book_format)
                        self.raw_idx = self.raw_idx + 3
                    else:
                        vals = contents[i].values()
                        self._sheet.write(self.raw_idx ,1, "voxelSizeX") 
                        self._sheet.write(self.raw_idx ,2, float(vals[0][0]))
                        self._sheet.write(self.raw_idx + 1,1, "voxelSizeY") 
                        self._sheet.write(self.raw_idx + 1,2, float(vals[0][1]))
                        self._sheet.write(self.raw_idx + 2,1, "voxelSizeZ")
                        self._sheet.write(self.raw_idx + 2,2, float(vals[0][2]))
                        self.raw_idx = self.raw_idx + 3 
                elif contents[i].keys()[0] == "isocenterPos[0],isocenterPos[1],isocenterPos[2]": 
                    if patient_change_cong_dict.has_key("isocenterPos[0]"):                        
                        self._sheet.write(self.raw_idx ,1,"isocenterPos[0]",self.book_format) 
                        self._sheet.write(self.raw_idx ,2,float(patient_change_cong_dict["isocenterPos[0]"]),self.book_format)
                        self._sheet.write(self.raw_idx + 1,1,"isocenterPos[1]",self.book_format) 
                        self._sheet.write(self.raw_idx + 1,2,float(patient_change_cong_dict["isocenterPos[1]"]),self.book_format)
                        self._sheet.write(self.raw_idx + 2,1,"isocenterPos[2]",self.book_format)
                        self._sheet.write(self.raw_idx + 2,2,float(patient_change_cong_dict["isocenterPos[2]"]),self.book_format) 
                        self.raw_idx = self.raw_idx + 3
                    else:
                        vals = contents[i].values()
                        self._sheet.write(self.raw_idx ,1, "isocenterPos[0]")
                        self._sheet.write(self.raw_idx ,2, float(vals[0][0])) 
                        self._sheet.write(self.raw_idx + 1,1, "isocenterPos[1]") 
                        self._sheet.write(self.raw_idx + 1,2, float(vals[0][1]))
                        self._sheet.write(self.raw_idx + 2,1, "isocenterPos[2]") 
                        self._sheet.write(self.raw_idx + 2,2, float(vals[0][2]))
                        self.raw_idx = self.raw_idx + 3 
                elif contents[i].keys()[0] == "beamData.matrixBeamToPatient[0][0], \
                            beamData.matrixBeamToPatient[0][1], \
                            beamData.matrixBeamToPatient[0][2], \
                            beamData.matrixBeamToPatient[1][0], \
                            beamData.matrixBeamToPatient[1][1], \
                            beamData.matrixBeamToPatient[1][2], \
                            beamData.matrixBeamToPatient[2][0], \
                            beamData.matrixBeamToPatient[2][1], \
                            beamData.matrixBeamToPatient[2][2]": 
                   
                    if patient_change_cong_dict.has_key("beamData.matrixBeamToPatient[0][0]"):                        
                        self._sheet.write(self.raw_idx ,1,"beamData.matrixBeamToPatient[0][0]", self.book_format) 
                        self._sheet.write(self.raw_idx ,2,
                                        float(patient_change_cong_dict["beamData.matrixBeamToPatient[0][0]"]),self.book_format) 

                        self._sheet.write(self.raw_idx + 1,1,"beamData.matrixBeamToPatient[0][1]", self.book_format) 
                        self._sheet.write(self.raw_idx + 1,2,
                                        float(patient_change_cong_dict["beamData.matrixBeamToPatient[0][1]"]),self.book_format) 

                        self._sheet.write(self.raw_idx + 2,1,"beamData.matrixBeamToPatient[0][2]", self.book_format)
                        self._sheet.write(self.raw_idx + 2,2,
                                        float(patient_change_cong_dict["beamData.matrixBeamToPatient[0][2]"]),self.book_format) 

                        self._sheet.write(self.raw_idx + 3,1,"beamData.matrixBeamToPatient[1][0]", self.book_format) 
                        self._sheet.write(self.raw_idx + 3,2,
                                        float(patient_change_cong_dict["beamData.matrixBeamToPatient[1][0]"]),self.book_format)

                        self._sheet.write(self.raw_idx + 4,1,"beamData.matrixBeamToPatient[1][1]", self.book_format) 
                        self._sheet.write(self.raw_idx + 4,2,
                                        float(patient_change_cong_dict["beamData.matrixBeamToPatient[1][1]"]),self.book_format)

                        self._sheet.write(self.raw_idx + 5,1,"beamData.matrixBeamToPatient[1][2]", self.book_format)
                        self._sheet.write(self.raw_idx + 5,2,
                                        float(patient_change_cong_dict["beamData.matrixBeamToPatient[1][2]"]),self.book_format)

                        self._sheet.write(self.raw_idx + 6,1,"beamData.matrixBeamToPatient[2][0]", self.book_format)
                        self._sheet.write(self.raw_idx + 6,2,
                                        float(patient_change_cong_dict["beamData.matrixBeamToPatient[2][0]"]),self.book_format) 

                        self._sheet.write(self.raw_idx + 7,1,"beamData.matrixBeamToPatient[2][1]", self.book_format) 
                        self._sheet.write(self.raw_idx + 7,2,
                                        float(patient_change_cong_dict["beamData.matrixBeamToPatient[2][1]"]),self.book_format) 

                        self._sheet.write(self.raw_idx + 8,1,"beamData.matrixBeamToPatient[2][2]", self.book_format)  
                        self._sheet.write(self.raw_idx + 8,2,
                                        float(patient_change_cong_dict["beamData.matrixBeamToPatient[2][2]"]),self.book_format)

                        self.raw_idx = self.raw_idx + 9
                    else:
                        vals = contents[i].values()
                        self._sheet.write(self.raw_idx ,1,"beamData.matrixBeamToPatient[0][0]") 
                        self._sheet.write(self.raw_idx ,2,float(vals[0][0]) )
                        self._sheet.write(self.raw_idx + 1,1,"beamData.matrixBeamToPatient[0][1]") 
                        self._sheet.write(self.raw_idx + 1,2,float(vals[0][1]) )
                        self._sheet.write(self.raw_idx + 2,1,"beamData.matrixBeamToPatient[0][2]")
                        self._sheet.write(self.raw_idx + 2,2,float(vals[0][2]))
                        
                        self._sheet.write(self.raw_idx+3 ,1,"beamData.matrixBeamToPatient[1][0]") 
                        self._sheet.write(self.raw_idx+3 ,2,float(vals[0][3])) 
                        self._sheet.write(self.raw_idx+4,1,"beamData.matrixBeamToPatient[1][1]") 
                        self._sheet.write(self.raw_idx+4,2,float(vals[0][4]))
                        self._sheet.write(self.raw_idx+5,1,"beamData.matrixBeamToPatient[1][2]")
                        self._sheet.write(self.raw_idx+5,2,float(vals[0][5]))

                        self._sheet.write(self.raw_idx+6,1,"beamData.matrixBeamToPatient[2][0]") 
                        self._sheet.write(self.raw_idx+6,2,float(vals[0][6]))
                        self._sheet.write(self.raw_idx+7,1,"beamData.matrixBeamToPatient[2][1]") 
                        self._sheet.write(self.raw_idx+7,2,float(vals[0][7]))
                        self._sheet.write(self.raw_idx+8,1,"beamData.matrixBeamToPatient[2][2]")
                        self._sheet.write(self.raw_idx+8,2,float(vals[0][8]))
                        self.raw_idx = self.raw_idx + 9
                elif contents[i].keys()[0] == "positionOnIso[0],positionOnIso[1]": 
                    if patient_change_cong_dict.has_key("positionOnIso[0]"):                        
                        self._sheet.write(self.raw_idx, 1,"positionOnIso[0]",self.book_format)
                        temp = float(patient_change_cong_dict["positionOnIso[0]"])
                        self._sheet.write(self.raw_idx , 2, temp, self.book_format) 
                        self._sheet.write(self.raw_idx + 1, 1,"positionOnIso[1]",self.book_format)
                        temp = float(patient_change_cong_dict["positionOnIso[1]"])
                        self._sheet.write(self.raw_idx + 1, 2, temp, self.book_format) 
                        self.raw_idx = self.raw_idx + 2
                    else:
                        vals = contents[i].values()
                        self._sheet.write(self.raw_idx , 1, "positionOnIso[0]") 
                        self._sheet.write(self.raw_idx , 2, float(vals[0][0]))
                        self._sheet.write(self.raw_idx + 1, 1, "positionOnIso[1]")
                        self._sheet.write(self.raw_idx + 1, 2, float(vals[0][1]))
                        self.raw_idx = self.raw_idx + 2 
                else:
                    pattern = re.compile(r'^[-+]?[0-9]+\.?[0-9]?')
                    if patient_change_cong_dict.has_key(contents[i].keys()[0]):
                        self._sheet.write(self.raw_idx , 1, contents[i].keys()[0], self.book_format)                       
                        temp = patient_change_cong_dict[contents[i].keys()[0]]                        
                        if not type(temp)== str:                        
                            self._sheet.write(self.raw_idx ,2, float(temp), self.book_format)
                        else:
                            self._sheet.write(self.raw_idx , 2, temp, self.book_format)
                        self.raw_idx = self.raw_idx + 1  
                    else:
                        self._sheet.write(self.raw_idx , 1,  contents[i].keys()[0] )
                        if contents[i].values()[0] == '':
                            self._sheet.write(self.raw_idx , 2,  contents[i].values()[0])
                        else:                            
                            if not pattern.match(contents[i].values()[0]) == None:  #recognize number
                                #contents[i].values()[0] == "File version":
                                self._sheet.write(self.raw_idx , 2,  float(contents[i].values()[0]) )
                            else:
                                self._sheet.write(self.raw_idx , 2,  contents[i].values()[0])
                        self.raw_idx = self.raw_idx + 1          
        
        return self.raw_idx
    
    # total line number: 73, refer to ProtonRequest_compare.txt
    def read_proton_request_file(self, file_path):
        contents = []
        with open(file_path,"r") as f:            
            contents.append({"File version": f.readline().rstrip('\n')})
            contents.append({"convEps":f.readline().rstrip('\n')})
            contents.append({"nMaxIteration":f.readline().rstrip('\n')})
            contents.append({"beamDoseUniformity":f.readline().rstrip('\n')})
            contents.append({"minCtNumber":f.readline().rstrip('\n')})
            contents.append({"surfaceMargin":f.readline().rstrip('\n')})
            contents.append({"paretiConstrainedMode":f.readline().rstrip('\n')})
            contents.append({"applyNuclearScatteringCorrection":f.readline().rstrip('\n')})
            contents.append({"kernelGenerationALg":f.readline().rstrip('\n')})
            contents.append({"rbeModelType":f.readline().rstrip('\n')})
            #line 11
            contents.append({"nKernelGernerationPrecision":f.readline().rstrip('\n')})
            contents.append({"nFinalGernerationPrecision":f.readline().rstrip('\n')})
            contents.append({"nuclearInteraction":f.readline().rstrip('\n')})
            contents.append({"bDoseToWater":f.readline().rstrip('\n')})
            contents.append({"photonCutoffEnergy":f.readline().rstrip('\n')})
            contents.append({"electronCutoffEnergy":f.readline().rstrip('\n')})
            contents.append({"protonCutoffEnergy":f.readline().rstrip('\n')})           
            contents.append({"doseThreshold":f.readline().rstrip('\n')})
            contents.append({"maxParticlesPerSpot": f.readline().rstrip('\n')})
            contents.append({"uncertaintyPerSpot": f.readline().rstrip('\n')})
             #line 21
            contents.append({"nGridDimX,nGridDimY,nGridDimZ": f.readline().rstrip('\n').split(',')})
            contents.append({"voxelSizeX,voxelSizeY,voxelSizeZ":f.readline().rstrip('\n').split(',')})
            contents.append({"nBeamNumr": f.readline().rstrip('\n')})
            contents.append({"nTargetNumr": f.readline().rstrip('\n')})
            contents.append({"materialDataLocation": f.readline().rstrip('\n')})
            contents.append({"materialTableName": f.readline().rstrip('\n')})
            contents.append({"doseCalibrationType": f.readline().rstrip('\n')})
            contents.append({"finalCalculationAlg": f.readline().rstrip('\n')})
            contents.append({"arrOffsetInfo.size": f.readline().rstrip('\n')})
            contents.append({"arrBeamData.size": f.readline().rstrip('\n')})
            #line 31
            contents.append({"nPaints": f.readline().rstrip('\n')})
            contents.append({"nSweeps": f.readline().rstrip('\n')})
            contents.append({"strRidgeFilterID": f.readline().rstrip('\n')})
            contents.append({"nominalBeamIntensity": f.readline().rstrip('\n')})
            contents.append({"isocenterPos[0],isocenterPos[1],isocenterPos[2]": f.readline().rstrip('\n').split(',')})
            contents.append({"beamData.matrixBeamToPatient[0][0], \
                            beamData.matrixBeamToPatient[0][1], \
                            beamData.matrixBeamToPatient[0][2], \
                            beamData.matrixBeamToPatient[1][0], \
                            beamData.matrixBeamToPatient[1][1], \
                            beamData.matrixBeamToPatient[1][2], \
                            beamData.matrixBeamToPatient[2][0], \
                            beamData.matrixBeamToPatient[2][1], \
                            beamData.matrixBeamToPatient[2][2]":  f.readline().rstrip('\n').split(',')})
            contents.append({"gantryAngle": f.readline().rstrip('\n')})
            contents.append({"collimatorAngle": f.readline().rstrip('\n')})
            contents.append({"couchRollAngle": f.readline().rstrip('\n')})
            contents.append({"couchPitchAngle": f.readline().rstrip('\n')})
             #line 41
            contents.append({"couchYawAngle": f.readline().rstrip('\n')})
            contents.append({"snoutID": f.readline().rstrip('\n')})
            contents.append({"strMachineID": f.readline().rstrip('\n')})
            contents.append({"strSpotTuneID": f.readline().rstrip('\n')})
            contents.append({"xFocusToIsocenter": f.readline().rstrip('\n')})
            contents.append({"yFocusToIsocenter": f.readline().rstrip('\n')})
            contents.append({"spotPlacementMarginOption": f.readline().rstrip('\n')})
            contents.append({"sliceThicknessOption": f.readline().rstrip('\n')})
            contents.append({"marginLateral": f.readline().rstrip('\n')})
            contents.append({"marginDistal": f.readline().rstrip('\n')})
            #line 51
            contents.append({"marginProximal": f.readline().rstrip('\n')})
            contents.append({"radiusProximalSmearing": f.readline().rstrip('\n')})
            contents.append({"radiusDistalSmearing": f.readline().rstrip('\n')})
            contents.append({"stepX": f.readline().rstrip('\n')})
            contents.append({"stepY": f.readline().rstrip('\n')})
            contents.append({"sliceThickness": f.readline().rstrip('\n')})
            contents.append({"peakWidthMultiplier": f.readline().rstrip('\n')})
            contents.append({"geoMargin": f.readline().rstrip('\n')})
            contents.append({"spotMode": f.readline().rstrip('\n')})
            contents.append({"longSt": f.readline().rstrip('\n')})
            #line 61
            contents.append({"arrLayerData.size": f.readline().rstrip('\n')})
            contents.append({"nShotNum": f.readline().rstrip('\n')})
            contents.append({"strBeamModelID": f.readline().rstrip('\n')})
            contents.append({"prescribedRange": f.readline().rstrip('\n')})
            contents.append({"nominalEnergy": f.readline().rstrip('\n')})
            contents.append({"airGap": f.readline().rstrip('\n')})
            contents.append({"position": f.readline().rstrip('\n')})
            contents.append({"rangeShifterId": f.readline().rstrip('\n')})
            contents.append({"rangeShifterMaterial": f.readline().rstrip('\n')})
            contents.append({"rangeShifterThickness": f.readline().rstrip('\n')})
            #line 71
            contents.append({"arrSpotData.size": f.readline().rstrip('\n')})
            contents.append({"meterset": f.readline().rstrip('\n')})
            contents.append({"positionOnIso[0],positionOnIso[1]": f.readline().rstrip('\n').split(',')})  
            return contents         

    def save_book(self):
        try:
            self._book.close()
            logger.info("save excel file successful") 
        except Exception,e:
            logger.error('save excel file failed: Reason is: {}'.format(str(e)), exc_info=True)
            raise e  
        
    def write(self,raw_idx,column,sheet_data,msg):             
        self._sheet.write(raw_idx,column,sheet_data)
        self._sheet.write(raw_idx,column+2,msg)
        raw_idx=raw_idx+1
        self.raw_idx=raw_idx
        return raw_idx

    def write_color(self,raw_idx,column,sheet_data,msg):
        self._sheet.write(raw_idx,column,sheet_data,self.book_format)
        self._sheet.write(raw_idx,column+2,msg,self.book_format)
        raw_idx=raw_idx+1
        self.raw_idx=raw_idx
        return raw_idx

    def write_Analysis_Result(self,raw_idx,column,dic_analy_result):
        self._sheet.write(raw_idx,8,"Analysis Results Overview:",self.format_bold) 
        self.raw_idx = raw_idx + 1      
        for key, value in dic_analy_result.iteritems():
            self._sheet.write(self.raw_idx,column,key,self.format_bold)  
            for i in range(0,len(value.keys()),1):
                if i == 0:
                    self._sheet.write(self.raw_idx,column + 1,value.keys()[i])
                    self._sheet.write(self.raw_idx,column + 2,value.values()[i])
                    self.raw_idx = self.raw_idx + 1
                else:
                    self._sheet.write(self.raw_idx ,column + 1,value.keys()[i])
                    self._sheet.write(self.raw_idx ,column + 2,value.values()[i])
                    self.raw_idx = self.raw_idx + 1        
             
        #self.raw_idx=self.raw_idx+1        
        return self.raw_idx   


    def write_single(self,raw_idx,column,msg):
        self._sheet.write(raw_idx, column, msg,self.format_bold)
        raw_idx=raw_idx+1
        self.raw_idx=raw_idx
        return raw_idx  
           
    def insert_image2Excel(self,raw_idx,column,msg,img_path):
        if not msg == "":
            self._sheet.write(raw_idx,column+1, msg)   

        self._sheet.insert_image(raw_idx + 1, column,img_path)        
        raw_idx = raw_idx + 27
        self.raw_idx = raw_idx
        return raw_idx
            