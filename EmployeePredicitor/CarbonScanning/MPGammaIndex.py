# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 16:34:46 2017

@author: CNLiLuk
"""
from sys import argv
import sys
import os
import struct
import numpy as np
import multiprocessing

#class Position:
#    def __init__(self, x, y, z):
#        self = np.array([x,y,z])
        
        
def read_bin(filename):
    INTSIZE = 4
    FLOATSIZE = 4
    if not os.path.isfile(filename):
        print("%s is not a file"%(filename))
        return None
    
    file = open(filename,'rb')
    shape = ()
    shape = struct.unpack('3L', file.read(INTSIZE*3))
    Len = shape[0]*shape[1]*shape[2]
    tupleData = struct.unpack(str(Len)+'f',file.read(FLOATSIZE*Len))
    file.close()
    data = np.array(tupleData).reshape(shape[1],shape[2],shape[0])
    
    return shape,data

def calcGamma(rp,tp,dose,Tdose,square_of_distance2Agree,square_of_doseCriteria):
    return(sum((rp - tp)**2)/square_of_distance2Agree + (1 - Tdose/dose)**2/(square_of_doseCriteria))


"""
argv[1]: reference data file
argv[2]: testing data file
argv[3]: distance to agreement, e.g 2mm
argv[4]: percentage to meet criteria, unit is percentage, like 2 percentage
argv[5]: comparison type, 3 kinds, local, max, selected. **only support local for now
argv[6]: grid spacing, unit mm
"""                  
#CompareType = ('Local', 'Max', 'Selected')
cmType = argv[5]
if (cmType.lower() != 'local'):
    print("only LOCAL is supported")
    sys.exit(0)
rshape, rdata = read_bin(argv[1]) # reference data
#data[:,:] = 20.0
tshape,tdata = read_bin(argv[2]) # testing data
if not (rshape[0]==tshape[0] and rshape[1]==tshape[1] and rshape[2]==tshape[2]):
    print('the two copy of datas don\'t match')
    sys.exit(0)
Distance2Agree = float(argv[3]) # unit is mm
squaredDIS = Distance2Agree * Distance2Agree
DoseCriteria = float(argv[4])/100.0 # unit is percentage

gridspacing = float(argv[6]) # unit is mm

configs = open('GammaIndexconfig.txt')
configs.readline()
#doseLowest is the lowest dose that will be considered
doseLowest = float(configs.readline())
#print(doseCriteria)
configs.readline()
#searchRadius is the searching radius that find the dose point meets the Distance2Agree and percentage agreement
searchRadius = int(configs.readline())

NsquaredDIS = squaredDIS/(gridspacing)**2#translate to dose grid
squaredDose = DoseCriteria * DoseCriteria
doseL = np.max(rdata) * doseLowest
failedNUM = 0
totalPoints = 0
GAMMAINDEX = 1.0
#points = []
#for i in range (shape[1]):
#    for j in range(shape[2]):
#        for k in range(shape[0]):
#            points.append(np.array([i,j,k]))

def MPgothrough(point):
    global GAMMAINDEX, searchRadius,NsquaredDIS,squaredDose,doseL
    global rshape,rdata,tdata
    totalpoint = 0
    failedpoint = 0
                      
    for j in range(rshape[2]):
        for k in range(rshape[0]):
            if rdata[point][j][k] >= doseL or tdata[point][j][k] >= doseL:
                break_ = False
                totalpoint = totalpoint + 1
                for ti in range(max(point - searchRadius, 0),min(point + searchRadius, rshape[1])):
                    for tj in range(max(j - searchRadius, 0), min(j + searchRadius, rshape[2])):
                        for tk in range(max(k - searchRadius, 0), min(k + searchRadius, rshape[0])):
                             tpi = np.array([ti, tj, tk])
                             calc = calcGamma(np.array([point,j,k]),tpi,max(rdata[point][j][k], doseL),tdata[tpi[0]][tpi[1]][tpi[2]],NsquaredDIS,squaredDose)
                             if ( GAMMAINDEX >= calc):
                                 break_ = True
                                 break
                        if(break_):
                            break
                    if(break_):
                        break
                    failedpoint = failedpoint + 1
    return totalpoint, failedpoint

points = range(rshape[1])            
cores = multiprocessing.cpu_count()
cores = 4
pool = multiprocessing.Pool(processes=cores)
sum1,sum2 = sum(pool.map(MPgothrough, points))
        



#filepath = ((argv[2].replace("\\","_")).replace("/","_")).replace(":","_")
file = open("C:/aGammaIndex.txt","w+") 
#print("c:/"+filepath+"GAMMAINDEX.txt") 
#file = open("c:/"+filepath+"GAMMAINDEX.txt","w+")
file.write("%s \r"%(argv[2]))
file.write("%s %f mm %f, dose lower than %f * maxdose is ignored \r"%(cmType, Distance2Agree, DoseCriteria*100, doseLowest))
file.write("%d points failed, total points considered is %d, passing rate is %f.\r"%(failedNUM, totalPoints, (1- (float(failedNUM)/float(totalPoints)))*100))
file.close()


