#!/usr/bin/env python
"""
This is a small script that does the equivalent of multicrab.

To run:
  ./multicrab --crabCmd CMD [--workArea WAD --crabCmdOpts OPTS]
  where CMD is the crab command, WAD is a work area directory with many CRAB project directories inside and OPTS are options for the crab command. 

For e.g.
Command to crab submit:
  ./multicrab_Job_<current file>.py --crabCmd submit

Command to crab status:
  ./multicrab_Job_<current file>.py --crabCmd status --workArea <working area (common)>

"""

import os
from optparse import OptionParser

from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException
from httplib import HTTPException


def getOptions():
    """
    Parse and return the arguments provided by the user.
    """
    usage = ("Usage: %prog --crabCmd CMD [--workArea WAD --crabCmdOpts OPTS]"
             "\nThe multicrab command executes 'crab CMD OPTS' for each project directory contained in WAD"
             "\nUse multicrab -h for help")

    parser = OptionParser(usage=usage)

    parser.add_option('-c', '--crabCmd',
                      dest = 'crabCmd',
                      default = '',
                      help = "crab command",
                      metavar = 'CMD')

    parser.add_option('-w', '--workArea',
                      dest = 'workArea',
                      default = '',
                      help = "work area directory (only if CMD != 'submit')",
                      metavar = 'WAD')

    parser.add_option('-o', '--crabCmdOpts',
                      dest = 'crabCmdOpts',
                      default = '',
                      help = "options for crab command CMD",
                      metavar = 'OPTS')

    (options, arguments) = parser.parse_args()

    if arguments:
        parser.error("Found positional argument(s): %s." % (arguments))
    if not options.crabCmd:
        parser.error("(-c CMD, --crabCmd=CMD) option not provided.")
    if options.crabCmd != 'submit':
        if not options.workArea:
            parser.error("(-w WAR, --workArea=WAR) option not provided.")
        if not os.path.isdir(options.workArea):
            parser.error("'%s' is not a valid directory." % (options.workArea))

    return options


def main():

    options = getOptions()

    # The submit command needs special treatment.
    if options.crabCmd == 'submit':

        #--------------------------------------------------------
        # This is the base config:
        #--------------------------------------------------------
        from CRABClient.UserUtilities import config
        config = config()
        
        scheme="PFA1p" # PFA1p, PFA2, PFA1

        SpTag="_wCaloOption"  ## IMPORTANT to set SpTag
		
        config.General.requestName = None
        config.General.workArea = 'L1TNtuple_HCal_OOT_PUS_mc_effi_%s%s' % (scheme,SpTag)
        config.General.transferOutputs = True
        config.General.transferLogs = False
        
        config.JobType.pluginName = 'Analysis'
        config.JobType.psetName = 'l1ntuple_maker_run3_mc_effi.py'
        config.JobType.pyCfgParams = ['maxEvt=-1', 'prtEvt=10000', 'nVtxMin=50', 'HCALPFA=%s' % (scheme)] 
        #config.JobType.outputFiles = ['L1Ntuple_HCAL.root']

        config.Data.inputDataset = None
        config.Data.ignoreLocality = False
        config.Data.inputDBS = 'global'
        config.Data.splitting = 'FileBased' # 'Automatic' #'LumiBased' 
        config.Data.unitsPerJob = 1
        #config.Data.totalUnits = 30
        config.Data.outputDatasetTag = None
#        config.Data.outLFNDirBase = '/store/user/ssawant/'
        #config.Data.useParent = True 

#        config.Site.storageSite = 'T2_IN_TIFR' # Choose your site. 

        config.Site.storageSite = 'T2_CH_CERN' # Choose your site
        config.Data.outLFNDirBase = '/store/group/dpg_trigger/comm_trigger/L1Trigger/ssawant/'
        #--------------------------------------------------------

        # Will submit one task for each of these input datasets.
        inputDatasets = [
#            '/SingleMuon/Run2018A-ZMu-12Nov2019_UL2018-v2/RAW-RECO',
#            '/SingleMuon/Run2018B-ZMu-12Nov2019_UL2018-v2/RAW-RECO',
#            '/SingleMuon/Run2018C-ZMu-12Nov2019_UL2018-v2/RAW-RECO',
#            '/SingleMuon/Run2018D-ZMu-12Nov2019_UL2018-v3/RAW-RECO',
#            '/SingleMuon/Run2018D-ZMu-12Nov2019_UL2018-v4/RAW-RECO',
#
#			'/ZeroBias/Run2018A-PromptReco-v1/AOD',
#			'/ZeroBias/Run2018A-PromptReco-v2/AOD',
#			'/ZeroBias/Run2018A-PromptReco-v3/AOD',
#			'/ZeroBias/Run2018B-PromptReco-v1/AOD',
#			'/ZeroBias/Run2018B-PromptReco-v2/AOD',
#			'/ZeroBias/Run2018C-PromptReco-v1/AOD',
#			'/ZeroBias/Run2018C-PromptReco-v2/AOD',
#			'/ZeroBias/Run2018C-PromptReco-v3/AOD',
#			'/ZeroBias/Run2018D-PromptReco-v1/AOD',
#			'/ZeroBias/Run2018D-PromptReco-v2/AOD',
#
#            '/Neutrino_Pt-2to20_gun/Run3Winter20DRPremixMiniAOD-SNB_110X_mcRun3_2021_realistic_v6-v1/AODSIM'
#
	    '/TTToSemiLeptonic_TuneCP5_14TeV-powheg-pythia8/Run3Winter20DRPremixMiniAOD-110X_mcRun3_2021_realistic_v6-v2/AODSIM'
	]

        secondaryInputDatasets = [
#            '/Neutrino_Pt-2to20_gun/Run3Winter20DRPremixMiniAOD-SNB_110X_mcRun3_2021_realistic_v6-v1/GEN-SIM-RAW'
#			
	    '/TTToSemiLeptonic_TuneCP5_14TeV-powheg-pythia8/Run3Winter20DRPremixMiniAOD-110X_mcRun3_2021_realistic_v6-v2/GEN-SIM-RAW'
	]

        for inDS in inputDatasets:
            # inDS is of the form /A/B/C. Since B is unique for each inDS, use this in the CRAB request name.
            datasetName_part1 = inDS.split('/')[1]
            datasetName_part2 = inDS.split('/')[2]
            config.General.requestName = '%s' % (datasetName_part2)
            config.Data.inputDataset = inDS
            config.Data.outputDatasetTag = '%s_%s' % (config.General.workArea, datasetName_part2)

            if len(secondaryInputDatasets) > 0:
                print "secondaryInputDatasets %s included **** IMPORTANT SIDDH *****" % secondaryInputDatasets[0]
                config.Data.secondaryInputDataset = secondaryInputDatasets[0]
				
            # Submit.
            try:
                print "Submitting for input dataset %s" % (inDS)
                crabCommand(options.crabCmd, config = config, *options.crabCmdOpts.split())
            except HTTPException as hte:
                print "Submission for input dataset %s failed: %s" % (inDS, hte.headers)
            except ClientException as cle:
                print "Submission for input dataset %s failed: %s" % (inDS, cle)

    # All other commands can be simply executed.
    elif options.workArea:

        for dir in os.listdir(options.workArea):
            projDir = os.path.join(options.workArea, dir)
            if not os.path.isdir(projDir):
                continue
            # Execute the crab command.
            msg = "Executing (the equivalent of): crab %s --dir %s %s" % (options.crabCmd, projDir, options.crabCmdOpts)
            print "-"*len(msg)
            print msg
            print "-"*len(msg)
            try:
                crabCommand(options.crabCmd, dir = projDir, *options.crabCmdOpts.split())
            except HTTPException as hte:
                print "Failed executing command %s for task %s: %s" % (options.crabCmd, projDir, hte.headers)
            except ClientException as cle:
                print "Failed executing command %s for task %s: %s" % (options.crabCmd, projDir, cle)


if __name__ == '__main__':
    main()
