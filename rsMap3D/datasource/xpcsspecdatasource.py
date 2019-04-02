'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.config.rsmap3dlogging import METHOD_ENTER_STR, METHOD_EXIT_STR
try:
    from pyimm.immheader import readHeader, getNumberOfImages
    from pyimm.GetImmStartIndex import GetStartPositions
    from pyimm.OpenMultiImm import OpenMultiImm
except ImportError as ex:
    raise ex

import sys
import time
import os
import glob
from spec2nexus.spec import SpecDataFile
import xrayutilities as xu
import numpy as np
import logging
logger = logging.getLogger(__name__)
import traceback

from rsMap3D.exception.rsmap3dexception import ScanDataMissingException,\
    RSMap3DException
from rsMap3D.datasource.Sector33SpecDataSource import IMAGE_DIR_MERGE_STR,\
    Sector33SpecFileException,  LoadCanceledException
from rsMap3D.gui.rsm3dcommonstrings import CANCEL_STR
from rsMap3D.datasource.specxmldrivendatasource import SpecXMLDrivenDataSource
from rsMap3D.mappers.abstractmapper import ProcessCanceledException

IMAGES_STR = "images"
IMM_STR = "*.imm"
XPCS_SCAN = 'xpcsscan'
ASCAN = 'ascan'
CCD_SCAN = 'ccdscan'
DARK_STR = 'dark'
PATH_TO_REPLACE = "pathToReplace"
REPLACE_PATH_WITH = "replacePathWith"

class XPCSSpecDataSource(SpecXMLDrivenDataSource):
    def __init__(self,
                 projectDir,
                 projectName,
                 projectExtension,
                 instConfigFile,
                 detConfigFile,
                 **kwargs):
        
        self.pathToReplace = None
        self.replacePathWith = None
        if kwargs[PATH_TO_REPLACE] != None:
            self.pathToReplace = kwargs[PATH_TO_REPLACE]
            logger.debug("pathToReplace: %s" % self.pathToReplace)
            
        if kwargs[REPLACE_PATH_WITH] != None:
            self.replacePathWith = kwargs[REPLACE_PATH_WITH]
            logger.debug("replacePathWith: %s" % self.replacePathWith)
        del kwargs[PATH_TO_REPLACE]
        del kwargs[REPLACE_PATH_WITH]
            
        super(XPCSSpecDataSource, self).__init__(projectDir,
                                                 projectName,
                                                 projectExtension,
                                                 instConfigFile,
                                                 detConfigFile,
                                                 **kwargs)
#         self.immDataFile = immDataFile
        logger.debug(METHOD_ENTER_STR)
        self.cancelLoad = False
        logger.debug(METHOD_EXIT_STR)
        
    
    def getGeoAngles(self, scan, angleNames):
        """
        This function returns all of the geometry angles for the
        for the scan as a N-by-num_geo array, where N is the number of scan
        points and num_geo is the number of geometry motors.
        """
#        scan = self.sd[scanNo]
        geoAngles = self.getScanAngles(scan, angleNames)
        return geoAngles
        

    def getUBMatrix(self, scan):
        """
        Read UB matrix from the #G3 line from the spec file. 
        """
        try:
            g3 = scan.G["G3"].strip().split()
            g3 = np.array(map(float, g3))
            ub = g3.reshape(-1,3)
            logger.debug("ub " +str(ub))
            return ub
        except:
            logger.error("Unable to read UB Matrix from G3")
            logger.error( '-'*60)
            traceback.print_exc(file=sys.stdout)
            logger.error('-'*60)

    def imagesBeforeScan(self, scanNo):
        numImages = 0
        scan = self.sd.scans[str(scanNo)]
        numImages = int(scan.data["img_n"][0])
            
        return numImages
            
        
    def imagesInScan(self, scanNo):
        scan = self.sd.scans[str(scanNo)]
        numImages = len(scan.data_lines)
        return numImages
        
    def loadSource(self, mapHKL=False):
        logger.debug(METHOD_ENTER_STR)
        #Load up the instrument config XML file
        self.loadInstrumentXMLConfig()
        #Load up the detector configuration file
        self.loadDetectorXMLConfig()
#         lastScan = None
        
        self.specFile = os.path.join(self.projectDir, self.projectName + \
                                     self.projectExt)
        try:
            self.sd = SpecDataFile(self.specFile)
            self.mapHKL = mapHKL
            maxScan = int(self.sd.getMaxScanNumber())
            logger.debug("%s scans" % str(maxScan))
            if self.scans  is None:
                self.scans = range(1, maxScan+1)
            imagePath = os.path.join(self.projectDir, 
                            IMAGE_DIR_MERGE_STR % self.projectName)
            
            self.imageBounds = {}
            self.imageToBeUsed = {}
            self.availableScans = []
            self.incidentEnergy = {}
            self.ubMatrix = {}
            self.scanType = {}
            self.scanDataFile = {}
            self.immDataFileName = {}
            self.progress = 0
            self.progressInc = 1
            self.isCcdScan = {}
            self.dataFilePrefix = {}
            self.containsDark = {}
            self.numberOfDarks = {}
            self.containsRoi = {}
            self.roi = {}
            self.repeatsPoints = {}
            self.numberOfRepeatPoints = {}
            # Zero the progress bar at the beginning.
            if self.progressUpdater is not None:
                self.progressUpdater(self.progress, self.progressMax)
            for scan in self.scans:
                if (self.cancelLoad):
                    self.cancelLoad = False
                    raise LoadCanceledException(CANCEL_STR)
                
                else:
#                     if (os.path.exists(os.path.join(imagePath, \
#                                             SCAN_NUMBER_MERGE_STR % scan))):
                    curScan = self.sd.scans[str(scan)]
                    curScan.interpret()
                    logger.debug( "scan: %s" % scan)
#                     if int(scan) > 1:
#                         lastScan = self.sd.scans[str(int(scan)-1)]
#                         lastScan.interpret()
#                         logger.debug("dir(lastScan) = %s" % dir(lastScan) )
#                         logger.debug("lastScan.CCD %s" % lastScan.CCD)
                    try:
                        angles = self.getGeoAngles(curScan, self.angleNames)
                        self.availableScans.append(scan)
                        self.scanType[scan] = \
                            self.sd.scans[str(scan)].scanCmd.split()[0]
                        logger.debug( "Scan %s scanType %s" % (scan, self.scanType[scan]))
                        if self.scanType[scan] == 'xpcsscan':
                            #print dir(self.sd)
                            d = curScan.data
                            h = curScan.header
                            dataFile = curScan.XPCS['batch_name'][0]
                            self.immDataFileName[scan] = dataFile
                            logger.debug("curScan.XPCS %s" % curScan.XPCS)
                            if not (dataFile in self.scanDataFile.keys()):
                                self.scanDataFile[dataFile] = {}
                                numImagesInScan = self.imagesInScan(scan)
                                self.scanDataFile[dataFile][scan] = \
                                    range(0, numImagesInScan)
                                self.scanDataFile[dataFile]['maxIndexImage'] = \
                                    numImagesInScan
                                logger.debug( "scanDataFile for " + \
                                    str(dataFile) + " at scan " + str(scan) + \
                                    " " + str(self.scanDataFile[dataFile][scan])) 
                            else:
                                startingImage = \
                                    self.scanDataFile[dataFile]['maxIndexImage']
                                numImagesInScan = self.imagesInScan(scan)
                                self.scanDataFile[dataFile][scan] = \
                                    range(startingImage, \
                                          startingImage + numImagesInScan)
                                self.scanDataFile[dataFile]['maxIndexImage'] = \
                                    startingImage + numImagesInScan
                                logger.debug( "scanDataFile for " + str(dataFile) + \
                                    " at scan " + str(scan) + " " + \
                                    str(self.scanDataFile[dataFile][scan] ))
                                
                            logger.debug("dataFile %s" % dataFile)
                        
                        elif curScan.CCD != None and \
                            'ccdscan' in curScan.CCD.keys():
                            # this is a ccdscan where the defining #CCD lines 
                            # were above the #S lines in spec file
                            #TODO
                            d = curScan.data
                            h = curScan.header
                            ccdPart = curScan.CCD
                            COUNTER_ROI_STR = 'counter_roi'
                            REPEAT_POINTS_STR = 'repeats_per_point'

                            self.isCcdScan[scan] = True
                            self.dataFilePrefix[scan] = ccdPart['image_dir'][0]
                            #If the data has moved from the original location 
                            # then we need to change the prefixPath
                            if (self.pathToReplace != None) and \
                                (self.replacePathWith !=None):
                                self.dataFilePrefix[scan] = self.dataFilePrefix[scan].\
                                    replace(self.pathToReplace, \
                                            self.replacePathWith)
                            self.containsDark[scan] = DARK_STR in ccdPart.keys()
                            self.numberOfDarks[scan] = int(ccdPart[DARK_STR][0])
                            self.containsRoi[scan] = COUNTER_ROI_STR in ccdPart.keys()
                            self.roi[scan] = map(int, ccdPart[COUNTER_ROI_STR])
                            self.repeatsPoints[scan] = REPEAT_POINTS_STR in ccdPart.keys()
                            self.numberOfRepeatPoints[scan] = ccdPart[REPEAT_POINTS_STR]
                            
                            logger.debug("isCcdScan[%s] %s" % 
                                         (scan,self.isCcdScan[scan]))
                            logger.debug("dataFilePrefix[%s] %s" % 
                                         (scan, self.dataFilePrefix[scan]))
                            if self.containsDark[scan]:
                                logger.debug("containsDark[%s] %s" % 
                                             (scan, self.containsDark[scan]))
                            logger.debug("numberOfDarks[%s] %s" % 
                                         (scan, self.numberOfDarks[scan]))
                            logger.debug("containsRoi[%s] %s" % 
                                         (scan, self.containsRoi[scan]))
                            if self.containsRoi[scan]:
                                self.detectorROI = self.roi[scan]
                                self.detectorROI[0] = self.roi[scan][0]
                                self.detectorROI[1] = self.roi[scan][0] + self.roi[scan][1]
                                self.detectorROI[2] = self.roi[scan][2]
                                self.detectorROI[3] = self.roi[scan][2] + self.roi[scan][3]
                                logger.debug("roi[%s] %s" % (scan, self.roi[scan]))
                            logger.debug("repeatsPoints[%s] %s" % 
                                         (scan, self.repeatsPoints[scan]))
                            if self.repeatsPoints[scan]:
                                logger.debug("numberOfRepeatPoints[%s] %s" % 
                                             (scan,self.numberOfRepeatPoints[scan]))

                        if self.mapHKL==True:
                            self.ubMatrix[scan] = self.getUBMatrix(curScan)
                            if self.ubMatrix[scan] is None:
                                raise Sector33SpecFileException("UB matrix " + \
                                                                "not found.")
                        else:
                            self.ubMatrix[scan] = None
                        self.incidentEnergy[scan] = \
                            12398.4 /float(curScan.G['G4'].split()[3])
                        _start_time = time.time()
                        self.imageBounds[scan] = \
                            self.findImageQs(angles, \
                                             self.ubMatrix[scan], \
                                             self.incidentEnergy[scan])
                        if self.progressUpdater is not None:
                            self.progressUpdater(self.progress, self.progressMax)
                        logger.debug (('Elapsed time for Finding qs for scan %d: ' +
                               '%.3f seconds') % \
                               (scan, (time.time() - _start_time)))
                        #Make sure to show 100% completion
                    except ScanDataMissingException:
                        logger.debug( "scan %s" % scan )
            if self.progressUpdater is not None:
                self.progressUpdater(self.progressMax, self.progressMax)
        except IOError:
            raise IOError( "Cannot open file " + str(self.specFile))
#         if len(self.getAvailableScans()) == 0:
#             raise ScanDataMissingException("Could not find scan data for " + \
#                                            "input file \n" + self.specFile + \
#                                            "\nOne possible reason for this " + \
#                                            "is that the image files are " + \
#                                            "missing.  Images are assumed " + \
#                                            "to be in " + \
#                                            os.path.join(self.projectDir, 
#                                         IMAGE_DIR_MERGE_STR % self.projectName))
        #Load config information from the imm file
        self.availableScanTypes = set(self.scanType.values())
        logger.debug(METHOD_EXIT_STR)
        
    def rawmap(self, scans, mask=None):
    
        if mask is None:
            mask_was_none = True
            #mask = [True] * len(self.getImageToBeUsed()[scans[0]])
        else:
            mask_was_none = False

        intensity = np.array([])
        
                # fourc goniometer in fourc coordinates
        # convention for coordinate system:
        # x: upwards;
        # y: along the incident beam;
        # z: "outboard" (makes coordinate system right-handed).
        # QConversion will set up the goniometer geometry.
        # So the first argument describes the sample rotations, the second the
        # detector rotations and the third the primary beam direction.
        qconv = xu.experiment.QConversion(self.getSampleCircleDirections(), \
                                    self.getDetectorCircleDirections(), \
                                    self.getPrimaryBeamDirection())
    
        # define experimental class for angle conversion
        #
        # ipdir: inplane reference direction (ipdir points into the primary beam
        #        direction at zero angles)
        # ndir:  surface normal of your sample (ndir points in a direction
        #        perpendicular to the primary beam and the innermost detector
        #        rotation axis)
        en = self.getIncidentEnergy()
        hxrd = xu.HXRD(self.getInplaneReferenceDirection(), \
                       self.getSampleSurfaceNormalDirection(), \
                       en=en[self.getAvailableScans()[0]], \
                       qconv=qconv)

        if (self.getDetectorPixelWidth() != None ) and \
            (self.getDistanceToDetector() != None):
            hxrd.Ang2Q.init_area(self.getDetectorPixelDirection1(), \
                self.getDetectorPixelDirection2(), \
                cch1=self.getDetectorCenterChannel()[0], \
                cch2=self.getDetectorCenterChannel()[1], \
                Nch1=self.getDetectorDimensions()[0], \
                Nch2=self.getDetectorDimensions()[0], \
                pwidth1=self.getDetectorPixelWidth()[0], \
                pwidth2=self.getDetectorPixelWidth()[1], \
                distance=self.getDistanceToDetector(), \
                Nav=self.getNumPixelsToAverage(), \
                roi=self.getDetectorROI()) 
        else:
            hxrd.Ang2Q.init_area(self.getDetectorPixelDirection1(), \
                self.getDetectorPixelDirection2(), \
                cch1=self.getDetectorCenterChannel()[0], \
                cch2=self.getDetectorCenterChannel()[1], \
                Nch1=self.getDetectorDimensions()[0], \
                Nch2=self.getDetectorDimensions()[0], \
                chpdeg1=self.getDetectorChannelsPerDegree()[0], \
                chpdeg2=self.getDetectorChannelsPerDegree()[1], \
                Nav=self.getNumPixelsToAverage(), 
                roi=self.getDetectorROI()) 

        angleNames = self.getAngles()
        scanAngle = {}
        for i in range(len(angleNames)):
            scanAngle[i] = np.array([])
    
        imageToBeUsed = self.getImageToBeUsed()
        #get startIndex and length for each image in the immFile
        imageDir = os.path.join(self.projectDir, IMAGES_STR) 
        self.progressMax = len( self.scans) * 100
        self.progressInc = 1.0 * 100.0
        self.progress = 0
        for scannr in scans:
            curScan = self.sd.scans[str(scannr)]
            curScan.interpret()
            logger.debug( "scan: %s" % scannr)
#             if int(scannr) > 1:
#                 lastScan = self.sd.scans[str(int(scannr)-1)]
#                 lastScan.interpret()
#                 logger.debug("dir(lastScan) = %s" % dir(curS) )
#                 logger.debug("lastScan.CCD %s" % lastScan.CCD)
            if curScan.CCD != None and \
                'ccdscan' in curScan.CCD.keys():
                darkImage = None
                darksToSkip = 1
                if self.containsDark[scannr]:
                    numDarks = self.numberOfDarks[scannr]
                    namePrefix = self.dataFilePrefix[scannr]
                    darkName = namePrefix + DARK_STR + \
                            ("_00001-%.5d" % numDarks) + \
                            IMM_STR[1:]
                    try:
                        fp = open(darkName, 'rb')
                        numImagesInFile = getNumberOfImages(fp)
                        fp.close()
                        if numImagesInFile < numDarks:
                            raise RSMap3DException("dark file %s contains " + \
                                                   "only %d images.  Spec " + \
                                                   "file says there should " + \
                                                   "be %d" % \
                                                   (darkName, \
                                                    numImagesInFile, \
                                                    numDarks))
                        imageStartIndex, dlen = \
                            GetStartPositions(darkName, numDarks)
                        images = OpenMultiImm(darkName, darksToSkip -1, \
                                              numDarks - darksToSkip,
                                              imageStartIndex, dlen)
                        darkImage = np.average(images, axis=0)                    
                        
                        
                    except Exception as ex:
                        logger.exception(ex)
                    # End reading dark Images
                    # start reading sample images
                    numScanPoints = len(curScan.data_lines)
                    angles = self.getGeoAngles(curScan, angleNames)
                    scanAngle1 = {}
                    scanAngle2 = {}
                    for i in range(len(angleNames)):
                        scanAngle1[i] = angles[:,i]
                        scanAngle2[i] = []
                    arrayInitializedForScan = False
                    if mask_was_none:
                        mask = True * len(self.getImageToBeUsed()[scannr])
                    mask1 = np.array(mask)
                    logger.debug("mask1.shape %s" % str(mask1.shape))
                    indexesToProcess = (np.where(mask1 == True))[0]
                    logger.debug("indexesToProcess.shape %s" % str(indexesToProcess.shape))
                    logger.debug("indexesToProcess %s" % str(indexesToProcess))
                    
                    foundIndex = 0
                    minorProgressInc = self.progressInc/indexesToProcess.shape[0]
                    minorProgress = self.progress
                    for scanno in indexesToProcess:
                        if self.progressUpdater is not None:
                            self.progressUpdater(minorProgress, self.progressMax)
                        minorProgress += minorProgressInc        
                        fileName = namePrefix + \
                                "%d_%.5d-%.5d" % (scanno, 1,1) + \
                                IMM_STR[1:]
                        logger.debug("Reading filename %s fileName" % fileName)
                        imageStartIndex, dlen = GetStartPositions(fileName, \
                                                                  1)
                        # read single image from file with one image
                        startImage = 0
                        numImages = 1
                        image = OpenMultiImm(fileName, startImage, \
                                             numImages,
                                             imageStartIndex, dlen)[0]
                        if not arrayInitializedForScan:
                            if not intensity.shape[0]:
                                offset = 0
                                intensity = np.zeros((indexesToProcess.shape[0],) + image.shape)
                                arrayInitializedForScan = True
                            else:
                                offset = intensity.shape[0]
                                intensity = np.concatenate((intensity, \
                                                            (np.zeros((indexesToProcess.shape[0],) + image.shape))), \
                                                           axis=0) 
                        logger.debug("foundIndex %s" % foundIndex)
                        logger.debug(" instensity.shape %s" % str(intensity.shape))
                        logger.debug("image.shape %s" % str(image.shape))
                        if self.containsDark[scannr]:
                            intensity[foundIndex + offset,:, :] = image - darkImage
                        else:
                            intensity[foundIndex + offset,:, :] = image - darkImage
                            
                        for i in range(len(angleNames)):
                            scanAngle2[i].append(scanAngle1[i][scanno])
                        foundIndex += 1
                    if len(scanAngle2[0]) > 0:
                        for i in range(len(angleNames)):

                            scanAngle[i] = np.concatenate((scanAngle[i], 
                                                       np.array(scanAngle2[i])), 
                                                       axis=0)  
                    
            else:
                immDataFile = self.immDataFileName[scannr]
                dataDir = os.path.join(imageDir, immDataFile)
                fullFileName = (glob.glob(os.path.join(dataDir, IMM_STR))[0]).replace('\\','\\\\').replace('/','\\\\')
                fullFileName = (glob.glob(os.path.join(dataDir, IMM_STR))[0])
                imageStartIndex = []
                dlen = []
                try:
                    fp = open(fullFileName, "rb")
                    numImages = getNumberOfImages(fp)
                    fp.close()
                    imageStartIndex, dlen = GetStartPositions(fullFileName, \
                                                              numImages)
                    fp = open(fullFileName, "rb")
                    header = readHeader(fp, imageStartIndex[self.scanDataFile[immDataFile][scannr][0]])
                    self.detectorROI = [header['row_beg'], header['row_end'],
                         header['col_beg'], header['col_end']]
                except IOError as ex:
                    logger.error("Problem opening IMM file to get the start indexes" +
                                  str(ex))
                finally: 
                    fp.close()
                if self.haltMap:
                    raise ProcessCanceledException("Process Canceled")
                scan = self.sd.scans[str(scannr)]
                angles = self.getGeoAngles(scan, angleNames)
                scanAngle1 = {}
                scanAngle2 = {}
                for i in range(len(angleNames)):
                    scanAngle1[i] = angles[:,i]
                    scanAngle2[i] = []
                arrayInitializedForScan = False
                foundIndex = 0
                if mask_was_none:
                    mask = True * len(self.getImageToBeUsed()[scannr])
                    
                imagesToSkip = \
                    self.imagesBeforeScan(scannr)
                imagesInScan = \
                    self.imagesInScan(scannr)
                mask1 = np.array(mask)
                indexesToProcess = (np.where(mask1 == True))[0]
                startIndex = indexesToProcess[0]
                numberToProcess = len(indexesToProcess)
                   
                images = OpenMultiImm(fullFileName, \
                                      imagesToSkip + startIndex - 1,
                                      numberToProcess,
                                      imageStartIndex,
                                      dlen)
                minorProgressInc = self.progressInc/indexesToProcess.shape[0]
                minorProgress = self.progress
                for ind in indexesToProcess:
                    if self.progressUpdater is not None:
                        self.progressUpdater(minorProgress, self.progressMax)
                    minorProgress += minorProgressInc        
                    if imageToBeUsed[scannr][ind] and mask[ind]:
                        img = images[ind-startIndex,:,:]
                        img2 = img
    
                        #initialize data Array
                        if not arrayInitializedForScan:
                            imagesToProcess = [imageToBeUsed[scannr][i] and mask[i] \
                                               for i in range(len(imageToBeUsed[scannr]))]
                            if not intensity.shape[0]:
                                offset = 0
                                intensity = np.zeros((np.count_nonzero(imagesToProcess),) + img2.shape)
                                arrayInitializedForScan = True
                            else:
                                offset = intensity.shape[0]
                                intensity = np.concatenate((intensity,
                                                    (np.zeros((np.count_nonzero(imagesToProcess),) + img2.shape))), 
                                                    axis = 0)
                        #add data to intensity array
                        intensity[foundIndex + offset,:,:] = img2
                        for i in range(len(angleNames)):
                            scanAngle2[i].append(scanAngle1[i][ind])
                            
                        foundIndex += 1
                
                if len(scanAngle2[0]) > 0:
                    for i in range(len(angleNames)):
                        scanAngle[i] = \
                            np.concatenate((scanAngle[i], np.array(scanAngle2[i])), \
                                        axis=0)
            self.progress += self.progressInc
            if self.progressUpdater is not None:
                self.progressUpdater(self.progress, self.progressMax)
                 
        # transform scan angles to reciprocal space coordinates for all detector
        # pixels
        angleList = []
        for i in range(len(angleNames)):
            angleList.append(scanAngle[i])
        if self.ubMatrix[scans[0]] is None:
            qx, qy, qz  = hxrd.Ang2Q.area( *angleList, \
                                           roi = self.getDetectorROI(),
                                           Nav=self.getNumPixelsToAverage())
        else:
            qx, qy, qz = hxrd.Ang2Q.area( *angleList, \
                                          roi=self.getDetectorROI(), \
                                          Nav=self.getNumPixelsToAverage(),
                                          UB=self.ubMatrix[scans[0]])
            
        # apply selected transform
        qxTrans, qyTrans, qzTrans = \
            self.transform.do3DTransform(qx, qy, qz)
            
        logger.debug("Shape of qxTrans %s, qyTrans %s, qzTrans %s, intensity %s" %
                      (str(qxTrans.shape), 
                       str(qyTrans.shape), 
                       str(qzTrans.shape),
                       str(intensity.shape)))
        return qxTrans, qyTrans, qzTrans, intensity

    def rawmapSingle(self, scan):
        intensity = np.array([])
                # fourc goniometer in fourc coordinates
        # convention for coordinate system:
        # x: upwards;
        # y: along the incident beam;
        # z: "outboard" (makes coordinate system right-handed).
        # QConversion will set up the goniometer geometry.
        # So the first argument describes the sample rotations, the second the
        # detector rotations and the third the primary beam direction.
        qconv = xu.experiment.QConversion(self.getSampleCircleDirections(), \
                                    self.getDetectorCircleDirections(), \
                                    self.getPrimaryBeamDirection())
    
        # define experimental class for angle conversion
        #
        # ipdir: inplane reference direction (ipdir points into the primary beam
        #        direction at zero angles)
        # ndir:  surface normal of your sample (ndir points in a direction
        #        perpendicular to the primary beam and the innermost detector
        #        rotation axis)
        en = self.getIncidentEnergy()
        hxrd = xu.HXRD(self.getInplaneReferenceDirection(), \
                       self.getSampleSurfaceNormalDirection(), \
                       en=en[self.getAvailableScans()[0]], \
                       qconv=qconv)

        if (self.getDetectorPixelWidth() != None ) and \
            (self.getDistanceToDetector() != None):
            hxrd.Ang2Q.init_area(self.getDetectorPixelDirection1(), \
                self.getDetectorPixelDirection2(), \
                cch1=self.getDetectorCenterChannel()[0], \
                cch2=self.getDetectorCenterChannel()[1], \
                Nch1=self.getDetectorDimensions()[0], \
                Nch2=self.getDetectorDimensions()[0], \
                pwidth1=self.getDetectorPixelWidth()[0], \
                pwidth2=self.getDetectorPixelWidth()[1], \
                distance=self.getDistanceToDetector(), \
                Nav=self.getNumPixelsToAverage(), \
                roi=self.getDetectorROI()) 
        else:
            hxrd.Ang2Q.init_area(self.getDetectorPixelDirection1(), \
                self.getDetectorPixelDirection2(), \
                cch1=self.getDetectorCenterChannel()[0], \
                cch2=self.getDetectorCenterChannel()[1], \
                Nch1=self.getDetectorDimensions()[0], \
                Nch2=self.getDetectorDimensions()[0], \
                chpdeg1=self.getDetectorChannelsPerDegree()[0], \
                chpdeg2=self.getDetectorChannelsPerDegree()[1], \
                Nav=self.getNumPixelsToAverage(), 
                roi=self.getDetectorROI()) 

        # Setup list of angles to produce transform
        angleNames = self.getAngles()
        scanAngle = {}
        for i in range(len(angleNames)):
            scanAngle[i] = np.array([])
        logger.debug("scan %s" % scan)
        angles = self.getGeoAngles(self.sd.scans[str(scan)], angleNames)
        angles = np.array([angles[0],])
        logger.debug("angles %s" % angles)
        
        for i in range(len(angleNames)):
            scanAngle[i] = np.concatenate((scanAngle[i], np.array(angles[:,i])), \
                            axis=0)
        # transform scan angles to reciprocal space coordinates for all detector
        # pixels
        angleList = []
        for i in range(len(angleNames)):
            angleList.append(scanAngle[i])

        if self.ubMatrix[scan] is None:
            qx, qy, qz  = hxrd.Ang2Q.area( *angleList, \
                                           roi = self.getDetectorROI(),
                                           Nav=self.getNumPixelsToAverage())
        else:
            qx, qy, qz = hxrd.Ang2Q.area( *angleList, \
                                          roi=self.getDetectorROI(), \
                                          Nav=self.getNumPixelsToAverage(),
                                          UB=self.ubMatrix[scan])
            
        # apply selected transform
        qxTrans, qyTrans, qzTrans = \
            self.transform.do3DTransform(qx, qy, qz)
            
           
        return qxTrans, qyTrans, qzTrans
