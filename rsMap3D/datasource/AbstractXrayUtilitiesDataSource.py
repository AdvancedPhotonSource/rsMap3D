'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import abc
import numpy as np
from rsMap3D.transforms.unitytransform3d import UnityTransform3D

class AbstractXrayutilitiesDataSource:
    __metaclass__ = abc.ABCMeta
    '''
    Abstract class for loading data needed to analyze using Xrayutilities.
    '''

    def __init__(self, transform=None, 
                 scanList=None, 
                 roi=None, 
                 pixelsToAverage=None,
                 badPixelFile=None):
        '''
        Constructor
        '''
        self.sampleCirclesDirections = None
        self.detectorCircleDirections = None
        self.primaryBeamDirection = None
        self.incidentWavelength = float('nan')
        self.incidentEnergy = None
        self.sampleInplaneReferenceDirection = None
        self.sampleSurfaceNormalDirection = None
        self.detectorCenterChannel = None
        self.detectorDimensions = None
        self.distanceToDetector = float('nan')
        self.detectorPixelWidth = None
        self.detectorChannelPerDegree = None
        self.numPixelsToAverage = pixelsToAverage
        self.detectorROI = roi
        self.detectorAngles = None
        self.sampleAngles = None
        self.detectorAngleNames = None
        self.sampleAngleNames = None
        self.detectorPixelDirection1 = None
        self.detectorPixelDirection2 = None
        self.imageBounds = {}
        self.imageToBeUsed = {}
        self.availableScans = []
        self.ubMatrix = {}
        self.badPixels = []
        self.rangeBounds = None
        self.cancelLoad = False
        self.monitorName = None
        self.monitorScaleFactor = 1.0
        self.filterName = None
        self.filterScaleFactor = 1.0
        if transform == None:
            self.transform = UnityTransform3D()
        else:
            self.transform = transform
        self.badPixelFile = badPixelFile
        
    def findScanQs(self, xmin, xmax, ymin, ymax, zmin, zmax):
        '''
        find the overall boundaries for a scan given the min/max boundaries
        of each image in the scan
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
        Return a list names for the sample and detector circles.
        '''
        return self.getSampleAngleNames() + self.getDetectorAngleNames()
    
        
    def getAvailableScans(self):
        '''
        Return a list of the available scans. Note that loadSource checks to 
        make sure that scans are available in the directory structure
        '''
        return self.availableScans
    
    def getBadPixels(self):
        '''
        Return a list of tuples holding the coordinates of bad pixels.
        '''
        return self.badPixels
    
    def getDetectorAngleNames(self):
        '''
        Return a list of names used in the spec file for the detector angles.
        '''
        return self.detectorAngleNames
    
    def getDetectorCenterChannel(self):
        '''
        '''
        return self.detectorCenterChannel
    
    def getDetectorChannelsPerDegree(self):
        '''
        '''
        return self.detectorChannelPerDegree
    
    def getDetectorCircleDirections(self):
        '''
        '''
        return self.detectorCircleDirections
    
    def getDetectorDimensions(self):
        '''
        '''
        return self.detectorDimensions
    
    def getDistanceToDetector(self):
        '''
        '''
        return self.distanceToDetector
    
    def getDetectorPixelDirection1(self):
        '''
        '''
        return self.detectorPixelDirection1
    
    def getDetectorPixelDirection2(self):
        '''
        '''
        return self.detectorPixelDirection2
    
    def getDetectorPixelWidth(self):
        '''
        '''
        return self.detectorPixelWidth
    
    def getDetectorROI(self):
        '''
        '''
        return self.detectorROI
    
    def getFilterName(self):
        '''
        return the name of monitor variable in spec file.  Returns none if this
        was not defined.
        '''
        return self.filterName

    def getFilterScaleFactor(self):
        '''
        return the scale factor associated with monitor corrections.  Returns 1
        if not defined
        '''
        return self.filterScaleFactor

    @abc.abstractmethod
    def getImage(self, index1=0, index2=0):
        '''
        '''
        return None
    
    def getImageBounds(self, scan):
        '''
        return the boundaries for images in the scan
        '''
        return self.imageBounds[scan]    

    def getImageToBeUsed(self):
        '''
        Return a dictionary containing list of images to be used in each scan.
        '''
        return self.imageToBeUsed
     
    def getIncidentWavelength(self):
        '''
        '''
        return self.incidentWavelength
    
    def getIncidentEnergy(self, index1=0, index2=0):
        '''
        '''
        return self.incidentEnergy
    
    def getInplaneReferenceDirection(self):
        '''
        '''
        return self.sampleInplaneReferenceDirection
    
    def getMonitorName(self):
        '''
        return the name of monitor variable in spec file.  Returns none if this
        was not defined.
        '''
        return self.monitorName

    def getMonitorScaleFactor(self):
        '''
        return the scale factor associated with monitor corrections.  Returns 1
        if not defined
        '''
        return self.monitorScaleFactor

    def getNumPixelsToAverage(self):
        '''
        '''
        return self.numPixelsToAverage
    
    def getOverallRanges(self):
        '''
        Return the boundaries for all data in all availableScans
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

    def getPrimaryBeamDirection(self):
        '''
        '''
        return self.primaryBeamDirection
    
    def getRangeBounds(self):
        '''
        Return boundaries of all scans to be included for analysis
        '''
        return self.rangeBounds
    
    def getSampleAngleNames(self):
        '''
        Return a list of Names used in the spec file for sample circles
        '''
        return self.sampleAngleNames
    
    def getSampleCircleDirections(self):
        '''
        Return a list of sample circle directions.  
        '''
        return self.sampleCirclesDirections
    
    def getSampleSurfaceNormalDirection(self):
        '''
        '''
        return self.sampleSurfaceNormalDirection
    
    def getUBMatrix(self, scan):
        '''
        '''
        return self.ubMatrix[scan]
    
    def inBounds(self, xmin, xmax, ymin, ymax, zmin, zmax):
        '''
        Check to see if the input boundaries have area that lie within the 
        range boundaries specified for analysis.  True if yes, False if no.
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
               
    @abc.abstractmethod
    def loadSource(self, mapHKL=False):
        print "Using Abstract Method"

    def processImageToBeUsed(self):
        '''
        process all available scans to see if the contained images fall within 
        the range boundaries.  Results are stored internally and can be 
        retrieved by getImageToBeUsed()
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
        Set the overall boundary to be used for analysis.
        '''
        self.rangeBounds = rangeBounds;
        self.processImageToBeUsed()
        
    def setTransform(self, transform):
        '''
        '''
        self.transform = transform
        
    def setDetectorROIs(self, roi):
        '''
        '''
        self.detectorROI = roi

    def signalCancelLoadSource(self):
        '''
        Set a flag to cancel a loadSource while looping through scans
        '''
        self.cancelLoad = True
        
