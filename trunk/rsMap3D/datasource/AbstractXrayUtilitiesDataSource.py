'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import abc
from rsMap3D.transforms.unitytransform3d import UnityTransform3D

class AbstractXrayutilitiesDataSource:
    __metaclass__ = abc.ABCMeta
    '''
    classdocs
    '''

    def __init__(self, transform=None, 
                 scanList=None, 
                 roi=None, 
                 pixelsToAverage=None):
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
        print transform
        if transform == None:
            self.transform = UnityTransform3D()
        else:
            self.transform = transform
        
    def getSampleCircleDirections(self):
        """ """
        return self.sampleCirclesDirections
    
    def getDetectorCircleDirections(self):
        """ """
        return self.detectorCircleDirections
    
    def getPrimaryBeamDirection(self):
        """ """
        return self.primaryBeamDirection
    
    def getIncidentWavelength(self):
        """ """
        return self.incidentWavelength
    
    def getIncidentEnergy(self, index1=0, index2=0):
        """ """
        return self.incidentEnergy
    
    def getInplaneReferenceDirection(self):
        """ """
        return self.sampleInplaneReferenceDirection
    
    def getSampleSurfaceNormalDirection(self):
        """ """
        return self.sampleSurfaceNormalDirection
    
    def getDetectorCenterChannel(self):
        """ """
        return self.detectorCenterChannel
    
    def getDetectorDimensions(self):
        """ """
        return self.detectorDimensions
    
    def getDistanceToDetector(self):
        """ """
        return self.distanceToDetector
    
    def getDetectorPixelWidth(self):
        """ """
        return self.detectorPixelWidth
    
    def getDetectorChannelsPerDegree(self):
        """ """
        return self.detectorChannelPerDegree
    
    def getNumPixelsToAverage(self):
        """ """
        return self.numPixelsToAverage
    
    def getDetectorPixelDirection1(self):
        return self.detectorPixelDirection1
    
    def getDetectorPixelDirection2(self):
        return self.detectorPixelDirection2
    
    
    
    def getDetectorROI(self):
        """ """
        return self.detectorROI
    
    @abc.abstractmethod
    def getDetectorAngles(self, index1=0, index2=0):
        """ """
        return None

    def getDetectorAngleNames(self):
        return self.detectorAngleNames
    
    @abc.abstractmethod
    def getSampleAngles(self, index1=0, index2=0):
        """ """
        return None
    
    def getSampleAngleNames(self):
        return self.detectorAngleNames
    
    @abc.abstractmethod
    def getImage(self, index1=0, index2=0):
        """ """
        return None
    
    def setTransform(self, transform):
        self.transform = transform
        
    def setDetectorROIs(self, roi):
        self.detectorROI = roi
        
