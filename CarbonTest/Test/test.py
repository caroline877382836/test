import time
import logging
import spotPlacement
strDataFolder = "D:/Caroline/Test Data/CSLog"
strLocalFilesFolder = "D:/Caroline/Test Data/IDOSE/IDOSELocalFiles"

# TODO: whether needs opt depends on kernel genereton or not
needsOptimization = True

if __name__ == '__main__':
    try:
        startTime = time.time()
        if (needsOptimization):
            # TODO   spotPlacement.placeSpots()
            # TODO   optimizeTrajectoryPath()
            # TODO   computeKernelDose()
            # TODO   weightOptimizer( pPatientData, funcPhysicalToClinic )
            # TODO   weightOptimizer.optimize()

    # TODO doseEngine.computeFinalDose()
         endTime = time.time()
         spentTime = endTime - startTime
    except:
        logging.warning( "Error" )
        logging.error( "Calculation fail!" )