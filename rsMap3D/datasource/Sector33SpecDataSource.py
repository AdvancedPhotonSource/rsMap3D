'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import os
from pyspec import spec
from rsMap3D.exception.rsmap3dexception import RSMap3DException,\
    InstConfigException, DetectorConfigException, ScanDataMissingException
from rsMap3D.gui.rsm3dcommonstrings import EMPTY_STR, COMMA_STR, CANCEL_STR
from rsMap3D.datasource.AbstractXrayUtilitiesDataSource \
    import AbstractXrayutilitiesDataSource
import rsMap3D.datasource.InstForXrayutilitiesReader as InstReader
import rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader \
    as DetectorReader
import numpy as np
import xrayutilities as xu
import time
import traceback
import csv
import Image

IMAGE_DIR_MERGE_STR = "images/%s"
SCAN_NUMBER_MERGE_STR = "S%03d"
TIFF_FILE_MERGE_STR = "S%%03d/%s_S%%03d_%%05d.tif"
ONE_EIGHTY = 180.0

class Sector33SpecDataSource(AbstractXrayutilitiesDataSource):
    '''
    Class to load data from spec file and configuration xml files from 
    for the way that data is collected at sector 33.
    :members
    '''


    def __init__(self, 
                 projectDir, 
                 projectName, 
                 projectExtension,
                 instConfigFile, 
                 detConfigFile, 
                 **kwargs):
        '''
        Constructor
        :param projectDir: Directory holding the project file to open
        :param projectName: First part of file name for the project
        :param projectExt: File extension for the project file.
        :param instConfigFile: Full path to Instrument configuration file.
        :param detConfigFile: Full path to the detector configuration file
        :param kwargs: Assorted keyword arguments

        :rtype: Sector33SpecDataSource
        '''
        super(Sector33SpecDataSource, self).__init__(**kwargs)
        self.projectDir = str(projectDir)
        self.projectName = str(projectName)
        self.projectExt = str(projectExtension)
        self.instConfigFile = str(instConfigFile)
        self.detConfigFile = str(detConfigFile)
        try:
            self.scans = kwargs['scanList']
        except KeyError:
            self.scans = None
        
    def findImageQs(self, angles, ub, en):
        '''
        Find the minimum/maximum q boundaries associated with each scan given 
        the angles, energy and UB matrix.
        :param angles: A list of angles used for Q calculations
        :param ub: sample UB matrix
        :param en: Incident Endergy
        '''
        qconv = xu.experiment.QConversion(self.getSampleCircleDirections(), 
                                          self.getDetectorCircleDirections(), 
                                          self.getPrimaryBeamDirection())
        hxrd = xu.HXRD(self.getInplaneReferenceDirection(), 
                       self.getSampleSurfaceNormalDirection(), 
                       en=en, 
                       qconv=qconv)

        cch = self.getDetectorCenterChannel() 
        nav = self.getNumPixelsToAverage()
        roi = self.getDetectorROI()
        detDims = self.getDetectorDimensions()
        hxrd.Ang2Q.init_area(self.getDetectorPixelDirection1(), 
                             self.getDetectorPixelDirection2(), 
                             cch1=cch[0], 
                             cch2=cch[1], 
                             Nch1=detDims[0], 
                             Nch2=detDims[1], 
                             pwidth1=self.detectorPixelWidth[0], 
                             pwidth2=self.detectorPixelWidth[1], 
                             distance = self.distanceToDetector,
                             Nav=self.getNumPixelsToAverage(), 
                             roi=self.getDetectorROI())

        angleList = []
        for i in range(len(angles[0])):
            angleList.append(angles[:,i])
        if ub == None:
            qx, qy, qz = hxrd.Ang2Q.area(*angleList, \
                                     roi=roi, \
                                     Nav=nav)
        else:
            qx, qy, qz = hxrd.Ang2Q.area(*angleList, \
                                     roi=roi, \
                                     Nav=nav, \
                                     UB = ub)
            
        qxTrans, qyTrans, qzTrans = self.transform.do3DTransform(qx, qy, qz)
        
        idx = range(len(qxTrans))
        xmin = [np.min(qxTrans[i]) for i in idx] 
        xmax = [np.max(qxTrans[i]) for i in idx] 
        ymin = [np.min(qyTrans[i]) for i in idx] 
        ymax = [np.max(qyTrans[i]) for i in idx] 
        zmin = [np.min(qzTrans[i]) for i in idx] 
        zmax = [np.max(qzTrans[i]) for i in idx] 
        return (xmin, xmax, ymin, ymax, zmin, zmax)

    def fixGeoAngles(self, scan, angles):
        '''
        Fix the angles using a user selected function.
        :param scan: scan to set the angles for
        :param angles: Array of angles to set for this scan  
        '''
        scanLine = scan.scan_command.split(' ') 
        scannedAngles = []
        if scanLine[0] == 'ascan':
            scannedAngles.append(scanLine[1])
        elif scanLine[0] == 'a2scan':
            scannedAngles.append(scanLine[1])
            scannedAngles.append(scanLine[4])
        elif scanLine[0] == 'a3scan':
            scannedAngles.append(scanLine[1])
            scannedAngles.append(scanLine[4])
            scannedAngles.append(scanLine[7])
        else:
            raise Exception("Scan type not supported by S33SpecDataSource " + \
                            " when angle mapping is used")
        refAngleNames = self.instConfig.getSampleAngleMappingReferenceAngles()
        needToCorrect = False
        for rAngle in refAngleNames:
            if (rAngle in scannedAngles):
                needToCorrect = True
        
        if needToCorrect:
            refAngles = self.getScanAngles(scan, refAngleNames)
            primaryAngles = self.instConfig.getSampleAngleMappingPrimaryAngles()
            functionName = self.instConfig.getSampleAngleMappingFunctionName()
            #Call a defined method to calculate angles from the reference angles.
            method = getattr(self, functionName)
            fixedAngles = method(primaryAngles=primaryAngles, 
                                   referenceAngles=refAngles)
            #print fixedAngles
            for i in range(len(primaryAngles)):
                #print i
                #print primaryAngles[i]
                angles[:,primaryAngles[i]-1] = fixedAngles[i]
        
    def loadSource(self, mapHKL=False):
        '''
        This method does the work of loading data from the files.  This has been
        split off from the constructor to allow this to be threaded and later 
        canceled.
        :param mapHKL: boolean to mark if the data should be mapped to HKL
        '''
        # Load up the instrument configuration file
        try:
            self.instConfig = \
                InstReader.InstForXrayutilitiesReader(self.instConfigFile)
            self.sampleCirclesDirections = \
                self.instConfig.getSampleCircleDirections()
            self.detectorCircleDirections = \
                self.instConfig.getDetectorCircleDirections()
            self.primaryBeamDirection = \
                self.instConfig.getPrimaryBeamDirection()
            self.sampleInplaneReferenceDirection = \
                self.instConfig.getInplaneReferenceDirection()
            self.sampleSurfaceNormalDirection = \
                self.instConfig.getSampleSurfaceNormalDirection()
            self.sampleAngleNames = self.instConfig.getSampleCircleNames()
            self.detectorAngleNames = self.instConfig.getDetectorCircleNames()
            self.monitorName = self.instConfig.getMonitorName()
            self.monitorScaleFactor = self.instConfig.getMonitorScaleFactor()
            self.filterName = self.instConfig.getFilterName()
            self.filterScaleFactor = self.instConfig.getFilterScaleFactor()
            self.angleNames = self.instConfig.getSampleCircleNames() + \
                self.instConfig.getDetectorCircleNames()
            self.projectionDirection = self.instConfig.getProjectionDirection()
        except InstConfigException as ex:
            raise ex
        except Exception as ex:
            print ("---Error Reading instconfig")
            raise ex
        #Load up the detector configuration file
        try:
            detConfig = \
                DetectorReader.DetectorGeometryForXrayutilitiesReader(
                                                      self.detConfigFile)
            detector = detConfig.getDetectorById("Pilatus")
            self.detectorCenterChannel = detConfig.getCenterChannelPixel(detector)
            self.detectorDimensions = detConfig.getNpixels(detector)
            detectorSize = detConfig.getSize(detector)
            self.detectorPixelWidth = \
                [detectorSize[0]/self.detectorDimensions[0],\
                 detectorSize[1]/self.detectorDimensions[1]]
            self.distanceToDetector = detConfig.getDistance(detector) 
            if self.numPixelsToAverage == None:
                self.numPixelsToAverage = [1,1]
            if self.detectorROI == None:
                self.detectorROI = [0, self.detectorDimensions[0],  
                                    0, self.detectorDimensions[1]]
            self.detectorPixelDirection1 = \
                detConfig.getPixelDirection1(detector)
            self.detectorPixelDirection2 = \
                detConfig.getPixelDirection2(detector)
        except DetectorConfigException as ex:
            raise ex
        except Exception as ex:
            print ("---Error Reading detector config")
            raise ex
        self.specFile = os.path.join(self.projectDir, self.projectName + \
                                     self.projectExt)
        imageDir = os.path.join(self.projectDir, \
                                IMAGE_DIR_MERGE_STR % self.projectName)
        self.imageFileTmp = os.path.join(imageDir, \
                                TIFF_FILE_MERGE_STR % 
                                (self.projectName))
        # if needed load up the bad pixel file.
        if not (self.badPixelFile == None):
            
            reader = csv.reader(open(self.badPixelFile), \
                                delimiter=' ', \
                                skipinitialspace=True) 
            self.badPixels = []
            for line in reader:
                newLine = []
                for word in line:
                    if not (word == EMPTY_STR):
                        words = word.split(COMMA_STR)
                        for newWord in words:
                            if not(newWord == EMPTY_STR):
                                newLine.append(newWord)
                for i in range(len(newLine)/2):
                    self.badPixels.append((int(newLine[i*2]), \
                                           int(newLine[2*i+1]))) 
        # id needed load the flat field file
        if not (self.flatFieldFile == None):
            self.flatFieldData = np.array(Image.open(self.flatFieldFile)).T
            print self.flatFieldData
        # Load scan information from the spec file
        try:
            self.sd = spec.SpecDataFile(self.specFile)
            self.mapHKL = mapHKL
            maxScan = max(self.sd.findex.keys())
            print maxScan
            if self.scans  == None:
                self.scans = range(1, maxScan+1)
            imagePath = os.path.join(self.projectDir, 
                            IMAGE_DIR_MERGE_STR % self.projectName)
            
            self.imageBounds = {}
            self.imageToBeUsed = {}
            self.availableScans = []
            self.incidentEnergy = {}
            self.ubMatrix = {}
            progress = 1
            for scan in self.scans:
                if (self.cancelLoad):
                    self.cancelLoad = False
                    raise LoadCanceledException(CANCEL_STR)
                
                else:
                    if (os.path.exists(os.path.join(imagePath, \
                                            SCAN_NUMBER_MERGE_STR % scan))):
                        curScan = self.sd[scan]
                        self.availableScans.append(scan)
                        angles = self.getGeoAngles(curScan, self.angleNames)
                        if self.mapHKL==True:
                            self.ubMatrix[scan] = curScan.UB
                        else:
                            self.ubMatrix[scan] = None
                        self.incidentEnergy[scan] =curScan.energy
                        _start_time = time.time()
                        self.imageBounds[scan] = \
                            self.findImageQs(angles, \
                                             self.ubMatrix[scan], \
                                             self.incidentEnergy[scan])
                        print (('Elapsed time for Finding qs for scan %d: ' +
                               '%.3f seconds') % \
                               (scan, (time.time() - _start_time)))
                if self.progressUpdater <> None:
                    self.progressUpdater(progress, len(self.scans))
                progress +=1        
        except IOError:
            raise IOError( "Cannot open file " + str(self.specFile))
        if len(self.getAvailableScans()) == 0:
            raise ScanDataMissingException("Could not find scan data for " + \
                                           "input file \n" + self.specFile + \
                                           "\nOne possible reason for this " + \
                                           "is that the image files are " + \
                                           "missing.  Images are assumed " + \
                                           "to be in " + \
                                           os.path.join(self.projectDir, 
                                        IMAGE_DIR_MERGE_STR % self.projectName))


    def getGeoAngles(self, scan, angleNames):
        """
        This function returns all of the geometry angles for the
        for the scan as a N-by-num_geo array, where N is the number of scan
        points and num_geo is the number of geometry motors.
        """
#        scan = self.sd[scanNo]
        geoAngles = self.getScanAngles(scan, angleNames)
        if not (self.instConfig.getSampleAngleMappingFunctionName() == ""):
            tb = None
            try:
                self.fixGeoAngles(scan, geoAngles)
            except Exception as ex:
                tb = traceback.format_exc()
                print "Handling exception in getGeoAngles"
                print ex
                print tb
        return geoAngles
    
    def getScanAngles(self, scan, angleNames):
        """
        This function returns all of the geometry angles for the
        for the scan as a N-by-num_geo array, where N is the number of scan
        points and num_geo is the number of geometry motors.
        :param scan: scan from which to retrieve the angles
        :params angleNames: a list of names for the angles to be returned
        """
        geoAngles = np.zeros((scan.data.shape[0], len(angleNames)))
        for i, name in enumerate(angleNames):
            v = scan.scandata.get(name)
            if v.size == 1:
                v = np.ones(scan.data.shape[0]) * v
            geoAngles[:,i] = v
        

        return geoAngles
        
    def _calc_eulerian_from_kappa(self, primaryAngles=None, \
                                  referenceAngles = None):
        """
        Calculate the eulerian sample angles from the kappa stage angles.
        :param primaryAngles:  list of sample axis numbers to be handled by 
        the conversion
        :param referenceAngles: list of reference angles to be used in angle 
        conversion
        """
        
        keta = referenceAngles[:,0] * np.pi/ONE_EIGHTY
        kappa = referenceAngles[:,1] * np.pi/ONE_EIGHTY
        kphi = referenceAngles[:,2] * np.pi/ONE_EIGHTY
        self.kalpha = 49.9945 * np.pi/ONE_EIGHTY
        self.kappa_inverted = False

        _t1 = np.arctan(np.tan(kappa / 2.0) * np.cos(self.kalpha))
        
        if self.kappa_inverted:
            eta = (keta + _t1) * ONE_EIGHTY/np.pi
            phi = (kphi + _t1) * ONE_EIGHTY/np.pi
        else:
            eta = (keta - _t1) * ONE_EIGHTY/np.pi
            phi = (kphi - _t1) * ONE_EIGHTY/np.pi
        chi = 2.0 * np.arcsin(np.sin(kappa / 2.0) * \
                              np.sin(self.kalpha)) * ONE_EIGHTY/np.pi
        
        return eta, chi, phi
        
    

class LoadCanceledException(RSMap3DException):
    '''
    Exception Thrown when loading data is canceled.
    '''
    def __init__(self, message):
        super(LoadCanceledException, self).__init__(message)

