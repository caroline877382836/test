# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:34:46 2018
@author: CNXuaCar
This doc is used to read dose from PhysicalDose.00
"""
import struct
import numpy as np
import os

class ReadCSDose():
    FloatSize = 4
    IntSize = 4
    def __init__(self,path):
        self.path = path        
        self.Get_Dose3D()
    
    def Get_Dose3D(self):
        path = self.path        
        if not os.path.isfile(path):  
            print 'Dose file: ' + path + 'not exits'
        f = open(path, 'rb')        
        shape = struct.unpack('3L',f.read(self.IntSize*3))        
        Len = shape[0]*shape[1]*shape[2]
        tupleData = struct.unpack(str(Len)+'f', f.read(self.FloatSize*Len))
        data3D = np.array(tupleData).reshape(shape[2], shape[1],shape[0]) #change to depth,height,width (Tra:width = x, height = z)
        self.Data3D = data3D
        
    def Get_Dose2D_with_LayerIdx(self,layer_idx,BeamDirection):   #### TODO: only support two directions
        data3D = self.Data3D        
        if BeamDirection.lower() == "width":
            data2D = data3D[0:data3D.shape[0],0:data3D.shape[1],layer_idx]# width direction            
        if BeamDirection.lower() == "height":
            data2D = data3D[0:data3D.shape[0],layer_idx,0:data3D.shape[2]]#height direction
        if BeamDirection.lower() != "width" and BeamDirection.lower() != "height":
            print "like this Gaussian(directory,grid,direction,plane), direction only support 'width' and height'"            
        np.squeeze(data2D)
        return data2D
    
    def Get_layCnt(self,BeamDirection):   #### TODO: only support two directions
        if BeamDirection.lower() == "width":            
            layer_cnt = self.Data3D.shape[2]
        if BeamDirection.lower() == "height":
            layer_cnt = self.Data3D.shape[1]           
        return layer_cnt