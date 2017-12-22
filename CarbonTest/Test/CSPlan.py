#include "CSPlan.h"

#include <algorithm>
#include "Utility\Grid3D.h"
#include "FileIO/PlanParam.h"
#include "FileIO/BeamParam.h"
#include "FileIO/FileStore.h"
#include "CSBeam.h"
#include "PatientModel.h"
#include "CSLayer.h"
#include "CSSpot.h"
#include "DeliveryMode.h"
#include "RoiTable.h"

using namespace std;

using CSD::Utility::Grid3D;
using CSD::FileIO::PlanParam;
using CSD::FileIO::FileStore;
using CSD::FileIO::PlanParam;
using CSD::FileIO::PrescribedOAR;
using CSD::FileIO::PrescribedTarget;

namespace CSD {
    
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::CSPlan
//
//  Constructor.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
CSPlan::CSPlan( const PlanParam& planParam, shared_ptr<const PatientModel> pPatientModel )
    : PlanData(planParam, pPatientModel)
{
    for ( auto nBeamNmbr: planParam.getBeamsRequested() )
    {
        auto pBeamParam = FileStore::getFileStore().getBeamParam( nBeamNmbr );

        if ( pBeamParam->getBeamNum() != nBeamNmbr )
        {
            addWarningMessage( "Warning:: Beam-" + to_string(nBeamNmbr) + " has mismatched beam number in request file!" );
            pBeamParam->setBeamNum( nBeamNmbr );
        }

        m_arrBeamDatas.push_back( make_shared<CSBeam>(*pBeamParam, this) );
    }
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::~CSPlan
//
//  De-constructor.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
CSPlan::~CSPlan(void)
{
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::getBeamData
//
//  Get all beam data in this plan.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
vector<shared_ptr<CSBeam>> CSPlan::getBeamData()
{
    return m_arrBeamDatas;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::getBeamData
//
//  Get a beam data.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
shared_ptr<const CSBeam> CSPlan::getBeamData( int nBeamNmbr ) const
{
    shared_ptr<const CSBeam> pBeamData;
    for ( auto pBeam: m_arrBeamDatas )
    {
        if ( pBeam->getBeamNmbr() == nBeamNmbr )
        {
            pBeamData = pBeam;
            break;
        }
    }
    return pBeamData;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::getBeamData
//
//  Get a beam data.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
shared_ptr<CSBeam> CSPlan::getBeamData( int nBeamNmbr )
{
    shared_ptr<CSBeam> pBeamData;
    for ( auto pBeam: m_arrBeamDatas )
    {
        if ( pBeam->getBeamNmbr() == nBeamNmbr )
        {
            pBeamData = pBeam;
            break;
        }
    }
    return pBeamData;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::writeDoseResult
//
//  Write dose result to file for Monaco.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void CSPlan::writeDoseResult() const
{
    auto& fileStore = FileStore::getFileStore();

    for ( auto& pBeam: m_arrBeamDatas )
    {
        // Kernel generation.
        if ( pBeam->getPhysicalDose() == nullptr || pBeam->getEffectiveDose() == nullptr )
        {
            auto& patientModel = getPatientModel();
            auto pPhysicalDose = make_shared<Grid3D<float>>( 
                patientModel.getWidth(), patientModel.getHeight(), patientModel.getDepth() );
            pPhysicalDose->initialize(0.0f);

            auto pEffectiveDose = make_shared<Grid3D<float>>( *pPhysicalDose );

            auto arrSpots = pBeam->getAllSpots();
            for( const auto pSpot: arrSpots )
            {
                const auto& arrDoseIndex = pSpot->getKernelDoseIndexes();
                const auto& arrEffDose = pSpot->getKernelZDose();
                const auto& arrPhysicalDose = pSpot->getKernelPhyDose();
                auto nSize = pSpot->getSizeOfDose();

                for( int i = 0; i < nSize; ++i )
                {
                    pPhysicalDose->operator[](arrDoseIndex[i]) += arrPhysicalDose[i];
                    pEffectiveDose->operator[](arrDoseIndex[i]) += arrEffDose[i];
                }
            }

            pBeam->setPhysicalDose( pPhysicalDose );
            pBeam->setEffectiveDose( pEffectiveDose );
        }

        fileStore.savePhysicalDose( *pBeam->getPhysicalDose(), pBeam->getBeamNmbr() );
        fileStore.saveEffectiveDose( *pBeam->getEffectiveDose(), pBeam->getBeamNmbr() );
    }
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::getAllBeamNmbrs
//
//  Get all beam numbers in this plan.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
vector<int> CSPlan::getAllBeamNmbrs() const
{
    vector<int> arrBeamNmbrs( m_arrBeamDatas.size() );

    transform( m_arrBeamDatas.begin(), m_arrBeamDatas.end(), arrBeamNmbrs.begin(),
        []( shared_ptr<const BeamData> pBeam ) { return pBeam->getBeamNmbr(); } );

    return arrBeamNmbrs;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::getOptBeamNmbrs
//
//  Get beam numbers need to be optimized.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
vector<int> CSPlan::getOptBeamNmbrs() const
{
    vector<int> arrBeamNmbrs;

    for ( auto pBeam: m_arrBeamDatas )
    {
        if ( pBeam->needsOptimization() )
        {
            arrBeamNmbrs.push_back( pBeam->getBeamNmbr() );
        }
    }

    return arrBeamNmbrs;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::needsOptimization
//
//  check current plan needs kernel generation or not
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
bool CSPlan::needsOptimization() const
{
    for ( auto beam : m_arrBeamDatas )
    {
        if ( beam->needsOptimization() ) // if any beam needs kernel generation, then the plan needs kernel generation
        {
            return true;
        }
    }
    return false;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::hasOffsetBeam
//
//  Check if there is any offset beam in this plan.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
bool CSPlan::hasOffsetBeam() const
{
    for ( auto beam : m_arrBeamDatas )
    {
        if ( beam->isMFSOBeam() )
        {
            return true;
        }
    }

    return false;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::getDeliveryMode
//
//  Get the delivery mode.
//  Currently, just check the mode according to the number of optimized beam.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
DeliveryMode CSPlan::getDeliveryMode() const
{
    return getOptBeamNmbrs().size() > 1 ? DeliveryMode::eIMPT : DeliveryMode::eSFUD;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::getSpotCnt
//
//  Get number of spot in this plan.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
int CSPlan::getSpotCnt() const
{
    int nAllSpotNum = 0;

    for ( auto beam : m_arrBeamDatas )
    {
        nAllSpotNum += beam->getAllSpotsNum();
    }

    return nAllSpotNum;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::getLayerCnt
//
//  Get number of layers in this plan.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
int CSPlan::getLayerCnt() const
{
    int nLayerCnt = 0;

    for ( auto beam : m_arrBeamDatas )
    {
        nLayerCnt += static_cast<int>( beam->getAllLayers().size() );
    }

    return nLayerCnt;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::getMFSOPhyDose
//
//  Get MFSO physical dose.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const vector<float>& CSPlan::getMFSOPhyDose() const
{
    if ( hasOffsetBeam() && m_arrMFSOPhyDose.empty() )
    {
        createMFSODose();
    }

    return m_arrMFSOPhyDose;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::getMFSOZDose
//
//  Get MFSO Zn dose.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const vector<float>& CSPlan::getMFSOZDose() const
{
    if ( hasOffsetBeam() && m_arrMFSOZDose.empty() )
    {
        createMFSODose();
    }

    return m_arrMFSOZDose;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::createBiasDose
//
//  Create bias dose.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void CSPlan::createBiasDose() const
{
    auto& fileStore = FileStore::getFileStore();
    auto pOffsetPhyDose = fileStore.getOffsetPhysicalDose();
    auto pOffsetEffDose = fileStore.getOffsetEffectiveDose();

    const auto& doseAssignedIndex = getExtentedPropertyGrid().getRoiIndex();
    const int nVoxelNum = static_cast<int>( doseAssignedIndex.size() ); 
    m_arrBiasPhyDose.resize( nVoxelNum );
    m_arrBiasClinDose.resize( nVoxelNum );

#pragma omp parallel for
    for ( int i = 0; i < nVoxelNum; ++i )
    {
        const int nIndex = doseAssignedIndex[i];
        m_arrBiasPhyDose[i] = (*pOffsetPhyDose)[nIndex];
        m_arrBiasClinDose[i] = (*pOffsetEffDose)[nIndex];
    }
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::createMFSODose
//
//  Create MFSO beam dose.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
void CSPlan::createMFSODose() const
{
    const auto& doseAssignedIndex = getExtentedPropertyGrid().getRoiIndex();
    m_arrMFSOPhyDose.assign( doseAssignedIndex.size(), 0.0f );
    m_arrMFSOZDose.assign( doseAssignedIndex.size(), 0.0f );

    for ( const auto beam : m_arrBeamDatas )
    {
        if ( beam->isMFSOBeam() )
        {
            for ( auto spot: beam->getAllSpots() )
            {
                auto nSize = spot->getSizeOfDose();
                auto arrTmpDoseIndexes = spot->getKernelDoseIndexes();
                auto arrTmpPhyDose = spot->getKernelPhyDose();
                auto arrTmpZDose = spot->getKernelZDose();
#pragma omp parallel for
                for ( int ii = 0; ii < nSize; ++ii )
                {
                    m_arrMFSOPhyDose[arrTmpDoseIndexes[ii]] += arrTmpPhyDose[ii];
                    m_arrMFSOZDose[arrTmpDoseIndexes[ii]] += arrTmpZDose[ii];
                }
            }
        }
    }
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::estimatePrescribedDosePerBeam
//
//  Roughly estimate the prescribed dose for each beam.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
vector<double> CSPlan::estimatePrescribedDosePerBeam() const
{
    map<int,int> mapOptTargetCount;    // <targetNum,count>
    map<int,double> mapMFSOTargetDose; // <targetNum,meanDose>
    for ( auto beam : m_arrBeamDatas )
    {
        int nTargetNum = beam->getTargetNum();
        if ( beam->needsOptimization() )
        {
            if ( mapOptTargetCount.find( nTargetNum ) == mapOptTargetCount.end() )
            {
                mapOptTargetCount.insert( make_pair( nTargetNum, 0 ) );
            }
            mapOptTargetCount[nTargetNum]++;
        }
        else
        {
            if ( mapMFSOTargetDose.find( nTargetNum ) == mapMFSOTargetDose.end() )
            {
                mapMFSOTargetDose.insert( make_pair( nTargetNum, 0.0 ) );
            }
            mapMFSOTargetDose[nTargetNum] += beam->getMeanEffectiveDose();
        }
    }

    const auto& roiTable = getPatientModel().getPropertyGrid().getPropertyTable();
    auto arrOptBeamNum = getOptBeamNmbrs();
    vector<double> arrPrescribedDoses( arrOptBeamNum.size(), 0 );
    auto& targets = getPrescribedTarget();
#pragma omp parallel for
    for ( int i = 0; i < arrOptBeamNum.size(); ++i )
    {
        auto beam = getBeamData( arrOptBeamNum[i] );
        int nTargetNum = beam->getTargetNum();

        double prescribedTotalDose = 0;
        for ( const auto& target : targets )
        {
            if ( target.nBitNum == roiTable->getBitNum( nTargetNum ) )
            {
                prescribedTotalDose = target.goalDose;
                if ( prescribedTotalDose < target.minimumDose || prescribedTotalDose > target.maxDose )
                {
                    prescribedTotalDose = ( target.minimumDose + target.maxDose )*0.5;
                }
                break;
            }
        }

        const double prescribedOptDose = prescribedTotalDose - mapMFSOTargetDose[nTargetNum];
        arrPrescribedDoses[i] = prescribedOptDose > 0 ? 
            prescribedOptDose/mapOptTargetCount[nTargetNum] : prescribedTotalDose;
    }

    return arrPrescribedDoses;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::getBiasPhyDose
//
//  Get bias physical dose.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const vector<float>& CSPlan::getBiasPhyDose() const
{
    if ( hasOffsetDose() && m_arrBiasPhyDose.empty() )
    {
        createBiasDose();
    }

    return m_arrBiasPhyDose;
}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  Function: CSPlan::getBiasClinDose
//
//  Get bias clinic dose.
//
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
const vector<float>& CSPlan::getBiasClinDose() const
{
    if ( hasOffsetDose() && m_arrBiasClinDose.empty() )
    {
        createBiasDose();
    }

    return m_arrBiasClinDose;
}
}