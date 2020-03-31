''' 
Script to analyze powder diffraction data 

Originally written by Christian Schleputz
Modified for current version by Zhan Zhang, APS, ANL. 

This version utilizes the now internal package "PowderScanMapper"
Note at this time, the plot function is not implemented. 

Here the SPEC file names and the scan # lists need to be one to one corresponding. 

List of scans or scan-ranges that should be processed. Each list item is
  processed as a new powder diffraction data set, but lists or string-ranges
  within list elements are combined in a single data file. List items can be
  integers, strings, string ranges, or lists.

Slices_not_used lists the slices (points) in any scan that will not be used.
  Each File should have a separate list, where the item itself a lists of 2 string items:
  the scan number(s) and the slices to be removed.

Example:  

  specFileList = [ "specfile_1.spec", 
                   "specfile_2.spec", 
                   "specfile_3.spec",
                   "specfile_4.spec",
                 ]
  scan_Lists = [   ['73'],
                   ['74','76'], 
                   ['113-114,116',],
                   range(113-117), # from 113 - 116, one curve per scan, 4 total
               ]

  slicesNotUsedLists = [
                [ # per spec file, list of the slices to be removed from any scans.
                    ['73', '0-10'], # per scan, with the format of ['scan_num', 'point_to_be_removed']
                    ['74', ''],     # scan 74 no slice removed; -- this one is not needed other than a place holder.
                    ['76', '0-5']   # scan 76, slices [0:6] removed
                    ['113-114, 116', '-10-20'] # scans 113, 114, & 116, all with slices [-10 : -1], and [0:21] removed
                ],
            ]            
  It will read in 4 specfiles, 
   for the file "specfile_1.spec", processes scan 73; and generates 1 file:
       ..._S073.xye : scan #73
   for the file "specfile_2.spec", generates 2 files:
       ..._S074.xye : scan #74
       ..._S076.xye : scan #76
   for the file "specfile_3.spec", generates 1 file:
       ..._S113.xye : scan #113, 114, and 116 together
   for the file "specfile_4.spec", generates 4 files, one for each scan:
       ..._S113.xye : scan #113
       ..._S114.xye : scan #114
       ..._S115.xye : scan #115
       ..._S116.xye : scan #116

  If no slices need to be removed for any scan, set:
  slicesNotUsedLists = [ [] ]

The generated xye file will be in a sub-folder with the same name as the 
  corresponding SPEC file. 

'''
#================================================
# Import some useful generic packages. 
import os
import sys
import time
import numpy as np
from itertools import zip_longest

#==============================================================================
# User parameters
# ---------------
#
# Modify this section according to your needs. 
#  Please focus on the parts between:
#vvvvvvvvvvvvvvvvvvvvvv
#
#^^^^^^^^^^^^^^^^^^^^^^
#
#==============================================================================

# Data files and scan selection
#vvvvvvvvvvvvvvvvvvvvvv
#projectDir = os.path.join("/home/33id/", "data/tung/20200131/SHK/")
# for Windows system:
#projectDir = os.path.join("Z:\\", "data\\tung\\20200131\\SHK\\")      
projectDir = os.path.join("C:\\", "work\\testground\\rsm3d_test\\CuCrCo\\")      
#^^^^^^^^^^^^^^^^^^^^^^

#vvvvvvvvvvvvvvvvvvvvvv
specFileList = [
                "100-6-CuCrCo_1.spec",
               ]    
scanLists = [
              #['290', '291'],  # per spec file
              range(290, 293), # or use range() in place of a list, this one will get one curve per scan;
              #[range(290, 293)], # this one, will get one curve with 3 scans together.  
            ]
slicesNotUsedLists = [
                [ # per spec file, list of scans with slices to be removed down here.  
                    #['290', '-10-20'],  # with the format of ['scan_num', 'point_to_be_removed']
                    #['291', '-20-20'], 
                ],
            ]     
             
#^^^^^^^^^^^^^^^^^^^^^^

#detectorSettings
detectorName = "Pilatus"
# set to reduce data by averaging pixels 1,1 produces no averaging of pixels,
# uses the original data
bin = [1,1]
# Region of interesting
# set explicitly since the images are cropped by ROI
# COMMENT OUT roi or set to none to simply grab size from the calib file
#vvvvvvvvvvvvvvvvvvvvvv
roi = [5, 480, 5, 185]
#^^^^^^^^^^^^^^^^^^^^^^

# Set the x-axis properties
# data_coordinate can be 'tth' or 'q'
data_coordinate = 'tth'
# Use x_min = None or x_max = None to automatically find data set bounds
#vvvvvvvvvvvvvvvvvvvvvv
x_min_0 = 8
x_max_0 = 52
#^^^^^^^^^^^^^^^^^^^^^^

# Histogram step size in units of the x-axis (q or tth)
#vvvvvvvvvvvvvvvvvvvvvv
x_step = 0.02
#^^^^^^^^^^^^^^^^^^^^^^

#------------------
# Control plotting options -- in this version, plot does not work
do_plot = True
#do_plot = False
# y-axis scaling, can be 'Linear' or 'log'
plot_y = 'Linear'
#plot_y = 'log'
#------------------

# Control file export options
# In the output_filename_fmt, the spec_File_Name (without extension) and the
# first scannumber from scans are inserted to create the output filename.
write_file = True
#write_file = False
output_filename_fmt = os.path.join(projectDir, \
        "analysis_runtime/%s/%s_S%03d.xye")

#==============================================================================
# End of user parameters
# Do not modify the code below, unless you know what you are doing...
#==============================================================================

#================================================
# try use the logger to do console display
import logging

# create root_logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# create console handler and set level to debug
ch = logging.StreamHandler()
# create formatter
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
formatter = logging.Formatter('%(levelname)s - %(message)s')
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
root_logger.addHandler(ch)

# create logger
logger = logging.getLogger('powderScan_RSM3D')
logger.setLevel(logging.INFO)
#================================================

#=====================================
#  Import RsMap3D package and setup update progress
import rsMap3D
from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource
from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader import DetectorGeometryForXrayutilitiesReader as detReader
from rsMap3D.utils.srange import srange
from rsMap3D.config.rsmap3dconfigparser import RSMap3DConfigParser
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
#from rsMap3D.mappers.gridmapper import QGridMapper
from rsMap3D.mappers.powderscanmapper import PowderScanMapper
from rsMap3D.mappers.output.powderscanwriter import PowderScanWriter

def updateDataSourceProgress(value1, value2):
    logger.info("\t\tDataSource Progress %s%%/%s%%" % (value1, value2))

def updateMapperProgress(value1):
    logger.info("\t\tMapper Progress -- Current Curve %s%%" % (value1))

#=====================================
# Set ROI or get info from the config
if roi is None:
    detector = dReader.getDetectorById(detectorName)
    nPixels = dReader.getNpixels(detector)
    roi = [1, nPixels[0], 1, nPixels[1]]
logger.info('  ROI: %s ' % roi)

#=====================================
# assign the configuration files
configDir = projectDir
instConfigName = os.path.join(configDir, "33IDD_kappa.xml")
detectorConfigName = os.path.join(configDir, "33IDD_Pilatus_kappa.xml")
badPixelFile = os.path.join(configDir, "badpixels_dp3.txt")
#flatfieldFile = os.path.join(configDir, "flatfield_allone.tif")
flatfieldFile = None
if not os.path.exists(detectorConfigName):
    raise Exception("Detector Config file does not exist: %s" % 
                    detectorConfigName)
if not os.path.exists(instConfigName):
    raise Exception("Instrument Config file does not exist: %s" % 
                    instConfigName)
if not (badPixelFile is None):
    if not os.path.exists(badPixelFile):
        raise Exception("Bad Pixel file does not exist: %s" % 
                        badPixelFile)
if not (flatfieldFile is None):
    if not os.path.exists(flatfieldFile):
        raise Exception("Flat field file does not exist: %s" % 
                        flatfieldFile)
    
dReader = detReader(detectorConfigName)
#=====================================

# Outer-most loop, iterate over different SPEC files
for (specfile, scan_list, slicesNotUsed_list) in zip_longest(specFileList, scanLists, slicesNotUsedLists):
    
    specName, specExt = os.path.splitext(specfile)
    logger.info('=============================')
    logger.info('  Starting SPEC file : %s' % (specfile) )
    logger.info('    Scans            : %s' % (scan_list) )

    # generate the scan_list from a number/string/range
    if not isinstance(scan_list, list):
        if isinstance(scan_list, (int, float)):
            scan_list = [int(scan_list)]
        elif isinstance(scan_list, str):
            scan_range = srange(scan_list)
            scan_list = scan_range.list()
        elif isinstance(scan_list, range):
            scan_list = list(scan_list)

    # generate the slicesNotUsed_list from the given list/strings
    slicesNotUsed_scanN = []
    slicesNotUsed_sliceN = []
    for slicesNotUsed_oneset in slicesNotUsed_list:
        scan_range = srange(slicesNotUsed_oneset[0])
        scan_num = scan_range.list()
        slice_range = srange(slicesNotUsed_oneset[1])
        slice_nums = slice_range.list()
        if slice_nums:
            slicesNotUsed_scanN.extend( scan_num )
            slicesNotUsed_sliceN.append( slice_nums * len(scan_num) )

    num_curves = len(scan_list)
    progress = 0
    # Inner loop here, iterate over set of scans, one curve/file per set
    #for (scans, slicesNotUsed) in zip_longest(scan_list, slicesNotUsed_list):
    for scans in scan_list:
        logger.info('  --------------------------------')
        logger.info('      Reading scans # %s' % (str(scans)) )
        #logger.info('        Skipped slices : %s' % (str(slicesNotUsed)) )
        
        # generate the scanlist for current curve/file
        #  Note this part is because I want to use the range() function for the input
        #   which complicate thing quite a bit.  Maybe I should not do that.  Instead,
        #   sticking with the string seems a lot easier to understand.  
        if not isinstance(scans, list):
            if isinstance(scans, int):
                scans = [scans]
            elif isinstance(scans, str):
                scan_range = srange(scans)
                scans = scan_range.list()
            elif isinstance(scans, range):
                scans = list(scans)
        fileNameMarker = scans[0]

        # generate the output file names
        if not os.path.exists(specName):
            os.makedirs(specName)
        outputFileName = output_filename_fmt % (specName, specName, fileNameMarker)

        # Reset x_min and x_max for of each interation.
        x_min = x_min_0
        x_max = x_max_0

        _start_time = time.time()

        # Initialize the data source from the spec file, detector and instrument
        # configuration, read the data, and set the ranges such that all images
        # will be used.
        appConfig = RSMap3DConfigParser()
        ds = Sector33SpecDataSource(projectDir, specName, specExt, \
                instConfigName, detectorConfigName, roi=roi, pixelsToAverage=bin, \
                scanList = scans, badPixelFile = badPixelFile, \
                flatFieldFile = flatfieldFile, appConfig=appConfig)
        ds.setCurrentDetector(detectorName)
        ds.setProgressUpdater(updateDataSourceProgress)
        ds.loadSource()
        ds.setRangeBounds(ds.getOverallRanges())
        logger.info('  --------------------------------')
        
        # Adding here the section to handle the slices that are not going to be used
        #  in each scan -- in working progress, ZZ 2020/03/20
        for onescan in scans:
            if onescan in slicesNotUsed_scanN:
                myindex = slicesNotUsed_scanN.index(onescan)
                slice_list = slicesNotUsed_sliceN[myindex]
                logger.info('      Points #%s in scan #%s ignored.  ' % \
                        (str(slice_list), str(onescan)) )
                my_len = len(ds.imageToBeUsed[onescan])
                for slice in slice_list:
                    if slice in range(-my_len, my_len):
                        ds.imageToBeUsed[onescan][slice] = False
            else:
                logger.info('       No slice removed. ')
        logger.info('  --------------------------------')
                        
        # calling powder scan Mapper here.
        #  Note here the plot part does not do anything yet.
        powderMapper = PowderScanMapper(ds,
                 outputFileName,
                 transform = UnityTransform3D(),
                 gridWriter = PowderScanWriter(),
                 appConfig = appConfig,
                 dataCoord = data_coordinate,
                 xCoordMin = x_min,
                 xCoordMax = x_max,
                 xCoordStep = x_step,
                 plotResults = do_plot,
                 yScaling  = plot_y,
                 writeXyeFile = write_file)
                
        powderMapper.setProgressUpdater(updateMapperProgress)
        powderMapper.doMap()
        
        # Some mapping information on screen output
        x_min_output = powderMapper.getXCoordMin()
        x_max_output = powderMapper.getXCoordMax()
        nbins = np.round((x_max_output - x_min_output) / x_step)
        logger.info('  \t %s minimum : %.3f' % (data_coordinate, x_min_output))
        logger.info('  \t %s maximum : %.3f' % (data_coordinate, x_max_output))
        logger.info('  \t %s stepsize: %.3f' % (data_coordinate, x_step))
        logger.info('  \t %s nbins   : %.3f' % (data_coordinate, nbins))

        progress += 100.0/num_curves
        #if verbose:
            #print 'Current File Progress: %.1f' % (progress)
            #print 'Elapsed time for Q-conversion: %.1f seconds' % (time.time() - _start_time)
        logger.info('  Elapsed time for current curve: %.3f seconds' % (time.time() - _start_time) )
        logger.info('  Mapper Progress -- Current File : %.1f%%' % (progress) )
        if write_file:
            logger.info('  Output filename : %s' % (outputFileName) )
        else:
            logger.info('  Output file %s disabled. ' % (outputFileName) )
    logger.info('  --------------------------------')
logger.info('=============================')
