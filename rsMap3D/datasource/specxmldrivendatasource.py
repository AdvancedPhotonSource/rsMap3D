'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
import numpy as np
import xrayutilities as xu

import rsMap3D.datasource.InstForXrayutilitiesReader \
    as InstReader
import rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader \
    as DetectorReader
import logging
from rsMap3D.config.rsmap3dlogging import METHOD_ENTER_STR, METHOD_EXIT_STR
from rsMap3D.datasource.AbstractXrayUtilitiesDataSource \
    import AbstractXrayutilitiesDataSource
from rsMap3D.exception.rsmap3dexception import ScanDataMissingException,\
    InstConfigException, DetectorConfigException, RSMap3DException
logger = logging.getLogger(__name__)

class SpecXMLDrivenDataSource(AbstractXrayutilitiesDataSource):
    
    def __init__(self,
                 projectDir,
                 projectName,
                 projectExtension,
                 instConfigFile,
                 detConfigFile,
                 **kwargs):
        super(SpecXMLDrivenDataSource, self).__init__(**kwargs)
        logger.debug(METHOD_ENTER_STR)
        self.projectDir = str(projectDir)
        self.projectName = str(projectName)
        self.projectExt = str(projectExtension)
        self.instConfigFile = str(instConfigFile)
        self.detConfigFile = str(detConfigFile)
        detConfig = \
                DetectorReader.DetectorGeometryForXrayutilitiesReader(
                                                      self.detConfigFile)
        firstDetector = detConfig.getDetectors().findall(detConfig.DETECTOR)[0]
        firstDetectorID = firstDetector.find(detConfig.DETECTOR_ID).text 
        
        self.currentDetector = \
            detConfig.getDetectorById(firstDetectorID)
        self.progress = 0
        self.progressInc = 1
        self.progressMax = 1
        self.haltMap = False
        self.availableScanTypes = []
        try:
            self.scans = kwargs['scanList']
        except KeyError:
            self.scans = None
        logger.debug(METHOD_EXIT_STR)

    #@profile
    def findImageQs(self, angles, ub, en):
        '''
        Find the minimum/maximum q boundaries associated with each scan given 
        the angles, energy and UB matrix.
        :param angles: A list of angles used for Q calculations
        :param ub: sample UB matrix
        :param en: Incident Energy
        '''
        logger.debug(METHOD_ENTER_STR)
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

        maxImageMem = self.appConfig.getMaxImageMemory()
        imageSize = self.getDetectorDimensions()[0] * \
                    self.getDetectorDimensions()[1]
        numImages = len(angles)
        if imageSize*4*numImages <= maxImageMem:
            self.progressMax = len( self.scans) * 100
            self.progressInc = 1.0 * 100.0
            if self.progressUpdater is not None:
                self.progressUpdater(self.progress, self.progressMax)
            self.progress += self.progressInc        
            angleList = []
            logger.debug("angles " + str(angles) )
            for i in range(len(angles[0])):
                angleList.append(angles[:,i])
            if ub is None:
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
        else:
            nPasses = int(imageSize*4*numImages/ maxImageMem + 1)
            xmin = []
            xmax = []
            ymin = []
            ymax = []
            zmin = []
            zmax = []
            for thisPass in range(nPasses):
                self.progressMax = len( self.scans) * 100.0
                self.progressInc = 1.0 / nPasses * 100.0
                if self.progressUpdater is not None:
                    self.progressUpdater(self.progress, self.progressMax)
                self.progress += self.progressInc        
                firstImageInPass = int(thisPass*numImages/nPasses)
                lastImageInPass = int((thisPass+1)*numImages/nPasses)
                angleList = []
                logger.debug("angles " + str(angles) )
                for i in range(len(angles[0])):
                    logger.debug("angles in pass " + str(angles[firstImageInPass:lastImageInPass,i]) )
                    angleList.append(angles[firstImageInPass:lastImageInPass,i])
                logger.debug("angleList " + str(angleList) )
                if ub is None:
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
                [xmin.append(np.min(qxTrans[i])) for i in idx] 
                [xmax.append(np.max(qxTrans[i])) for i in idx] 
                [ymin.append(np.min(qyTrans[i])) for i in idx] 
                [ymax.append(np.max(qyTrans[i])) for i in idx] 
                [zmin.append(np.min(qzTrans[i])) for i in idx] 
                [zmax.append(np.max(qzTrans[i])) for i in idx] 
                
        logger.debug(METHOD_EXIT_STR % str((xmin, xmax, ymin, ymax, zmin, zmax))) 
        return (xmin, xmax, ymin, ymax, zmin, zmax)

    def getReferenceNames(self):
        '''
        '''
        names = []
        names.extend(self.getSampleAngleNames())
        names.extend(self.getDetectorAngleNames())
        return names
    
    def getReferenceValues(self, scan):
        '''
        '''
        
        try:
            angles = self.getGeoAngles(self.sd.scans[str(scan)], 
                                       self.getReferenceNames())
        except ScanDataMissingException as e:
            logger.error ("Get Reference Values Scan data missing " + 
                           str(e.message))
        return angles

    def getScanAngles(self, scan, angleNames):
        """
        This function returns all of the geometry angles for the
        for the scan as a N-by-num_geo array, where N is the number of scan
        points and num_geo is the number of geometry motors.
        :param scan: scan from which to retrieve the angles
        :params angleNames: a list of names for the angles to be returned
        """
        try:
            dataKeys = scan.data.keys()
        except IndexError as ie:
            logger.exception(str(ie) )
            raise ie
        except Exception as ex:
            logger.exception(str(ex) + "at scan " + str(scan.scanNum))
            raise ex
        if len(dataKeys) == 0:
            raise ScanDataMissingException("No Scan Data Found for scan " + 
                                           scan.scanNum)
        logger.debug("dataKeys:  %s", dataKeys)
        geoAngles = np.zeros((len(scan.data[list(dataKeys)[0]]), len(angleNames)))
        for i, name in enumerate(angleNames):
            v = scan.data.get(name)
            p = scan.positioner.get(name)

            if v != None:
                if len(v) == 1:
                    v = np.ones(len(scan.data[list(scan.data.keys())[0]])) * v
            elif p != None:
                logger.debug(scan.data.keys())
                logger.debug(scan.data[list(scan.data.keys())[0]])
                v = np.ones(len(scan.data[list(scan.data.keys())[0]])) * p
            else:
                raise InstConfigException("Could not find angle " + name + \
                                          " in scan parameters")
            geoAngles[:,i] = v
        return geoAngles
        
    def loadDetectorXMLConfig(self):
        try:
            detConfig = \
                DetectorReader.DetectorGeometryForXrayutilitiesReader(
                                                      self.detConfigFile)
            detector = detConfig.getDetectorById(self.currentDetector)
            self.detectorCenterChannel = \
                detConfig.getCenterChannelPixel(detector)
            self.detectorDimensions = detConfig.getNpixels(detector)
            detectorSize = detConfig.getSize(detector)
            self.detectorPixelWidth = \
                [detectorSize[0]/self.detectorDimensions[0],\
                 detectorSize[1]/self.detectorDimensions[1]]
            self.distanceToDetector = detConfig.getDistance(detector) 
            if self.numPixelsToAverage is None:
                self.numPixelsToAverage = [1,1]
            if self.detectorROI is None:
                self.detectorROI = [0, self.detectorDimensions[0],  
                                    0, self.detectorDimensions[1]]
            self.detectorPixelDirection1 = \
                detConfig.getPixelDirection1(detector)
            self.detectorPixelDirection2 = \
                detConfig.getPixelDirection2(detector)
        except DetectorConfigException as ex:
            raise ex
        except RSMap3DException as ex:
            logger.error ("---Error Reading detector config")
            raise ex
        except Exception as ex:
            logger.error ("---Unhandled Exception in loading detector config")
            raise ex
        
    def loadInstrumentXMLConfig(self):
        try:
            self.instConfig = \
                InstReader.InstForXrayutilitiesReader(self.instConfigFile)
            self.sampleCircleDirections = \
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
        except RSMap3DException as ex:
            logger.error ("---Error Reading instrument config")
            raise ex
        except Exception as ex:
            logger.error( "Unhandle Exception loading instrument config" + 
                           str(ex))
            raise ex
        
    
    def setCurrentDetector(self, currentDetector):
        self.currentDetector = currentDetector
        
    def setScanTypeUsed(self, scanType, used):
        for scan in self.availableScans:
            if self.scanType[scan] == scanType:
                for i in range(len(self.imageToBeUsed[scan])):
                    self.imageToBeUsed[scan][i] = used
