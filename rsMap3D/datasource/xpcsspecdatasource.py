'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
try:
    from pyimm.immheader import readHeader, offsetToNextHeader, getNumberOfImages
    from pyimm.GetImmStartIndex import GetStartPositions
    from pyimm.OpenMultiImm import OpenMultiImm
except ImportError as ex:
    raise ex

import time
import os
from spec2nexus.spec import SpecDataFile
import xrayutilities as xu
import numpy as np
import logging

from rsMap3D.exception.rsmap3dexception import ScanDataMissingException
from rsMap3D.datasource.Sector33SpecDataSource import IMAGE_DIR_MERGE_STR,\
    Sector33SpecFileException,  LoadCanceledException
from rsMap3D.gui.rsm3dcommonstrings import CANCEL_STR
from rsMap3D.datasource.specxmldrivendatasource import SpecXMLDrivenDataSource
from rsMap3D.mappers.abstractmapper import ProcessCanceledException

class XPCSSpecDataSource(SpecXMLDrivenDataSource):
    def __init__(self,
                 projectDir,
                 projectName,
                 projectExtension,
                 instConfigFile,
                 detConfigFile,
                 immDataFile,
                 **kwargs):
        
        super(XPCSSpecDataSource, self).__init__(projectDir,
                                                 projectName,
                                                 projectExtension,
                                                 instConfigFile,
                                                 detConfigFile,
                                                 **kwargs)
        self.immDataFile = immDataFile
        self.cancelLoad = False

    
    def getGeoAngles(self, scan, angleNames):
        """
        This function returns all of the geometry angles for the
        for the scan as a N-by-num_geo array, where N is the number of scan
        points and num_geo is the number of geometry motors.
        """
#        scan = self.sd[scanNo]
        geoAngles = self.getScanAngles(scan, angleNames)
        return geoAngles
        

    def imagesBeforeScan(self, scanNo):
        numImages = 0
        for scanno in xrange(1, scanNo):
            scan = self.sd.scans[str(scanno)]
            numImages += len(scan.data_lines)
            
        return numImages
            
        
    def imagesInScan(self, scanNo):
        scan = self.sd.scans[str(scanNo)]
        numImages = len(scan.data_lines)
        return numImages
        
    def loadSource(self, mapHKL=False):
        #Load up the instrument config XML file
        self.loadInstrumentXMLConfig()
        #Load up the detector configuration file
        self.loadDetectorXMLConfig()
        
        self.specFile = os.path.join(self.projectDir, self.projectName + \
                                     self.projectExt)
        try:
            self.sd = SpecDataFile(self.specFile)
            self.mapHKL = mapHKL
            maxScan = int(self.sd.getMaxScanNumber())
            print str(maxScan) + " scans"
            if self.scans  == None:
                self.scans = range(1, maxScan+1)
            imagePath = os.path.join(self.projectDir, 
                            IMAGE_DIR_MERGE_STR % self.projectName)
            
            self.imageBounds = {}
            self.imageToBeUsed = {}
            self.availableScans = []
            self.incidentEnergy = {}
            self.ubMatrix = {}
            self.scanType = {}
            self.progress = 0
            self.progressInc = 1
            # Zero the progress bar at the beginning.
            if self.progressUpdater <> None:
                self.progressUpdater(self.progress, self.progressMax)
            for scan in self.scans:
                if (self.cancelLoad):
                    self.cancelLoad = False
                    raise LoadCanceledException(CANCEL_STR)
                
                else:
#                     if (os.path.exists(os.path.join(imagePath, \
#                                             SCAN_NUMBER_MERGE_STR % scan))):
                    curScan = self.sd.scans[str(scan)]
                    try:
                        angles = self.getGeoAngles(curScan, self.angleNames)
                        self.availableScans.append(scan)
                        self.scanType[scan] = \
                            self.sd.scans[str(scan)].scanCmd.split()[0]
                        if self.mapHKL==True:
                            self.ubMatrix[scan] = self.getUBMatrix(curScan)
                            if self.ubMatrix[scan] == None:
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
                        if self.progressUpdater <> None:
                            self.progressUpdater(self.progress, self.progressMax)
                        print (('Elapsed time for Finding qs for scan %d: ' +
                               '%.3f seconds') % \
                               (scan, (time.time() - _start_time)))
                        #Make sure to show 100% completion
                    except ScanDataMissingException:
                        print scan
            if self.progressUpdater <> None:
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
        try:
            imagesToSkip = self.imagesBeforeScan(self.scans[0])
            fp = open(str(self.immDataFile), "rb")
            numImages = getNumberOfImages(fp)
            fp.close()
            startIndex, dlen = GetStartPositions(str(self.immDataFile),
                                                  numImages)
            fp = open(str(self.immDataFile), "rb")
            header = readHeader(fp, startIndex[imagesToSkip])
            fp.close()
            self.detectorROI = [header['row_beg'], header['row_end'],
                                header['col_beg'], header['col_end']]
            print ("DetectorROI " + str(self.detectorROI))
        except IOError as e:
            raise IOError("Trouble opening IMM file " + str(self.immDataFile) +
                          "\n " + str(e) )
        self.availableScanTypes = set(self.scanType.values())
        
    def rawmap(self, scans, mask=None):
    
        if mask == None:
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
        for i in xrange(len(angleNames)):
            scanAngle[i] = np.array([])
    
        imageToBeUsed = self.getImageToBeUsed()
        #get startIndex and length for each image in the immFile
        try:
            fp = open(self.immDataFile, "rb")
            numImages = getNumberOfImages(fp)
            fp.close()
            imageStartIndex, dlen = GetStartPositions(self.immDataFile, \
                                                      numImages)
            
        except IOError:
            logging.error("probelm opening IMM file")

        for scannr in scans:
            if self.haltMap:
                raise ProcessCanceledException("Process Canceled")
            scan = self.sd.scans[str(scannr)]
            angles = self.getGeoAngles(scan, angleNames)
            print "angles " + str(angles)
            scanAngle1 = {}
            scanAngle2 = {}
            for i in xrange(len(angleNames)):
                scanAngle1[i] = angles[:,i]
                scanAngle2[i] = []
            print "scanAngle1: " + str(scanAngle1)
            arrayInitializedForScan = False
            foundIndex = 0
            if mask_was_none:
                mask = True * len(self.getImageToBeUseds()[scannr])
                
            imagesToSkip = \
                self.imagesBeforeScan(scannr)
            imagesInScan = \
                self.imagesInScan(scannr)
            print "imagesToSkip " + str(imagesToSkip)
            print "imagesInScan " + str(imagesInScan)
            images = OpenMultiImm(self.immDataFile, \
                                  imagesToSkip+1, 
                                  imagesInScan,
                                  imageStartIndex,
                                  dlen)
            print scan.data.keys()
            print "images.shape " + str(images.shape)
            print "scan.data.keys()[0]] " + str(scan.data.keys()[0])
            print "scan.data[scan.data.keys()[0]] " + str(scan.data[scan.data.keys()[0]])
            for ind in xrange(len(scan.data[scan.data.keys()[0]])):
                if imageToBeUsed[scannr][ind] and mask[ind]:
                    img = images[ind,:,:]
                    print ('img.shape ' + str(img.shape))
                    print ('detectorROI ' + str(self.detectorROI))
                    print ('pixelsToAverage' + str(self.getNumPixelsToAverage()))
#                     img2 = xu.blockAverage2D(img,
#                                              self.getNumPixelsToAverage()[0],
#                                              self.getNumPixelsToAverage()[1],
#                                              roi= self.getDetectorROI())
                    img2 = img
                    print ('img2.shape ' + str(img2.shape))

                    #initialize data Array
                    if not arrayInitializedForScan:
                        imagesToProcess = [imageToBeUsed[scannr][i] and mask[i] \
                                           for i in range(len(imageToBeUsed[scannr]))]
                        if not intensity.shape[0]:
                            offset = 0
                            print( "Creating Intensity img2.shape " + str(img2.shape))
                            print ("imagesToProcess " + str(imagesToProcess))
                            intensity = np.zeros((np.count_nonzero(imagesToProcess),) + img2.shape)
                            print ("Intensity just created Shape" + str(intensity.shape))
                            arrayInitializedForScan = True
                        else:
                            offset = intensity.shape[0]
                            intensity = np.concatenate((intensity,
                                                (np.zeros((np.count_nonzero(imagesToProcess),) + img2.shape))), 
                                                axis = 0)
                            print ("Intensity expanded Shape" + str(intensity.shape))
                    #add data to intensity array
                    intensity[foundIndex + offset,:,:] = img2
                    for i in xrange(len(angleNames)):
                        scanAngle2[i].append(scanAngle1[i][ind])
                    print "scanAngle2 at ind " + str(scanAngle2) + ("ind = %d"% ind)
                        
                    foundIndex += 1
            
            if len(scanAngle2[0]) > 0:
                for i in xrange(len(angleNames)):
                    scanAngle[i] = \
                        np.concatenate((scanAngle[i], np.array(scanAngle2[i])), \
                                    axis=0)
        # transform scan angles to reciprocal space coordinates for all detector
        # pixels
        angleList = []
        for i in xrange(len(angleNames)):
            angleList.append(scanAngle[i])
        print ("angleList" + str(angleList))
            
        if self.ubMatrix[scans[0]] == None:
            qx, qy, qz  = hxrd.Ang2Q.area( *angleList, \
                                           roi = self.getDetectorROI(),
                                           Nav=self.getNumPixelsToAverage())
        else:
            qx, qy, qz = hxrd.Ang2Q.area( *angleList, \
                                          roi=self.getDetectorROI(), \
                                          Nav=self.getNumPixelsToAverage(),
                                          UB=self.ubMatrix[scan[0]])
            
        # apply selected transform
        qxTrans, qyTrans, qzTrans = \
            self.transform.do3DTransform(qx, qy, qz)
            
        
        return qxTrans, qyTrans, qzTrans, intensity
                