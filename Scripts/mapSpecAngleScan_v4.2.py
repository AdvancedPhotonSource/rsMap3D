'''

Script to rebuild reciprocal space map
Try to handle the mapping data from the specfile as it is taken.
Check the file as it goes, analysis the data 

 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.

 Modified from earlier version and Mike's code -- ZZ 2022/10/07
 
 And try to move the inputs to the external json file: config.json.
 ==========
 User parameters are loaded from the rsmconfig.json file, preferably in the 
   same folder as this script.  If not, the full path and filename need to be 
   given as an argument, e.g. : 
       python mapSpecAngleScan_v2.py path/to/rsmconfig.json
 ==========


Script to process a dataset using the Sector33SpecDataSource

Change list:

    2022/10/12 (ZZ):
       - consolidated earlier version and generated v3 (input in the py file)
           and v4 (use external json file for input).  

    2022/10/14 (ZZ):
       - try to check the scan is done or not on realtime option with the 
           EPICS PV flag.  Just implemented at 33-ID-D.  
    
    2024/01/03 (ZZ):
       - add the grid range in the json file as entry "grid_range", in 
            the format of [h_min, h_max, k_min, k_max, l_min, l_max]
       - accordingly, modify the code here to use the range.  
       - if it is value "null", use the default full range.  
    
To DO:
    
    - SPEC file reindex check file time stamp? No need to redo if not changed. 

'''

import os
import numpy as np
import sys
import datetime
import time
import json
import argparse
from pathlib import Path
from spec2nexus import spec

from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource
from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader import DetectorGeometryForXrayutilitiesReader as detReader
from rsMap3D.utils.srange import srange
from rsMap3D.config.rsmap3dconfigparser import RSMap3DConfigParser
from rsMap3D.constants import ENERGY_WAVELENGTH_CONVERT_FACTOR
from rsMap3D.mappers.gridmapper import QGridMapper
from rsMap3D.gui.rsm3dcommonstrings import BINARY_OUTPUT
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.mappers.output.vtigridwriter import VTIGridWriter
from epics import PV

def updateDataSourceProgress(value1, value2):
    logger.info("\t\tDataLoading Progress -- Current set: %.3f%%/%s%%" % (value1, value2))

def updateMapperProgress(value1):
    logger.info("\t\tMapper Progress -- Current volume: %.3f%%" % (value1))

def reindex_specfile(fullFilename):
    logger.info('=============================')
    logger.info('  Re-indexing the SPEC file...')
    spec_data = spec.SpecDataFile(fullFilename)
    scansInFile_list = spec_data.getScanNumbers()
    logger.info('  Done. The lastest scan # is %s' % scansInFile_list[-1])
    return scansInFile_list, spec_data

def parseArgs():
    parser = argparse.ArgumentParser(description='Default MPI run script. Expects a json config file pointed at the data.')
    parser.add_argument('configPath', 
                        nargs='?', 
                        default=os.path.join(os.getcwd(), 'rsmconfig.json'),
                        help='Path to config file. If none supplied, directs to a config.json located in CWD')
    return parser.parse_args()

def generateScanLists(inputScanList):
    # How many conditions/cycles in total
    num_cycles = inputScanList["cycles"]
    # Total number of scans at one condition, say each temperature
    scans_in_1_cycle = inputScanList["scans_per_cycle"]
    SetsOfRSM = inputScanList["rsm_sets"]
    
    scanListTop = []
    for i in range(0, num_cycles):
        for oneSetRSM in SetsOfRSM:
            scan_s = oneSetRSM["start"]
            scan_e = oneSetRSM["end"]
            scans_in_1_rsm = scan_e - scan_s + 1
            scanListTop = scanListTop + \
                ( [[f"{x}" if scans_in_1_rsm==1 else f"{x}-{x+scans_in_1_rsm-1}"] for \
                x in range(scan_s+i*scans_in_1_cycle, scan_e+i*scans_in_1_cycle+1, scans_in_1_rsm)] )
    return scanListTop

def _is_scan_done(specfile_full, curr_scan=1):
    specfile_pv = PV("33idSIS:spec:SPECFileName")
    scann_pv = PV("33idSIS:spec:SCANNUM")
    scanDone_pv = PV("33idSIS:spec:ISSCANDONE")
    
    # Check if PVs are there.  If one cant be reached, stop there. 
    if (not scann_pv.wait_for_connection(timeout=2)) \
        or (not scanDone_pv.wait_for_connection(timeout=2)) \
        or (not specfile_pv.wait_for_connection(timeout=2)):
        return -1
    
    # If it is not the current file, this one is irrelavent.
    if specfile_full != specfile_pv.char_value:
        return 1
    # If scan number is lower than the current, go ahead
    if (curr_scan < scann_pv.value):
        return 1
    elif (curr_scan == scann_pv.value):
        if scanDone_pv.value == 1:
            return 1
        else:
            return 0
    else:
        return 0

def checkGridRange(gridRange, fullRange):
    if (gridRange is None):
        tmp = fullRange
    elif (len(gridRange) != 6):
        tmp = fullRange
    else:
        h_min = max(fullRange[0], min(gridRange[0], gridRange[1]))
        h_max = min(fullRange[1], max(gridRange[0], gridRange[1]))
        k_min = max(fullRange[2], min(gridRange[2], gridRange[3]))
        k_max = min(fullRange[3], max(gridRange[2], gridRange[3]))
        l_min = max(fullRange[4], min(gridRange[4], gridRange[5]))
        l_max = min(fullRange[5], max(gridRange[4], gridRange[5]))
        tmp = h_min, h_max, k_min, k_max, l_min, l_max
    return tmp

# Rocord the starting run time
startTime = datetime.datetime.now()
with open('time.log', 'a') as time_log:
    time_log.write(f'Start: {startTime}\n')
    
#================================================
# try use the logger to do console display
import logging

# create root_logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
root_logger.addHandler(ch)

# create logger
logger = logging.getLogger('mapSpecAngleScan_RSM3D')
logger.setLevel(logging.INFO)
#================================================

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
# Get the input from the input file
args = parseArgs()
with open(args.configPath, 'r') as config_f:
    config = json.load(config_f)

# workpath and config file path
projectDir = config["project_dir"]
configDir = config["config_dir"]

if configDir == None:
    configDir = projectDir
    
# Config files 
detectorConfigName = os.path.join(configDir, config["detector_config"])
instConfigName = os.path.join(configDir, config["instrument_config"])
badPixelFile = os.path.join(configDir, config["badpixel_file"])
flatfieldFile = config["flat_field"]
                      
# Detector settngs
detectorName = config["detector_name"]
bin = config["binning"]
roi = config["roi_setting"]
# Output grid number
nx = config["nx"]
ny = config["ny"]
nz = config["nz"]
# Output grid range
gridRange_input = config["grid_range"]
# Output selction
mapHKL = config["use_HKL"]
# Do realtime or not
realtime_flag = config["real_time"]

datasets = config["datasets"]
one_scan_time = config["maxTime_1Scan"]

#$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

#####################################
# checking for validity of the inputs
if not os.path.exists(detectorConfigName):
    raise Exception("Detector Config file does not exist: %s" % 
                    detectorConfigName)
if not os.path.exists(instConfigName):
    raise Exception("Instrument Config file does not exist: %s" % 
                    instConfigName)
if not os.path.exists(badPixelFile):
    raise Exception("Bad Pixel file does not exist: %s" % 
                    badPixelFile)
if not (flatfieldFile is None):
    flatfieldFile = os.path.join(configDir, flatfieldFile)
    if not os.path.exists(flatfieldFile):
        raise Exception("Flat field file does not exist: %s" % 
                        flatfieldFile)

# If no ROI set, get info from the config
if roi is None:
    detector = dReader.getDetectorById(detectorName)
    nPixels = dReader.getNpixels(detector)
    roi = [1, nPixels[0], 1, nPixels[1]]
logger.info("ROI: %s " % roi)
# End checking for inputs
#####################################

dReader = detReader(detectorConfigName)

#=====================================
# Outer-most loop, iterate over different SPEC files
for idx, dataset in enumerate(datasets, 1):
    # SPEC file name and scan numbers
    specFile = dataset["spec_file"]
    scanListTop = dataset["scan_list"]
    
    if scanListTop == None:
        inputScanList = dataset["scan_range"]
        scanListTop = generateScanLists(inputScanList)
    
    specfile_full = os.path.join(projectDir, specFile)
    # Check if the SPEC file exists. Quit if not. 
    if not os.path.exists( specfile_full ):
        print(f"File not found.  Please check the path and name {specFile} is correct.")
        print(f"Moving on...in a couple of seconds. ")
        time.sleep(2)
        continue

    specName, specExt = os.path.splitext(specFile)
    # generate the output file folder now
    outputFilePath = os.path.join(projectDir, \
            "analysis_runtime", specName)
    Path(outputFilePath).mkdir(parents=True, exist_ok=True)
    
    logger.info('=============================')
    logger.info(f"SPEC file #{idx}: {specfile_full}")
    logger.info(f"Generated Scan List #{idx}: {scanListTop}")

    # (Re)index the SPEC file
    scansInFile_list, spec_data = reindex_specfile(specfile_full)

    for scanList1 in scanListTop:
        outputFileName = os.path.join(outputFilePath, \
            f"{specName}_{str(scanList1[0])}")

        if mapHKL == True:    
            outputFileName += '_hkl.vti'
        else:
            outputFileName += '_Qxyz.vti'

        appConfig = RSMap3DConfigParser()
        maxImageMemory = appConfig.getMaxImageMemory()

        scanRange = []
        for scans in scanList1:
            scanRange += srange(scans).list()
        logger.info(f"  --------------------------------")
        logger.info("scanRange %s" % scanRange)
        #logger.info("specName, specExt: %s, %s" % (specName, specExt))

        #=======================
        # Find the largest scan number in this set
        curr_scan = max(scanRange)
        # waiting time factor
        _accu = 1  
        last_len = 0
        while (realtime_flag):
            # add my local way to check if scan is done
            _scanDone_flag = _is_scan_done(specfile_full, curr_scan)
            if _scanDone_flag == 1:
                break
            elif _scanDone_flag == 0:
                sleep_time = 5
            else:
                # check if the largest scan number is available yet.
                if not (str(curr_scan) in scansInFile_list):
                    sleep_time = _accu*5
                    logger.info('  Scan #%d not available yet.  \
                        Wait %d seconds' % (curr_scan, sleep_time))
                elif scansInFile_list.index(str(curr_scan)) == (len(scansInFile_list) - 1):
                    # Try to figure out the scan is done or not -- no good way as I see it.
                    scan = spec_data.getScan(curr_scan)
                    #scan.interpret()
                    if(len(scan.data)>0):
                        curr_len = len(scan.data[scan.L[0]])
                    else:
                        curr_len = 0
                    logger.info('   Data points current in the scan #%d is %d' \
                        % (curr_scan, curr_len) )
                    if(curr_len == 0):
                        pass
                    elif(curr_len != last_len):
                        last_len = curr_len
                    else:
                        if(_accu>4):
                            break
                    sleep_time = 5*_accu
                    logger.info('  Scan #%d may not be finished.  Wait %d seconds...' \
                      % (curr_scan, sleep_time) )
                else:
                    logger.info('\t--------------------------------')
                    logger.info('  Scan #%d ready.\n' % curr_scan)
                    break
                _accu += 1

                scansInFile_list, spec_data = \
                    reindex_specfile(specfile_full)
                    
            # this is in the outer loop, when the scan does not exist yet, wait sometime before resume loops
            time.sleep(sleep_time)
            
        ds = Sector33SpecDataSource(projectDir, specName, specExt,
                                    instConfigName, detectorConfigName, roi=roi, 
                                    pixelsToAverage=bin, scanList= scanRange, 
                                    badPixelFile=badPixelFile, 
                                    flatFieldFile=flatfieldFile, 
                                    appConfig=appConfig)
        ds.setCurrentDetector(detectorName)
        ds.setProgressUpdater(updateDataSourceProgress)
        ds.loadSource(mapHKL=mapHKL)
        
        fullRange = ds.getOverallRanges()
        if gridRange_input is None:
            gridRange = fullRange
        else:
            gridRange = checkGridRange(gridRange_input, fullRange)
            
        ds.setRangeBounds(gridRange)
        
        imageToBeUsed = ds.getImageToBeUsed()
        #print("imageToBeUsed %s" % imageToBeUsed)
        imageSize = np.prod(ds.getDetectorDimensions())
        logger.info('  --------------------------------')

        gridMapper = QGridMapper(ds,
                                 outputFileName, 
                                 outputType=BINARY_OUTPUT,
                                 nx=nx, ny=ny, nz=nz,
                                 transform=UnityTransform3D(),
                                 gridWriter=VTIGridWriter(),
                                 appConfig=appConfig)

        gridMapper.setProgressUpdater(updateMapperProgress)
        gridMapper.doMap()

    with open('time.log', 'a') as time_log:
        endTime = datetime.datetime.now()
        time_log.write(f'End: {endTime}\n')
        time_log.write(f'Diff: {endTime - startTime}\n')
        
    logger.info('  --------------------------------')
logger.info('=============================')
