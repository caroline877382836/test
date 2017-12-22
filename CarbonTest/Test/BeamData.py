m_strFileVersion = "000410d8"
m_nBeamNumr = 1  # number of beams
m_nGroupNum = -1

m_strMachineID = "NVC"
m_strIonType = "CARBON"

SCALING_FACTOR = 1.0
SCAN_MODE      = "HYBRID"
m_strLongSt = SCAN_MODE
m_ptIsoCenter = [240.0,54.0,238.0]
m_IsoToSkin = 228.185761
m_matrixBeamToPatient = [0.939692621,0.342020143,0.0,0.000000000,0.0,1.0,0.342020143,-0.939692621,0.0]
m_stepX = 2                   #scan step size in horizontal
m_stepY  = 2                  #scan step size in vertical 
m_sliceThickness = 2          #slice thickness

m_marginLateral = 0           #lateral margin
m_marginDistal = 0            #distal margin 
m_marginProximal = 0          #proximal margin 
m_nominalBeamIntensity = 600000000.0    #nominal beam intensity
m_avgRespiCycle = 0.0
m_gantingDutyStart = 0.0
m_gantingDutyEnd = 0.0

m_nSweeps =  1    #number of sweeps
m_nGauss = 3
m_radiusProximalSmearing= 0.0   #Proximal smearing radius
m_radiusDistalSmearing= 4.0     #Distal smearing radius

m_maxEnergy                 =  -1
m_maxRange                  =  -1
m_targetMinWeqDepth         = -1
m_targetMaxWeqDepth         = -1
m_targetWeqThickness        = -1 
m_targetMaxOffaxisDist      = -1 #target maximum off-axis distance
m_fieldArea                 = -1 #beam field area at isocenter plane
m_nominalTreatedVol = -1

m_minXPos =0.0
m_maxXPos = 0.0
m_minYPos = 0.0
m_maxYPos = 0.0

m_maxParticles  = -1
m_nTargetNbr  =   17    

m_strTargetName             = "OTV2b"     
m_targetVolume              = -1
m_targetMeanPhyDose         = -1
m_targetMeanEffDose         = -1
m_targetMeanRbe             = -1
m_strEffectiveDoseFile      = "Optimization"
m_strPhysicalDoseFile       = "Optimization"               

#check if the beam need optimization by the name of dose file
if ( m_strPhysicalDoseFile == "Optimization" ):
    m_bNeedOptimization  = 1
else:
    m_bNeedOptimization  = 0
    
m_totalParticle     = -1
m_nTotalSpotParams  = -1
m_strRbeModelID     ="NIRS_MKM"
m_scalingFactor     = -1
nCntOfShots         = 1  
 


m_sid= 1 

m_targetMeanPhyDose = 0.0       # target mean physical dose 
m_targetMeanEffDose = 0.0       # target mean effective dose 
m_targetMeanRbe = 0.0         # target mean rbe 
    
m_targetMinWeqDepth = 1       #target minimum water equivalent depth 
m_targetMaxWeqDepth  = 1      #target maximum water equivalent depth 
m_strRFID = 1                 #ridge filter ID
m_targetMaxWeqThickness= 1    #target maximum water equivalent thickness
m_maxTargetOffaxisDist = 1    #target maximum off-axis distance
m_nominalTreatedVolume = 1    #nominal treated 