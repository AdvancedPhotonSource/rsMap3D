'''
 Copyright (c) 2014, 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import abc
import numpy as np
from rsMap3D.gui.rsm3dcommonstrings import POSITIVE_INFINITY, \
    NEGATIVE_INFINITY, XMIN_INDEX, XMAX_INDEX, YMIN_INDEX, YMAX_INDEX, \
    ZMIN_INDEX, ZMAX_INDEX
import logging
from rsMap3D.exception.rsmap3dexception import RSMap3DException
logger = logging.getLogger(__name__)

class AbstractDataSource(object):
    __metaclass__ = abc.ABCMeta
    '''
    This is the base class for all data sources to be used with rsMap3D.  
    it provides some basic functionality for all data sour
    '''


    def __init__(self, appConfig=None):
        '''
        Constructor.  Initialize members needed for calls made by this class.
        '''
        self.appConfig = None
        if not (appConfig is None):
            self.appConfig = appConfig
        else:
            raise RSMap3DException("no AppConfig object received.")
        
        
        self.availableScans = []
        self.imageBounds = {}
        self.imageToBeUsed = {}
        self.availableScanTypes = []

        self.detectorDimensions = None
        self.rangeBounds = None
        
    def getAvailableScans(self):
        '''
        Return a list of the available scans. Note that loadSource checks to 
        make sure that scans are available in the directory structure
        '''
        return self.availableScans
    
    def getAvailableScanTypes(self):
        """
        Return the set of available scan types
        """
        return self.availableScanTypes
    
    def getDetectorDimensions(self):
        '''
        Return the dimensions (in pixels of the detector
        '''
        return self.detectorDimensions
    
    def getImageBounds(self, scan):
        '''
        return the boundaries for images in the scan
        '''
        return self.imageBounds[scan]    

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

    def getRangeBounds(self):
        '''
        Return boundaries of all scans to be included for analysis
        '''
        return self.rangeBounds
    
    @abc.abstractmethod
    def getReferenceNames(self):
        '''
        return a list of names that describe a set of 
        reference values to be used in display of scan extent
        '''
        logger.error("Using abstract method: getReferenceNames")
        return []
    
    @abc.abstractmethod
    def getReferenceValues(self):
        '''
        return a list of values to be used in display of scan extent
        '''
        logger.error("Using abstract method: getReferenceValues")
        return []
    
    def inBounds(self, xmin, xmax, ymin, ymax, zmin, zmax):
        '''
        Check to see if the input boundaries have area that lie within the 
        range boundaries specified for analysis.  True if yes, False if no.
        '''
               
        return (xmin <= self.rangeBounds[XMAX_INDEX] and \
                xmax >= self.rangeBounds[XMIN_INDEX]) and \
               (ymin <= self.rangeBounds[YMAX_INDEX] and \
                ymax >= self.rangeBounds[YMIN_INDEX]) and \
               (zmin <= self.rangeBounds[ZMAX_INDEX] and \
                zmax >= self.rangeBounds[ZMIN_INDEX])
               
    def processImageToBeUsed(self):
        '''
        process all available scans to see if the contained images fall within 
        the range boundaries.  Results are stored internally and can be 
        retrieved by getImageToBeUsed()
        '''
        self.imageToBeUsed = {}
        for scan in self.availableScans:
            inUse = []
            for i in range(len(self.imageBounds[scan][0])):
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
            
    def resetHaltMap(self):
        self.haltMap = False
    
    def setProgressUpdater(self, updater):
        '''
        set an updater that will affect a progress bar to indicate progress on
        loading.  Especially useful for slow loading
        ''' 
        self.progressUpdater = updater
 
    def setRangeBounds(self, rangeBounds):
        '''
        Set the overall boundary to be used for analysis.
        '''
        self.rangeBounds = rangeBounds;
        self.processImageToBeUsed()
        
    def stopMap(self):
        '''
        Set a flag that will be used to halt processing the scan using 
        '''
        self.haltMap = True
