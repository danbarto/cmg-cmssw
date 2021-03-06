import FWCore.ParameterSet.Config as cms

# Define the CMSSW process
process = cms.Process("RERUN")

# Load the standard set of configuration modules
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

# Message Logger settings
process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.destinations = ['cout', 'cerr']
process.MessageLogger.cerr.FwkReport.reportEvery = 1

# Set the process options -- Display summary at the end, enable unscheduled execution
process.options = cms.untracked.PSet( 
    allowUnscheduled = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False) 
)

# How many events to process
process.maxEvents = cms.untracked.PSet( 
   input = cms.untracked.int32(10)
)

#configurable options =======================================================================
runOnData=False #data/MC switch
usePrivateSQlite=True #use external JECs (sqlite file)
useHFCandidates=True #create an additionnal NoHF slimmed MET collection if the option is set to false
redoPuppi=True # rebuild puppiMET
#===================================================================


### External JECs =====================================================================================================

#from Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff import *
#process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag_condDBv2 import GlobalTag
#from Configuration.AlCa.autoCond import autoCond
if runOnData:
  process.GlobalTag.globaltag =  cms.string('80X_dataRun2_Prompt_ICHEP16JEC_v0')
else:
  process.GlobalTag.globaltag =  cms.string('80X_mcRun2_asymptotic_2016_miniAODv2_v1')


if usePrivateSQlite:
    from CondCore.DBCommon.CondDBSetup_cfi import *
    import os
    if runOnData:
      era="Spring16_25nsV6_DATA"
    else:
      era="Spring16_25nsV6_MC"
    jerera="Spring16_25nsV6"

##___________________________External JEC file________________________________||

    process.jec = cms.ESSource("PoolDBESSource",CondDBSetup,
                               connect = cms.string("sqlite:PhysicsTools/PatUtils/data/"+era+".db"),
                               toGet =  cms.VPSet(
            cms.PSet(
                record = cms.string("JetCorrectionsRecord"),
                tag = cms.string("JetCorrectorParametersCollection_"+era+"_AK4PF"),
                label= cms.untracked.string("AK4PF")
                ),
            cms.PSet(
                record = cms.string("JetCorrectionsRecord"),
                tag = cms.string("JetCorrectorParametersCollection_"+era+"_AK4PFchs"),
                label= cms.untracked.string("AK4PFchs")
                ),
            cms.PSet(record  = cms.string("JetCorrectionsRecord"),
                tag     = cms.string("JetCorrectorParametersCollection_"+era+"_AK4PFPuppi"),
                label   = cms.untracked.string("AK4PFPuppi")
                ),
            )
                               )
    process.es_prefer_jec = cms.ESPrefer("PoolDBESSource",'jec')

##___________________________External JER file________________________________||

    process.jer = cms.ESSource("PoolDBESSource",CondDBSetup,
                               connect = cms.string("sqlite:PhysicsTools/PatUtils/data/JER/"+jerera+"_MC.db"),
                               toGet =  cms.VPSet(
        #######
        ### read the PFchs

        cms.PSet(
          record = cms.string('JetResolutionRcd'),
          tag    = cms.string('JR_'+jerera+'_MC_PtResolution_AK4PFchs'),
          label  = cms.untracked.string('AK4PFchs_pt')
          ),
        cms.PSet(
          record = cms.string("JetResolutionRcd"),
          tag    = cms.string('JR_'+jerera+'_MC_PhiResolution_AK4PFchs'),
          label  = cms.untracked.string("AK4PFchs_phi")
          ),
        cms.PSet(
          record = cms.string('JetResolutionScaleFactorRcd'),
          tag    = cms.string('JR_'+jerera+'_MC_SF_AK4PFchs'),
          label  = cms.untracked.string('AK4PFchs')
          ),

        #######
        ### read the Puppi JER

        cms.PSet(
          record = cms.string('JetResolutionRcd'),
          tag    = cms.string('JR_'+jerera+'_MC_PtResolution_AK4PFPuppi'),
          label  = cms.untracked.string('AK4PFPuppi_pt')
          ),
        cms.PSet(
          record = cms.string("JetResolutionRcd"),
          tag = cms.string('JR_'+jerera+'_MC_PhiResolution_AK4PFPuppi'),
          label= cms.untracked.string("AK4PFPuppi_phi")
          ),
        cms.PSet(
          record = cms.string('JetResolutionScaleFactorRcd'),
          tag    = cms.string('JR_'+jerera+'_MC_SF_AK4PFPuppi'),
          label  = cms.untracked.string('AK4PFPuppi')
          ),

        ) )

    process.es_prefer_jer = cms.ESPrefer("PoolDBESSource",'jer')


### =====================================================================================================
# Define the input source
if runOnData:
  fname = 'root://eoscms.cern.ch//store/relval/CMSSW_8_0_11/SinglePhoton/MINIAOD/80X_dataRun2_relval_v12_RelVal_sigPh2015D-v2/10000/62F5F051-ED35-E611-BD3C-0CC47A4D76C8.root'
else:
  fname = 'root://eoscms.cern.ch//store/relval/CMSSW_8_0_11/RelValTTbar_13/MINIAODSIM/80X_mcRun2_asymptotic_v14-v1/10000/863A92CE-C134-E611-9989-0CC47A4D760C.root'

# Define the input source
process.source = cms.Source("PoolSource", 
    fileNames = cms.untracked.vstring([ fname ])
)


### ---------------------------------------------------------------------------
### Removing the HF from the MET computation
### ---------------------------------------------------------------------------
if not useHFCandidates:
    process.noHFCands = cms.EDFilter("CandPtrSelector",
                                     src=cms.InputTag("packedPFCandidates"),
                                     cut=cms.string("abs(pdgId)!=1 && abs(pdgId)!=2 && abs(eta)<3.0")
                                     )

#jets are rebuilt from those candidates by the tools, no need to do anything else
### =================================================================================

from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD

#default configuration for miniAOD reprocessing, change the isData flag to run on data
#for a full met computation, remove the pfCandColl input
runMetCorAndUncFromMiniAOD(process,
                           isData=runOnData,
                           )

if not useHFCandidates:
    runMetCorAndUncFromMiniAOD(process,
                               isData=runOnData,
                               pfCandColl=cms.InputTag("noHFCands"),
                               reclusterJets=True, #needed for NoHF
                               recoMetFromPFCs=True, #needed for NoHF
                               postfix="NoHF"
                               )

if redoPuppi:
  from PhysicsTools.PatAlgos.slimming.puppiForMET_cff import makePuppiesFromMiniAOD
  makePuppiesFromMiniAOD( process );

  runMetCorAndUncFromMiniAOD(process,
                             isData=runOnData,
                             pfCandColl=cms.InputTag("puppiForMET"),
                             recoMetFromPFCs=True,
                             reclusterJets=True,
                             jetFlavor="AK4PFPuppi",
                             postfix="Puppi"
                             )


process.MINIAODSIMoutput = cms.OutputModule("PoolOutputModule",
    compressionLevel = cms.untracked.int32(4),
    compressionAlgorithm = cms.untracked.string('LZMA'),
    eventAutoFlushCompressedSize = cms.untracked.int32(15728640),
    outputCommands = cms.untracked.vstring( "keep *_slimmedMETs_*_RERUN",
                                            "keep *_slimmedMETsNoHF_*_*",
                                            "keep *_patPFMet_*_*",
                                            "keep *_patPFMetT1_*_*",
                                            "keep *_patPFMetT1JetResDown_*_*",
                                            "keep *_patPFMetT1JetResUp_*_*",
                                            "keep *_patPFMetT1Smear_*_*",
                                            "keep *_patPFMetT1SmearJetResDown_*_*",
                                            "keep *_patPFMetT1SmearJetResUp_*_*",
                                            "keep *_puppiForMET_*_*",
                                            "keep *_puppi_*_*",
                                            "keep *_patPFMetT1Puppi_*_*",
                                            "keep *_slimmedMETsPuppi_*_*",
                                            ),
    fileName = cms.untracked.string('corMETMiniAOD.root'),
    dataset = cms.untracked.PSet(
        filterName = cms.untracked.string(''),
        dataTier = cms.untracked.string('')
    ),
    dropMetaData = cms.untracked.string('ALL'),
    fastCloning = cms.untracked.bool(False),
    overrideInputFileSplitLevels = cms.untracked.bool(True)
)


process.MINIAODSIMoutput_step = cms.EndPath(process.MINIAODSIMoutput)
