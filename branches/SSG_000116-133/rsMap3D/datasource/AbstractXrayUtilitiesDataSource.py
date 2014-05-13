'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import abc
import numpy as np
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.gui.rsm3dcommonstrings import POSITIVE_INFINITY, \
    NEGATIVE_INFINITY, XMIN_INDEX, XMAX_INDEX, YMIN_INDEX, YMAX_INDEX, \
    ZMIN_INDEX, ZMAX_INDEX

class AbstractXrayutilitiesDataSource:
    __metaclass__ = abc.ABCMeta
    '''
    Abstract class for loading data needed to analyze using xrayutilities.
    '''

    def __init__(self, transform=None, 
                 scanList=None, 
                 roi=None, 
                 pixelsToAverage=None,
                 badPixelFile=None,
                 flatFieldFile=None):
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
        self.projectionDirection = None
        self.filterName = None
        self.filterScaleFactor = 1.0
        if transform == None:
            self.transform = UnityTransform3D()
        else:
            self.transform = transform
        self.badPixelFile = badPixelFile
        self.flatFieldFile = flatFieldFile
        self.flatFieldData = None
        self.progressUpdater = None
        
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
        Return the center channel of the detector
        '''
        return self.detectorCenterChannel
    
    def getDetectorChannelsPerDegree(self):
        '''
        Return the channels/degree for the detector
        '''
        return self.detectorChannelPerDegree
    
    def getDetectorCircleDirections(self):
        '''
        return a list of detector circle directions
        '''
        return self.detectorCircleDirections
    
    def getDetectorDimensions(self):
        '''
        Return the dimensions (in pixels of the detector
        '''
        return self.detectorDimensions
    
    def getDetectorPixelDirection1(self):
        '''
        Return the direction of increasing pixels for the area detector first
        dimension.
        '''
        return self.detectorPixelDirection1
    
    def getDetectorPixelDirection2(self):
        '''
        Return the direction of increasing pixels for the area detector second
        dimension.
        '''
        return self.detectorPixelDirection2
    
    def getDetectorPixelWidth(self):
        '''
        return the pixel with in mm of the detector
        '''
        return self.detectorPixelWidth
    
    def getDetectorROI(self):
        '''
        return the detector region of interest
        '''
        return self.detectorROI
    
    def getDistanceToDetector(self):
        '''
        Return the distance from sample to detector
        '''
        return self.distanceToDetector
    
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

    def getFlatFieldData(self):
        '''
        Return image for the flat field correction
        ''' 
        return self.flatFieldData
    
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
        Return the incident wavelength for a scan
        '''
        return self.incidentWavelength
    
    def getIncidentEnergy(self, index1=0, index2=0):
        '''
        return the incident energy for a scan
        '''
        return self.incidentEnergy
    
    def getInplaneReferenceDirection(self):
        '''
        Return the inplane reference direction
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
        Return the number of pixels to average in each direction.
        '''
        return self.numPixelsToAverage
    
    def getOverallRanges(self):
        '''
        Return the boundaries for all data in all availableScans
        '''
        overallXmin = float(POSITIVE_INFINITY)
        overallXmax = float(NEGATIVE_INFINITY)
        overallYmin = float(POSITIVE_INFINITY)
        overallYmax = float(NEGATIVE_INFINITY)
        overallZmin = float(POSITIVE_INFINITY)
        overallZmax = float(NEGATIVE_INFINITY)
        
        for scan in self.availableScans:
            overallXmin = min( overallXmin, \
                               np.min(self.imageBounds[scan][XMIN_INDEX]))
            overallXmax = max( overallXmax, \
                               np.max(self.imageBounds[scan][XMAX_INDEX]))
            overallYmin = min( overallYmin, \
                               np.min(self.imageBounds[scan][YMIN_INDEX]))
            overallYmax = max( overallYmax, \
                               np.max(self.imageBounds[scan][YMAX_INDEX]))
            overallZmin = min( overallZmin, \
                               np.min(self.imageBounds[scan][ZMIN_INDEX]))
            overallZmax = max( overallZmax, \
                               np.max(self.imageBounds[scan][ZMAX_INDEX]))
                    
        return overallXmin, overallXmax, overallYmin, overallYmax, \
               overallZmin, overallZmax

    def getPrimaryBeamDirection(self):
        '''
        Return the primary beam direction
        '''
        return self.primaryBeamDirection
    
    def getProjectionDirection(self):
        '''
        Return the axis direction for producing stereographic projection.
        '''
        return self.projectionDirection
    
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
        Return the sample surface normal direction
        '''
        return self.sampleSurfaceNormalDirection
    
    def getUBMatrix(self, scan):
        '''
        Return the UB matrix
        '''
        return self.ubMatrix[scan]
    
    def inBounds(self, xmin, xmax, ymin, ymax, zmin, zmax):
        '''
        Check to see if the input boundaries have area that lie within the 
        range boundaries specified for analysis.  True if yes, False if no.
        '''
        return ((xmin >= self.rangeBounds[XMIN_INDEX] and \
                 xmin <= self.rangeBounds[XMAX_INDEX]) or \
                (xmax >= self.rangeBounds[XMIN_INDEX] and \
                 xmax <= self.rangeBounds[XMAX_INDEX])) and \
                ((ymin >= self.rangeBounds[YMIN_INDEX] and \
                  ymin <= self.rangeBounds[YMAX_INDEX]) or \
                (ymax >= self.rangeBounds[YMIN_INDEX] and \
                 ymax <= self.rangeBounds[YMAX_INDEX])) and \
                ((zmin >= self.rangeBounds[ZMIN_INDEX] and \
                  zmin <= self.rangeBounds[ZMAX_INDEX]) or \
                (zmax >= self.rangeBounds[ZMIN_INDEX] and \
                 zmax <= self.rangeBounds[ZMAX_INDEX]))
               
    @abc.abstractmethod
    def loadSource(self, mapHKL=False):
        '''
        Method to load data into the source for use in analysis.  This should
        be defined by the subclass
        '''
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
                if self.inBounds(bounds[XMIN_INDEX][i], \
                                 bounds[XMAX_INDEX][i], \
                                 bounds[YMIN_INDEX][i], \
                                 bounds[YMAX_INDEX][i], \
                                 bounds[ZMIN_INDEX][i], \
                                 bounds[ZMAX_INDEX][i]):
                    inUse.append(True)
                else:
                    inUse.append(False)
            self.imageToBeUsed[scan] = inUse
            
    def setProgressUpdater(self, updater):
        self.progressUpdater = updater
 
    def setRangeBounds(self, rangeBounds):
        '''
        Set the overall boundary to be used for analysis.
        '''
        self.rangeBounds = rangeBounds;
        self.processImageToBeUsed()
        
    def setTransform(self, transform):
        '''
        set the coordinate transform class to be used to 
        transform qx, qy, qz in the output data.
        '''
        self.transform = transform
        
    def setDetectorROIs(self, roi):
        '''
        Set the detector region of interest
        '''
        self.detectorROI = roi

    def signalCancelLoadSource(self):
        '''
        Set a flag to cancel a loadSource while looping through scans
        '''
        self.cancelLoad = True
        
