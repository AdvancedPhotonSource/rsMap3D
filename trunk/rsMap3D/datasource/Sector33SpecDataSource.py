'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import os
from pyspec import spec
from rsMap3D.datasource.AbstractXrayUtilitiesDataSource \
    import AbstractXrayutilitiesDataSource
import rsMap3D.datasource.InstForXrayutilitiesReader as InstReader
import rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader \
    as DetectorReader
import numpy as np
import xrayutilities as xu
import time

class Sector33SpecDataSource(AbstractXrayutilitiesDataSource):
    '''
    classdocs
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
        '''
        super(Sector33SpecDataSource, self).__init__(**kwargs)
        self.projectDir = str(projectDir)
        self.projectName = str(projectName)
        self.projectExt = str(projectExtension)
        self.instConfigFile = str(instConfigFile)
        self.detConfigFile = str(detConfigFile)
        if kwargs['scanList']  == None:
            self.scans = None
        else:
            self.scans = kwargs['scanList']
        self.cancelLoad = False
        
    def loadSource(self):
        instConfig = InstReader.InstForXrayutilitiesReader(self.instConfigFile)
        self.sampleCirclesDirections = instConfig.getSampleCircleDirections()
        self.detectorCircleDirections = instConfig.getDetectorCircleDirections()
        self.primaryBeamDirection = instConfig.getPrimaryBeamDirection()
        self.sampleInplaneReferenceDirection = \
            instConfig.getInplaneReferenceDirection()
        self.sampleSurfaceNormalDirection = \
            instConfig.getSampleSurfaceNormalDirection()
        self.sampleAngleNames = instConfig.getSampleCircleNames()
        self.detectorAngleNames = instConfig.getDetectorCircleNames()
        
        
        detConfig = \
            DetectorReader.DetectorGeometryForXrayutilitiesReader(self.detConfigFile)
        detector = detConfig.getDetectorById("Pilatus")
        self.detectorCenterChannel = detConfig.getCenterChannelPixel(detector)
        self.detectorDimensions = detConfig.getNpixels(detector)
        detectorSize = detConfig.getSize(detector)
        self.detectorPixelWidth = [detectorSize[0]/self.detectorDimensions[0],
                                   detectorSize[1]/self.detectorDimensions[1]]
        self.distanceToDetector = detConfig.getDistance(detector) 
        if self.numPixelsToAverage == None:
            self.numPixelsToAverage = [1,1]
        if self.detectorROI == None:
            self.detectorROI = [0, self.detectorDimensions[0],  
                                0, self.detectorDimensions[1]]
        self.detectorPixelDirection1 = detConfig.getPixelDirection1(detector)
        self.detectorPixelDirection2 = detConfig.getPixelDirection2(detector)
        
        self.angleNames = instConfig.getSampleCircleNames() + \
            instConfig.getDetectorCircleNames()
        self.specFile = os.path.join(self.projectDir, self.projectName + \
                                     self.projectExt)
        imageDir = os.path.join(self.projectDir, "images/%s" % self.projectName)
        self.imageFileTmp = os.path.join(imageDir, \
                                "S%%03d/%s_S%%03d_%%05d.tif" % 
                                (self.projectName))

        try:
            self.sd = spec.SpecDataFile(self.specFile)
            maxScan = max(self.sd.findex.keys())
            print maxScan
            if self.scans  == None:
                self.scans = range(1, maxScan+1)
            imagePath = os.path.join(self.projectDir, 
                            "images/%s" % self.projectName)
            
            self.imageBounds = {}
            self.imageToBeUsed = {}
            self.availableScans = []
            self.incidentEnergy = {}
            for scan in self.scans:
                if (self.cancelLoad):
                    raise LoadCanceledException()
                else:
                    if (os.path.exists(os.path.join(imagePath, "S%03d" % scan))):
                        curScan = self.sd[scan]
                        self.availableScans.append(scan)
                        angles = self.getGeoAngles(curScan, self.angleNames)
                        ub = curScan.UB
                        self.incidentEnergy[scan] = \
                            curScan.energy
                        _start_time = time.time()
                        self.imageBounds[scan] = \
                            self.findImageQs(angles, ub, self.incidentEnergy[scan])
                        print 'Elapsed time for Finding qs for scan %d: %.3f seconds' % \
                            (scan, (time.time() - _start_time))        
        except IOError:
            raise IOError( "Cannot open file " + str(self.specFile))
        
        
    def cancelLoadSource(self):
        self.cancelLoad = True
        
    def findImageQs(self, angles, ub, en):
        '''
        '''
        qconv = xu.experiment.QConversion(self.getSampleCircleDirections(), 
                                          self.getDetectorCircleDirections(), 
                                          self.getPrimaryBeamDirection())
        hxrd = xu.HXRD(self.getInplaneReferenceDirection(), 
                       self.getSampleSurfaceNormalDirection(), 
                       en=en, 
                       qconv=qconv)

        cch = self.getDetectorCenterChannel() 
#        chpdeg = self.getDetectorChannelsPerDegree()
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

        qx, qy, qz = hxrd.Ang2Q.area(angles[:,0], \
                                     angles[:,1], \
                                     angles[:,2], \
                                     angles[:,3], \
                                     roi=roi, \
                                     Nav=nav)
        qxTrans, qyTrans, qzTrans = self.transform.do3DTransform(qx, qy, qz)
        
        idx = range(len(qxTrans))
        xmin = [np.min(qxTrans[i]) for i in idx] 
        xmax = [np.max(qxTrans[i]) for i in idx] 
        ymin = [np.min(qyTrans[i]) for i in idx] 
        ymax = [np.max(qyTrans[i]) for i in idx] 
        zmin = [np.min(qzTrans[i]) for i in idx] 
        zmax = [np.max(qzTrans[i]) for i in idx] 
        return (xmin, xmax, ymin, ymax, zmin, zmax)

    def findScanQs(self, xmin, xmax, ymin, ymax, zmin, zmax):
        '''
        '''
        scanXmin = np.min( xmin)
        scanXmax = np.max( xmax)
        scanYmin = np.min( ymin)
        scanYmax = np.max(  ymax)
        scanZmin = np.min(  zmin)
        scanZmax = np.max(  zmax)
        return scanXmin, scanXmax, scanYmin, scanYmax, scanZmin, scanZmax

    def getAngles(self):
        '''
        '''
        return self.getSampleAngleNames() + self.getDetectorAngleNames()
    
    def getAvailableScans(self):
        '''
        '''
        return self.availableScans
    
    def getDetectorAngles(self):
        '''
        '''
        return
    
    def getDetectorAngleNames(self):
        return self.detectorAngleNames
    
    def getImageBounds(self, scan):
        '''
        '''
        return self.imageBounds[scan]    

    def getImage(self):
        '''
        '''
        return
    
    def getImageToBeUsed(self):
        '''
        '''
        return self.imageToBeUsed
     
    def getOverallRanges(self):
        '''
        '''
        overallXmin = float("Infinity")
        overallXmax = float("-Infinity")
        overallYmin = float("Infinity")
        overallYmax = float("-Infinity")
        overallZmin = float("Infinity")
        overallZmax = float("-Infinity")
        
        for scan in self.availableScans:
            overallXmin = min( overallXmin, np.min(self.imageBounds[scan][0]))
            overallXmax = max( overallXmax, np.max(self.imageBounds[scan][1]))
            overallYmin = min( overallYmin, np.min(self.imageBounds[scan][2]))
            overallYmax = max( overallYmax, np.max(self.imageBounds[scan][3]))
            overallZmin = min( overallZmin, np.min(self.imageBounds[scan][4]))
            overallZmax = max( overallZmax, np.max(self.imageBounds[scan][5]))
                    
        return overallXmin, overallXmax, overallYmin, overallYmax, \
               overallZmin, overallZmax

    def getRangeBounds(self):
        '''
        '''
        return self.rangeBounds
    
    def getSampleAngles(self):
        '''
        '''
        return
    
    def getSampleAngleNames(self):
        '''
        '''
        return self.sampleAngleNames
    
            
    def inBounds(self, xmin, xmax, ymin, ymax, zmin, zmax):
        '''
        '''
        return ((xmin >= self.rangeBounds[0] and \
                 xmin <= self.rangeBounds[1]) or \
                (xmax >= self.rangeBounds[0] and \
                 xmax <= self.rangeBounds[1])) and \
                ((ymin >= self.rangeBounds[2] and \
                  ymin <= self.rangeBounds[3]) or \
                (ymax >= self.rangeBounds[2] and \
                 ymax <= self.rangeBounds[3])) and \
                ((zmin >= self.rangeBounds[4] and \
                  zmin <= self.rangeBounds[5]) or \
                (zmax >= self.rangeBounds[4] and \
                 zmax <= self.rangeBounds[5]))
               
    def processImageToBeUsed(self):
        '''
        '''
        self.imageToBeUsed = {}
        for scan in self.availableScans:
            inUse = []
            for i in xrange(len(self.imageBounds[scan][0])):
                bounds = self.imageBounds[scan]
                if self.inBounds(bounds[0][i], \
                                 bounds[1][i], \
                                 bounds[2][i], \
                                 bounds[3][i], \
                                 bounds[4][i], \
                                 bounds[5][i]):
                    inUse.append(True)
                else:
                    inUse.append(False)
            self.imageToBeUsed[scan] = inUse
 
    def setRangeBounds(self, rangeBounds):
        '''
        '''
        self.rangeBounds = rangeBounds;
        self.processImageToBeUsed()
        
    def getGeoAngles(self, scan, angleNames):
        """
        This function returns all of the geometry angles for the
        for the scan as a N-by-num_geo array, where N is the number of scan
        points and num_geo is the number of geometry motors.
        """
#        scan = self.sd[scanNo]
        geo_angles = np.zeros((scan.data.shape[0], len(angleNames)))
        for i, name in enumerate(angleNames):
            v = scan.scandata.get(name)
            if v.size == 1:
                v = np.ones(scan.data.shape[0]) * v
            geo_angles[:,i] = v
        
        return geo_angles

class LoadCanceledException(Exception):
    def __init__(self):
        super(LoadCanceledException, self).__init__()

            
if __name__ == '__main__':
    source = Sector33SpecDataSource('/local/RSM/BFO_LAO', '130123B_2', ".spc"\
                                '/local/RSM/33BM-instForXrayutilities.xml', \
                                '/local/RSM/33bmDetectorGeometry.xml')