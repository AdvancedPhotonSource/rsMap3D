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
import csv
import Image
import matplotlib.pyplot as plt

class Sector33SpecDataSource(AbstractXrayutilitiesDataSource):
    '''
    Class to load data from spec file and configuration xml files from 
    for the way that data is collected at sector 33.
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
        try:
            self.scans = kwargs['scanList']
        except KeyError:
            self.scans = None
        
    def findImageQs(self, angles, ub, en):
        '''
        Find the minimum/maximum q boundaries associated with each scan given 
        the angles, energy and UB matrix.
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

        if ub == None:
            qx, qy, qz = hxrd.Ang2Q.area(angles[:,0], \
                                     angles[:,1], \
                                     angles[:,2], \
                                     angles[:,3], \
                                     roi=roi, \
                                     Nav=nav)
        else:
            qx, qy, qz = hxrd.Ang2Q.area(angles[:,0], \
                                     angles[:,1], \
                                     angles[:,2], \
                                     angles[:,3], \
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

    def getImage(self):
        '''
        '''
        return
    
    def loadSource(self, mapHKL=False):
        '''
        This method does the work of loading data from the files.  This has been
        split off from the constructor to allow this to be threaded and later 
        canceled.
        '''
        # Load up the instrument configuration file
        try:
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
            self.monitorName = instConfig.getMonitorName()
            self.monitorScaleFactor = instConfig.getMonitorScaleFactor()
            self.filterName = instConfig.getFilterName()
            self.filterScaleFactor = instConfig.getFilterScaleFactor()
        except Exception as ex:
            print ("---Error Reading instconfig")
            raise ex
        #Load up the detector configuration file
        try:
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
        except Exception as ex:
            print ("---Error Reading detconfig")
            raise ex
        self.angleNames = instConfig.getSampleCircleNames() + \
            instConfig.getDetectorCircleNames()
        self.specFile = os.path.join(self.projectDir, self.projectName + \
                                     self.projectExt)
        imageDir = os.path.join(self.projectDir, "images/%s" % self.projectName)
        self.imageFileTmp = os.path.join(imageDir, \
                                "S%%03d/%s_S%%03d_%%05d.tif" % 
                                (self.projectName))
        # if needed load up the bad pixel file.
        if not (self.badPixelFile == None):
            
            reader = csv.reader(open(self.badPixelFile), delimiter=' ',skipinitialspace=True) 
            self.badPixels = []
            for line in reader:
                newLine = []
                for word in line:
                    if not (word == ''):
                        words = word.split(',')
                        for newWord in words:
                            if not(newWord == ''):
                                newLine.append(newWord)
                for i in range(len(newLine)/2):
                    self.badPixels.append((int(newLine[i*2]), int(newLine[2*i+1]))) 
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
                            "images/%s" % self.projectName)
            
            self.imageBounds = {}
            self.imageToBeUsed = {}
            self.availableScans = []
            self.incidentEnergy = {}
            self.ubMatrix = {}
            for scan in self.scans:
                if (self.cancelLoad):
                    self.cancelLoad = False
                    raise LoadCanceledException()
                
                else:
                    if (os.path.exists(os.path.join(imagePath, "S%03d" % scan))):
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
        except IOError:
            raise IOError( "Cannot open file " + str(self.specFile))
        
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
    '''
    Exception Thrown when loading data is canceled.
    '''
    def __init__(self):
        super(LoadCanceledException, self).__init__()

            
if __name__ == '__main__':
    source = Sector33SpecDataSource('/local/RSM/BFO_LAO', '130123B_2', ".spc"\
                                '/local/RSM/33BM-instForXrayutilities.xml', \
                                '/local/RSM/33bmDetectorGeometry.xml')