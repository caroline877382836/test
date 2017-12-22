import logging
import patientData
import AppConfig
import BeamData


def placeSpots(needsOptimization):
    if ( not needsOptimization ):
        logging.info("No need spot placement!")
        return
    try:
        doTargetExpansion()
        doSpotPlacement()
    except:
        logging.error( "Error" )
        logging.error( "Calculation fail!" )

def doTargetExpansion():
    m_mapPFinalTargetBitMap = getExtentedTargetGrid()
    saveExtendedRoiBitMap()
    
def saveExtendedRoiBitMap():
     const auto& arrBeamNumbers = m_pPatientData->getPlanData()->getAllBeamNmbrs();

    const auto& gridProperty = m_pPatientData->getPatientModel().getPropertyGrid();
    const int nSize = gridProperty.getNVertices();

    const auto targetRxSetting1 = AppConfig::getConfig().getOptStage1TargetRxSetting();
    const auto targetRxSetting2 = AppConfig::getConfig().getOptStage2TargetRxSetting();
    const auto targetRxSettingFinal = AppConfig::getConfig().getFinalOptTargetRxSetting();
    if ( targetRxSetting1 == TargetRxSetting::eExtendedGoalDose ||
        targetRxSetting1 == TargetRxSetting::eExtendedNormalRx ||
        targetRxSetting2 == TargetRxSetting::eExtendedGoalDose || 
        targetRxSetting2 == TargetRxSetting::eExtendedNormalRx ||
        targetRxSettingFinal == TargetRxSetting::eExtendedGoalDose || 
        targetRxSettingFinal == TargetRxSetting::eExtendedNormalRx ||
        targetRxSettingFinal == TargetRxSetting::eExtendedMaxDose )
    {
        auto pPlanPropertryGrid = make_shared<PropertyGrid3D>( *(m_mapPFinalTargetBitMap.begin()->second), gridProperty.getPropertyTable() );

        for ( int nBeamNmb: arrBeamNumbers )
        {
            const auto& extendedBeamTarget = *m_mapPFinalTargetBitMap[nBeamNmb];

#pragma omp parallel for
            for ( int i = 0; i < nSize; ++i )
            {
                pPlanPropertryGrid->operator[](i) |= extendedBeamTarget[i];
            }
        }
        
        m_pPatientData->getPlanData()->setExtentedPropertyGrid( pPlanPropertryGrid );  
    }

    const auto& extentedPropertyGrid = m_pPatientData->getPlanData()->getExtentedPropertyGrid();
    for ( int nBeamNmb: arrBeamNumbers )
    {
        const auto& beamPropertyGrid = *m_mapPFinalTargetBitMap[nBeamNmb];

        const auto& roiIndex = extentedPropertyGrid.getRoiIndex();
        vector<VoxelProperty> arrPropertyIndex( roiIndex.size() );
        
#pragma omp parallel for
        for (int i = 0; i < arrPropertyIndex.size(); i++)
        {
            const int idx = roiIndex[i];
            arrPropertyIndex[i] = beamPropertyGrid[idx] & (~gridProperty[idx]);
        }

        m_pPatientData->getPlanData()->getBeamData(nBeamNmb)->setExtendedRoiIndex( move(arrPropertyIndex) );
    }
      
def doSpotPlacement():
    startTime = time.clock()

    # loop for all beams
    for ( auto beamNum : m_pPatientData->getPlanData()->getAllBeamNmbrs() )
    {
        m_nCurrentBeamNum = beamNum;
        auto pBeam = m_pPatientData->getPlanData()->getBeamData( m_nCurrentBeamNum );
        if ( !pBeam->needsOptimization() )
        {
            continue;
        }
        LoggerInstance::writeConsole( "Spot Arrangement For Beam-" + to_string(beamNum) );

        # build 2D boolean grid
        build2DPorjectionGrid();

        VoxelProperty checkNum = getRoiCheckNum(beamNum);
        # projection beam 3D target and OAR to 2D     
        Projection3DTo2D projector( m_pTargetProjectionGrid, *(m_mapPFinalTargetBitMap[beamNum]), 
            m_pPatientData->getGridSize(), checkNum, pBeam->getMatrixBeamToPatient() );
        projector.doProjection();

        # Cut target out of field.
        cutTargetOutField();

        # loop for 2D grid, do ray trace
        rayTraceThroughTarget();
        
        # to calculate minRange, maxRange and weqThickness 
        const auto originalProjperty3DGrid = m_pPatientData->getPatientModel().getPropertyGrid();
        Projection3DTo2D projectorOriginal( m_pOriginalTargetProjectionGrid, originalProjperty3DGrid, 
            m_pPatientData->getGridSize(), checkNum, pBeam->getMatrixBeamToPatient() );
        projectorOriginal.doProjection();

        rayTraceThroughOriginalTarget();

        # initialize discrete layer(beam model), from maximum to minimum range
        buildDiscreteRangeMap();

        # loop for Vector<coord2D>
        buildLayerData();

        # calculate the field area
        double projection2DGridArea = m_nFieldAreaGridCount * ( m_pTargetProjectionGrid->getIUnit() * m_pTargetProjectionGrid->getJUnit() );

        pBeam->setFieldArea( projection2DGridArea );
        pBeam->setNominalTreatedVolume( projector.getNominalTreatedVolume() );        
        pBeam->setTargetMaxOffaxisDist( m_maxTargetOffaxisDist );

        bool hasNoSpot = true;
        # set LayerData into beam
        pBeam->removeAllLayers();
        for( auto rIter = m_mapLayerData.rbegin(); 
             rIter != m_mapLayerData.rend();
             ++rIter )
        {
            pBeam->addLayerData( rIter->second );   

            hasNoSpot &= rIter->second->getSpotDatas().empty();

            LoggerInstance::writeConsole( "depth:: " + to_string( (*rIter).first ) + "mm # spot:: " + 
                to_string((*rIter).second->getSpotDatas().size()) );
        }
        
        if( hasNoSpot )
        {
            LoggerInstance::writeConsole( "Error::No spot can be placed to the target, calculation will be aborted!" );
            throw exception();
        }
    }
    m_mapPFinalTargetBitMap.clear();
    clock_t endTime = clock();
    const double spentTime = static_cast<double>(endTime - startTime) / CLOCKS_PER_SEC;
    LoggerInstance::writeConsole( "TIME FOR SPOT ARRANGEMENT: " + to_string(spentTime) + " [sec]" );

def getExtentedTargetGrid():
    try:
        gridSize = patientData.GridSize
        rayTraceResolution = gridSize * AppConfig.rayTraceResolution
        lateralMarginCheckOption = AppConfig.LateralMarginCheckMethod(1)  #eCenterCheckPlus1Spot
        #auto pPlan = m_pPatientData->getPlanData()
        arrBeamNums = BeamData.m_nBeamNumr
        spotMode = PlanPara.m_nSpotMode
        const auto& roiTable = m_pPatientData->getPatientModel().getPropertyGrid().getPropertyTable()

        set<int> setTargetBitNum
        if ( spotMode == CSD::SpotMode::eTargetToPrescribed )
        {
            const auto& arrPrescribedTarget = pPlan->getPrescribedTarget()
            for ( auto target: arrPrescribedTarget )
            {
                setTargetBitNum.insert( target.nBitNum )
            }
        }

        OarSubtraction oarSubtractor( m_pPatientData )

        for ( int nBeamNum: arrBeamNums )
        {
            auto pBeam = pPlan->getBeamData( nBeamNum )
            if ( !pBeam->needsOptimization() )
            {
                continue
            }

            const double beamSid = pBeam->getSid()
            const double proximalMargin = pBeam->getProximalMargin()
            const double distalMargin = pBeam->getDistalMargin()
            const double proximalRadius = pBeam->getProximalSmearingRadius()
            const double distalRadius = pBeam->getDistalSmearingRadius()
            double marginLateral = pBeam->getLateralMargin()
            if ( LateralMarginCheckMethod::eCenterCheckPlus1Spot == lateralMarginCheckOption )
            {
                marginLateral += gridSize
            }
            const auto& matrixBeamToPatient = pBeam->getMatrixBeamToPatient()

            # initialize target set for current beam
            if ( spotMode == CSD::SpotMode::eBeamTarget )
            {
                setTargetBitNum.clear()
                setTargetBitNum.insert( roiTable->getBitNum( pBeam->getTargetNum() ) )
            }

            if ( marginLateral < 0.0 )
            {
                LoggerInstance::writeConsole( "Error::Lateral margin is less than zero, stop calculation." )
                throw exception()
            }

            # Do extension
            auto pExtensionLateral = ExtensionLateral::buildExtensionlateral ( 
                inverse( matrixBeamToPatient ), *(m_mapTargetGrid[nBeamNum]), gridSize, marginLateral, lateralMarginCheckOption )
            for ( const auto& nTargetBitNum: setTargetBitNum )
            {
                const VoxelProperty nTargetCheckValue = ( 1 << nTargetBitNum )
                # subtract OAR 1st time
                oarSubtractor.doSubtraction( *m_mapTargetGrid[nBeamNum], nTargetBitNum )

                if ( pExtensionLateral != nullptr )
                {
                    # Lateral extension.
                    pExtensionLateral->doExtension( nTargetCheckValue )
                }

                # subtract OAR 2nd time
                oarSubtractor.doSubtraction( *m_mapTargetGrid[nBeamNum], nTargetBitNum )

                # Construct 2D spot grid.
                const auto vecFieldSize = pBeam->getFieldSize()
                auto pGridSpot = calcSpotGrid(nBeamNum, vecFieldSize, rayTraceResolution, nTargetCheckValue, matrixBeamToPatient)

                # Ray trace.
                auto gridRayPath = calcRayTracePath(nBeamNum, pGridSpot, matrixBeamToPatient, nTargetCheckValue, beamSid)

                if ( !cms::isZero( proximalMargin ) || !cms::isZero( distalMargin ) )
                {
                    # Proximal and distal margin.
                    ExtensionProximalDistal extensionProDist( *(m_mapTargetGrid[nBeamNum]), gridSize, gridRayPath )
                    extensionProDist.doExtension( proximalMargin, distalMargin, nTargetCheckValue )
                }

                if ( !cms::isZero( proximalRadius ) || !cms::isZero( distalRadius ) )
                {
                    # Smearing margin.
                    ExtensionSmearing exntensionSmearing( *(m_mapTargetGrid[nBeamNum]), gridSize, gridRayPath, rayTraceResolution )
                    exntensionSmearing.doExtension( proximalRadius, distalRadius, nTargetCheckValue )
                }
                # subtract OAR 3rd time
                oarSubtractor.doSubtraction( *m_mapTargetGrid[nBeamNum], nTargetBitNum )
            }
        }

        return m_mapTargetGrid
    }
    except ValueError:
        logging.error( "Could not get extended target grid" )