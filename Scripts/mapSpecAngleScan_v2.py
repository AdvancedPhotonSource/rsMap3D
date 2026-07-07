'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
'''
Script to process a dataset using the Sector33SpecDataSource
'''

import os
import numpy as np

#==============================================================================
# User parameters
# ---------------
#
# Modify this section according to your needs. 
#  Please focus on the parts between:
#vvvvvvvvvvvvvvvvvvvvvv
#
#^^^^^^^^^^^^^^^^^^^^^^
# Example:
#
# scanListTop = [['73'],['74','76'], ['113-114,116'],]
#
# It will do 3 volumes:
#   one with scan 73, saved as
#       ..._73.vti
#   one with scans 74 & 76, saved as
#       ..._74-76.vti
#  and a third for scans 113-114 & 116 combined, saved as
#       ..._113-116.vti
#
#==============================================================================


# The project path, for Linux and Windows, note the different format
#  Currently, we only handel one single file
#vvvvvvvvvvvvvvvvvvvvvv
#projectDir = os.path.join("/home/33id/", "data/tung/20200131/SHK/")      
# for Windows system, use this format --
projectDir = os.path.join("C:\\work\\synrun\\", "20171011_33IDD_RSM_Dong\\RSM")      
#^^^^^^^^^^^^^^^^^^^^^^

#  Currently, we only handel one single file
#vvvvvvvvvvvvvvvvvvvvvv
specFile = "PTODSO_1.spec"
#^^^^^^^^^^^^^^^^^^^^^^
# a list of the lists.  Each inner list would be one RSM volume.
# For the example below, it will do 3 volumes, one with scan 73, one with scans 74 & 76,
#  and a third for scans 113-114 & 116.  
#vvvvvvvvvvvvvvvvvvvvvv
scanListTop = [['37-38'], ]
#^^^^^^^^^^^^^^^^^^^^^^

mapHKL = True
#mapHKL = False

# assign the configuration files
#***** Make sure you have these files in the same directory as the SPEC files.*****
#***** These are instrument specific.                           *****
#***** Please ask the beamline scientist if they are missing.   *****
configDir = projectDir
instConfigName = os.path.join(configDir, "33IDD_psic.xml")
detectorConfigName = os.path.join(configDir, "33IDD_Pilatus_psic.xml")
badPixelFile = os.path.join(configDir, "badpixels_dp3.txt")
#flatfieldFile = os.path.join(configDir, "flatfield_allone.tif")
flatfieldFile = None
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
    if not os.path.exists(flatfieldFile):
        raise Exception("Flat field file does not exist: %s" % 
                        flatfieldFile)
    
#detectorSettings
detectorName = "Pilatus"
# set to reduce data by averaging pixels 1,1 produces no averaging of pixels,
# uses the original data
bin = [1,1]
# Region of interesting
# set explicitly since the images are cropped by ROI
# COMMENT OUT roi or set to none to simply grab size from the calib file
roi = [5, 480, 5, 180]
# or get info from the config

#output grid size.  
nx = 200
ny = 200
nz = 200

#==============================================================================
# End of user parameters
# Do not modify the code below, unless you know what you are doing...
#==============================================================================

from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource
from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader import DetectorGeometryForXrayutilitiesReader as detReader
from rsMap3D.utils.srange import srange
from rsMap3D.config.rsmap3dconfigparser import RSMap3DConfigParser
from rsMap3D.constants import ENERGY_WAVELENGTH_CONVERT_FACTOR
from rsMap3D.mappers.gridmapper import QGridMapper
from rsMap3D.gui.rsm3dcommonstrings import BINARY_OUTPUT
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.mappers.output.vtigridwriter import VTIGridWriter

def updateDataSourceProgress(value1, value2):
    logger.info("\t\tDataLoading Progress -- Current set: %.3f%%/%s%%" % (value1, value2))

def updateMapperProgress(value1):
    logger.info("\t\tMapper Progress -- Current volume: %.3f%%" % (value1))

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

# If no ROI set, get info from the config
if roi is None:
    detector = dReader.getDetectorById(detectorName)
    nPixels = dReader.getNpixels(detector)
    roi = [1, nPixels[0], 1, nPixels[1]]
logger.info("ROI: %s " % roi)

dReader = detReader(detectorConfigName)

specName, specExt = os.path.splitext(specFile)

for scanList1 in scanListTop:
    outputFileName = os.path.join(projectDir, "analysis_runtime", specName + '_' + str(scanList1[0]) + 'x.vti')
    # note that the q ranges in the three dimensions are available
    # later.  If you know resolution desired, it is possible to calculate more 
    # appropriate nx, ny, nz

    appConfig = RSMap3DConfigParser()
    maxImageMemory = appConfig.getMaxImageMemory()

    scanRange = []
    for scans in scanList1:
        scanRange += srange(scans).list()
    logger.info("scanRange %s" % scanRange)
    logger.info("specName, specExt: %s, %s" % (specName, specExt))
    ds = Sector33SpecDataSource(projectDir, specName, specExt,
                                instConfigName, detectorConfigName, roi=roi, 
                                pixelsToAverage=bin, scanList= scanRange, 
                                badPixelFile=badPixelFile, 
                                flatFieldFile=flatfieldFile, 
                                appConfig=appConfig)
    ds.setCurrentDetector(detectorName)
    ds.setProgressUpdater(updateDataSourceProgress)
    ds.loadSource(mapHKL=mapHKL)
    ds.setRangeBounds(ds.getOverallRanges())
    imageToBeUsed = ds.getImageToBeUsed()
    #print("imageToBeUsed %s" % imageToBeUsed)
    imageSize = np.prod(ds.getDetectorDimensions())

    gridMapper = QGridMapper(ds,
                             outputFileName, 
                             outputType=BINARY_OUTPUT,
							 nx=nx, ny=ny, nz=nz,
                             transform=UnityTransform3D(),
                             gridWriter=VTIGridWriter(),
                             appConfig=appConfig)

    gridMapper.setProgressUpdater(updateMapperProgress)
    gridMapper.doMap()
    
    
