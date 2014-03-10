'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import abc

class AbstractXrayutilitiesDataSource:
    __metaclass__ = abc.ABCMeta
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        self.sampleCirclesDirections = None
        self.detectorCircleDirections = None
        self.primaryBeamDirection = None
        self.incidentWavelength = float('nan')
        self.incidentEnergy = float('nan')
        self.sampleInplaneReferenceDirection = None
        self.sampleSurfaceNormalDirection = None
        self.detectorCenterChannel = None
        self.detectorDimensions = None
        self.distanceToDetector = float('nan')
        self.detectorPixelWidth = None
        self.detectorChannelPerDegree = None
        self.numPixelsToAverage = None
        self.detectorROI = None
        self.detectorAngles = None
        self.sampleAngles = None
        self.detectorPixelDirection1 = None
        self.detectorPixelDirection2 = None
        
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
    
    def getIncidentEnergy(self):
        """ """
        return self.incidentEnergy
    
    def getSampleInplaneReferenceDirection(self):
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
    
    
    @abc.abstractmethod
    def getSampleAngles(self, index1=0, index2=0):
        """ """
        return None
    
    @abc.abstractmethod
    def getImage(self, index1=0, index2=0):
        """ """
        return None
        
