from enum import Enum

file_dir ="D:/Caroline/Test Data/CSLog/PlanParametersRequest"
# Dependency type.
class DependencyType(Enum):   
    eOFFSET_NONE = 0
    eOFFSET_BEAM = 1
    eOFFSET_DOSE = 2
    
class NuclearInteraction(Enum):
    ePatient = 1
    ePhantom = 2
    eOff = 3
    
class SpotMode(Enum):
    eTargetToPrescribed = 1    # Target to be Prescribed 
    eBeamTarget = 2             # Beam target

class CalculationAlgorithm(Enum):
    eUnkown = 0
    ePBA = 1   # Kernal generation
    ePBSA = 2   # Pencil Beam Sub-Spot Algorithm. Final calculation.
           
# Offset beam information.
class OffsetBeamInfo:
    def __init__(self): 
        self.nBeamNum = 1
        self.nFractions = 1
        self.dependencyType = DependencyType(0)

           
m_strFileVersion= "000510d7"
m_strPatientID = "BS001EKK"
m_nPatBitNum = 0 # ROI number representing the patient outline among the ROI number defined in ROI bitmap file.
m_nOffsetDose = 2 # The identification flag for the exist ence of offset dose.
                        # 1: offset beam was set 2: offset beam was not set
m_nGridDimX= 251
m_nGridDimY= 190
m_nGridDimZ= 226
m_voxelSizeX = 2
m_voxelSizeY = 2
m_voxelSizeZ = 2
        
m_arrOffsetBeamInfo = OffsetBeamInfo(1,1,DependencyType(0))
m_strPlanID= "T25N30_A"
m_fractionDose = 0
m_strRbeModeID= "NIRS_MKM"
m_rlMargin= 1  # Margin for target respiratory motion in RL
m_apMargin= 1  # Margin for target respiratory motion in AP
m_fhMargin = 1 # Margin for target respiratory motion in FH

m_scalingFactor= 1  # Predicted-Dose scaling factor
nNuclearInteraction = 1  # ePatient=1, ePhantom=2, eOff=3
m_nNucleareraction = NuclearInteraction(nNuclearInteraction)
nSpotMode= 1  # TargetTobePrescribed =1, BeamTarget =2
m_nSpotMode = SpotMode(nSpotMode)

m_nCalcAlgo = CalculationAlgorithm(2)

m_nKernelGenerationPrecision= 3  # Sub spot precision of kernel dose generation.
m_nFinalCalculationPrecision= 3  # Sub spot precision of final dose calculation.

m_nEnergyChange= 1  # NOT USED: Permission to change the beam energy  within same IMIT group.
m_nBeamSizeChange= 1  # NOT USED: Permission to change the beam size within same IMIT group.
m_nRidgeFilterChange= 1  # NOT USED: Permission to change the Ridge Filter within same IMIT group.

m_arrBeamNums = 1 # Array of beam number for the beams listed in the Plan param file, current Rx's Beams, MFSO beams and bias Dose beams.
m_arrPrescribedTarget= 1 
m_arrPrescribedOAR= 1    
m_convEps= 1  # Convergence Criterion defined to stop the optimization iteration.
m_nMaxIterations= 1  # Maximum Iteration Number defined to stop the optimization iteration.
m_strCalcStatus= 1 
m_strCalcMessage= 1
