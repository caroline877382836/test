# -*- coding: utf-8 -*-
"""
Created on Mon Oct  9 11:33:10 2017

@author: CNLiLuk
"""
import scipy
from scipy import special
import scipy.optimize as optimize
import xlwt
import datetime
import pandas as pd
from time import gmtime, strftime
#import math
import struct
import numpy as np
import os
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
from matplotlib import axes
from sys import argv


class GaussianERFFitException(Exception):
    def __init__(self,file_name): 
        self._log_file_name = file_name        
        
    def _write_log_msg(self,message): 
        self._log_file = open(self._log_file_name, "a")               
        self._log_file.write("{0}".format(message) + "\r\n")
        self._log_file.close()
        
class WriteDada2Excel:  #each patient correspond to one sheet
    def __init__(self,book,benchMarch_sigma, protonCS_sigma, del_sigma, testPatientName):   # init create excel file: if exits / not
        self._book = book
        self._benchMarch_sigma =  benchMarch_sigma
        self._protonCS_sigma =  protonCS_sigma       
        self._del_sigma = del_sigma  #list[sigmaX,sigmaY]     
        self._testPatientName = testPatientName 
    
    def add_sheet(self):
        #Add a sheet with one line of data  
        value = "This sheet with patient named: %s" % self._testPatientName
        book = self._book
        sheet = book.add_sheet(self._testPatientName)
        sheet.write(0,0, value)
        sheet.write(0, 1, "total_LayerCnt : %s" %  len(self._benchMarch_sigma))
        self._sheet = sheet
    
    def write2_sheet(self):  
        self._sheet.write(1, 0, "benchMarch_sigmaX") 
        self._sheet.write(1, 1, "benchMarch_sigmaY") 
        self._sheet.write(1, 2, "protonCS_sigmaX") 
        self._sheet.write(1, 3, "protonCS_sigmaY")
        self._sheet.write(1, 4, "delta_sigmaX")  # bench - Proton
        self._sheet.write(1, 5, "delta_sigmaY") 
        for idx in range(0,len(self._benchMarch_sigma),1):
            self._sheet.write(idx + 2, 0, self._benchMarch_sigma[idx][0])
            self._sheet.write(idx + 2, 1, self._benchMarch_sigma[idx][1])
            self._sheet.write(idx + 2, 2, self._protonCS_sigma[idx][0])
            self._sheet.write(idx + 2, 3, self._protonCS_sigma[idx][1])
            self._sheet.write(idx + 2, 4, self._del_sigma[idx][0])
            self._sheet.write(idx + 2, 5, self._del_sigma[idx][1])
    def save_sheet(self):
        self._book.save(self._excel_name + ".xls")   
        
    def insert_image_into_excel(self,image):
        self._sheet.set_column('A:A', 30)
        self._sheet.write('A2', 'Insert an image in a cell:')
        self._sheet.insert_image('B2', 'python.png')             

class ReadDada:  
    def __init__(self,datapath,direction,Plane):
        self.datapath = datapath
        self.direction = direction
        self.Plane = Plane
        self._readbin()        
    
    def _readbin(self):
        Floatsize = 4
        Intsize = 4
        if not os.path.isfile(self.datapath):            
            log_msg._write_log_msg("%s is not a file!"%self.datapath)  
        file = open(self.datapath,'rb')
        shape = struct.unpack('3L',file.read(Intsize*3))
        Len = shape[0]*shape[1]*shape[2]
        tupleData = struct.unpack(str(Len)+'f', file.read(Floatsize*Len))
        data = np.array(tupleData).reshape(shape[2], shape[1],shape[0])#[depth,height,width]
        #data2D = np.zeros(shape(shape[1],shape[2]),float)
        if self.direction.lower() == "width":
            data2D = data[0:shape[2],0:shape[1],int(self.Plane)]# width direction
            self._layer_cnt = shape[0]
        if self.direction.lower() == "height":
            data2D = data[0:shape[2],int(self.Plane),0:shape[0]]#height direction
            self._layer_cnt = shape[1]
        if self.direction.lower() != "width" and self.direction.lower() != "height":
            msg = "like this Gaussian(directory,grid,direction,plane), direction only support 'width' and height'"
            #output = GaussianERFFitException(msg)
            log_msg._write_log_msg(msg)  
        np.squeeze(data2D)
        self._data2D = data2D
        self._shape = data2D.shape
              
class GaussianERFFit:
    def __init__(self,data2D,grid):        
        self._data2D = data2D
        self._shape = data2D.shape

        self.grid = grid
       
        self.top,self.bottom,self.left,self.right, self.clipData = self._findRectangle()        
        try:
            self.p = self._cacl_para()
            self.sigmaX = abs(self.p[2])
            self.sigmaY = abs(self.p[3])
            #print(self._Imx,self._Imy,self._IsigmaX,self._IsigmaY,self._IA)
            #print(self.p)
            #print("sigmaX is %f, sigmaY is %f"%(self.sigmaX,self.sigmaY))

            figure2 = plt.figure()
            ax = Axes3D(figure2)
            X = np.arange(self.left,self.right,1)
            Y = np.arange(self.top,self.bottom,1)
            X,Y = np.meshgrid(X,Y)
            ax.plot_surface(X,Y,self.clipData,rstride=1,cstride=1,cmap='rainbow')
            plt.show()
        except Exception:
            pass 
        
    def _plot_2D(self):        
        #print(self._shape[0],self._shape[1],np.max(data2D))
        '''
        hIDD = np.zeros((shape[1],2),float)
        for i in range(shape[1]):
            hIDD[i,0] = i
            for j in range(shape[0]):
                for k in range(shape[2]):                    
                    hIDD[i,1] = hIDD[i,1] + data[k,i,j]
                    
        plt.figure(1)
        plt.plot(hIDD[0:shape[1],0], hIDD[0:shape[1],1])
        plt.show()      '''        

        figure2 = plt.figure()
        ax = Axes3D(figure2)
        X = np.arange(0,self._data2D[0],1)
        Y = np.arange(0,self._data2D[1],1)
        X,Y = np.meshgrid(X,Y)
        ax.plot_surface(X,Y,self._data2D,rstride=1,cstride=1,cmap='rainbow')
        plt.show()

        
        

    def _findRectangle(self): # check the edge with dose>0
        [top, bottom, left, right] = [0,self._shape[0]-1,0,self._shape[1]-1]        
        for i in range(0,self._shape[0],1):
            if(sum(self._data2D[i,0:self._shape[1]]) > 0):
                top = i
                break               
             
        for i in range(self._shape[0]-1,0,-1):
            if(sum(self._data2D[i,0:self._shape[1]])> 0):
                bottom = i
                break                
            
        for i in range(0,self._shape[1],1):
            if(sum(self._data2D[0:self._shape[0], i]) > 0):
                left = i
                break            
            
        for i in range(self._shape[1]-1,0,-1):
            if(sum(self._data2D[0:self._shape[0], i]) > 0):
                right = i
                break
        try:
            clippeddata2D = self._data2D[top:bottom, left:right]
            #===================================================================
            # if not [top, bottom, left, right] == [0,self._shape[0]-1,0,self._shape[1]-1]:
            #     clippeddata2D = self._data2D[top:bottom, left:right]
            # else:    
            #     clippeddata2D = self._data2D           
            #     #output = GaussianERFFitException("%s have zero dose!"% "current layer")   
            #     log_msg._write_log_msg("%s have zero dose!"% "current layer")             
            #===================================================================
        except:
            pass
        return top, bottom, left, right, clippeddata2D
    
    
    def _getInitP(self):

        self._Imx = (self.clipData.shape[1])/2.0
        self._Imy = (self.clipData.shape[0])/2.0
        self._IA = np.amax(self.clipData)*0.25#Martin's equation 0.25*A*erf()
        dataX = self.clipData[int(self._Imy), :]
        dataY = self.clipData[:, int(self._Imx)]
        self._IsigmaX = scipy.sqrt(scipy.average((scipy.arange(dataX.size) - int(self._Imx))**2, None, dataX)/2.0)
        self._IsigmaY = scipy.sqrt(scipy.average((scipy.arange(dataY.size) - int(self._Imy))**2, None, dataY)/2.0)
        return self._Imx, self._Imy,self._IsigmaX,self._IsigmaY,self._IA
     
    def _cacl_para(self):

        def ferf(mx,my,sigmaX,sigmaY,A):
            delta = self.grid
            #return lambda x, y : scipy.longfloat(0.25*A*scipy.exp(-((x-mx)*delta)**2/(2*sigmaX**2) - (((y-my)*delta)**2/(2*sigmaY**2))))
            return lambda x, y : 0.25*A*(scipy.special.erf(((x-mx+0.5)*delta)/(scipy.sqrt(2.0)*sigmaX))-scipy.special.erf(((x-mx-0.5)*delta)/(scipy.sqrt(2.0)*sigmaX)))*(scipy.special.erf(((y-my+0.5)*delta)/(scipy.sqrt(2.0)*sigmaY))-scipy.special.erf(((y-my-0.5)*delta)/(scipy.sqrt(2.0)*sigmaY)))
        def errorSquare(p):
            cd = self.clipData
            y, x= scipy.indices(cd.shape) # data2D = data[0:shape[2],self.Plane,0:shape[0]], depth,height,width = z,y,x here.
            f = ferf(*p)
            return (f(x,y) - cd).ravel()
        initialP = self._getInitP()
        p, cov, infodict, msg, ier = optimize.leastsq(errorSquare, initialP, full_output = True)
        return p      
        
        
   

if __name__ == "__main__" :
    # test data folder dir    
    INPUT_FOLDER = 'D:/TestData/SingleSpot/'
    os.chdir(INPUT_FOLDER)
    cur_dir = os.getcwd()
    base_dir = os.path.abspath(os.path.join(cur_dir, os.pardir))    
    test_data_exe = os.path.join(base_dir,"read_dose.exe")
    
    patients = os.listdir(cur_dir)
    patients_benchMark = []
    patients_Proton = []
    direction = "height"
    grid = 2    
    for i in patients:
        if not i.endswith("_Proton"):
            patients_benchMark.append(i)
        elif i.endswith("_Proton"):
            patients_Proton.append(i) 
             
    if os.path.isfile(os.path.join(cur_dir,"log_msg.txt")):
        os.remove(os.path.join(cur_dir,"log_msg.txt")) # remove the file
                
    log_msg = GaussianERFFitException("log_msg.txt")   
         
    book = xlwt.Workbook(encoding="utf-8")
    excel_name = strftime("%Y-%m-%d %H:%M:%S", gmtime()).replace(':', '-')     # set as current time         
    for i in patients_benchMark:
        if os.path.isdir(os.path.join(cur_dir,i)):
            log_msg._write_log_msg("Patient DATA Name: " + i)
            path_benchMark = os.path.join(os.path.join(cur_dir,i),"IDOSELocalFiles.1")  #TODO: transfer the file format use readfile.exe
            #process= subprocess.Popen(['cmd','/c',r'D:\TestData\cidose']) #subprocess.Popen(['cmd','/c',r'calc.exe'])
            #process.wait()
            #subprocess.check_call(['cidose'])  # no file output
            
            proton_name = i + "_Proton"
            path_proton = os.path.join(os.path.join(cur_dir,proton_name),"PhysicalDose.00")
            data_2DbenchMark = ReadDada(path_benchMark, direction, 5)        
            lay_cnt = data_2DbenchMark._layer_cnt
            benchMarch_sigma = []  # [sigmaX,sigmaY]
            protonCS_sigma = []
            del_sigma = []
            for lay_idx in range(0, lay_cnt, 1):  # loop for all the layers                
                data_2DbenchMark = ReadDada(path_benchMark, direction, lay_idx)
                data_2Dproton = ReadDada(path_proton, direction, lay_idx)
                
                axx_benchMarch = GaussianERFFit(data_2DbenchMark._data2D, grid)
                axx_proton = GaussianERFFit(data_2Dproton._data2D, grid)
                 
                try:                    
                    if hasattr(axx_benchMarch, 'sigmaX'):
                        benchMarch_sigma.append([axx_benchMarch.sigmaX, axx_benchMarch.sigmaY])
                    else:
                        benchMarch_sigma.append([0, 0]) # zero dose case: assign to sigmaX and sigmaY to 0 currently                        
                        log_msg._write_log_msg("BenchData: both values of sigmaX and sigmaY are assigned to 0 due to current layer: %s have zero dose!"% lay_idx)   
                except:
                    pass
                
                try:
                    if hasattr(axx_proton, 'sigmaX'):
                        protonCS_sigma.append([axx_proton.sigmaX, axx_proton.sigmaY])
                    else:
                        protonCS_sigma.append([0, 0]) # zero dose case: assign to sigmaX and sigmaY to 0 currently                        
                        log_msg._write_log_msg("Proton Data: both values of sigmaX and sigmaY are assigned to 0 due to current layer: %s have zero dose!" % lay_idx)    
                except:
                    pass
                
                del_sigma.append([benchMarch_sigma[lay_idx][0] - protonCS_sigma[lay_idx][0], benchMarch_sigma[lay_idx][1] - protonCS_sigma[lay_idx][1]])   
            excel = WriteDada2Excel(book, benchMarch_sigma, protonCS_sigma, del_sigma, i)               
            excel.add_sheet()
            excel.write2_sheet()
            book.save(excel_name + ".xls")  

            # print(axx_proton.sigmaX, axx_proton.sigmaY)                    

    
