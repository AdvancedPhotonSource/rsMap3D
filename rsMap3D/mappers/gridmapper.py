'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''

import xrayutilities as xu
from rsMap3D.mappers.abstractmapper import AbstractGridMapper
import numpy as np
from xrayutilities.exception import InputError
import logging
logger = logging.getLogger(__name__)

class QGridMapper(AbstractGridMapper):
    '''
    Override parent class to add in output type
    '''
    def __init__(self, dataSource, \
                 outputFileName, \
                 outputType, \
                 nx=200, ny=201, nz=202, \
                 transform = None, \
                 gridWriter = None, **kwargs):
        super(QGridMapper, self).__init__(dataSource, \
                 outputFileName, \
                 nx=nx, ny=ny, nz=nz, \
                 transform = transform, \
                 gridWriter = gridWriter, \
                 **kwargs)
        self.outputType = outputType
        
    def getFileInfo(self):
        '''
        Override parent class to add in output type
        '''
        return (self.dataSource.projectName, 
                self.dataSource.availableScans[0],
                self.nx, self.ny, self.nz,
                self.outputFileName,
                self.outputType)
    
    '''
    This map provides an x, y, z grid of the data.
    '''
    #@profile
    def processMap(self, **kwargs):
        """
        read ad frames and grid them in reciprocal space
        angular coordinates are taken from the spec file
    
        **kwargs are passed to the rawmap function
        """
        maxImageMem = self.appConfig.getMaxImageMemory()
        gridder = xu.Gridder3D(self.nx, self.ny, self.nz)
        gridder.KeepData(True)
        rangeBounds = self.dataSource.getRangeBounds()
        try:
            # repository version or xrayutilities > 1.0.6
            gridder.dataRange(rangeBounds[0], rangeBounds[1], 
                              rangeBounds[2], rangeBounds[3], 
                              rangeBounds[4], rangeBounds[5], 
                              True)
        except:
            # xrayutilities 1.0.6 and below
            gridder.dataRange((rangeBounds[0], rangeBounds[1]), 
                              (rangeBounds[2], rangeBounds[3]), 
                              (rangeBounds[4], rangeBounds[5]), 
                              True)
                              
        imageToBeUsed = self.dataSource.getImageToBeUsed()
        progress = 0
        for scan in self.dataSource.getAvailableScans():

            if True in imageToBeUsed[scan]:
                imageSize = self.dataSource.getDetectorDimensions()[0] * \
                            self.dataSource.getDetectorDimensions()[1]
                numImages = len(imageToBeUsed[scan])
                if imageSize*4*numImages <= maxImageMem:
                    kwargs['mask'] = imageToBeUsed[scan]
                    qx, qy, qz, intensity = self.dataSource.rawmap((scan,), **kwargs)
                    
                    # convert data to rectangular grid in reciprocal space
                    gridder(qx, qy, qz, intensity)
                    progress += 100
                    if self.progressUpdater is not None:
                        self.progressUpdater(progress)
                else:
                    nPasses = int(imageSize*4*numImages/ maxImageMem + 1)
                    
                    for thisPass in range(nPasses):
                        imageToBeUsedInPass = np.array(imageToBeUsed[scan])
                        imageToBeUsedInPass[:int(thisPass*numImages/nPasses)] = False
                        imageToBeUsedInPass[int((thisPass+1)*numImages/nPasses):] = False
                        
                        if True in imageToBeUsedInPass:
                            kwargs['mask'] = imageToBeUsedInPass
                            qx, qy, qz, intensity = \
                                self.dataSource.rawmap((scan,), **kwargs)
                            # convert data to rectangular grid in reciprocal space
                            try:
                                gridder(qx, qy, qz, intensity)
                        
                                progress += 1.0/nPasses* 100.0
                                if self.progressUpdater is not None:
                                    self.progressUpdater(progress)
                            except InputError as ex:
                                print ("Wrong Input to gridder")
                                print ("qx Size: " + str( qx.shape))
                                print ("qy Size: " + str( qy.shape))
                                print ("qz Size: " + str( qz.shape))
                                print ("intensity Size: " + str(intensity.shape))
                                raise InputError(ex)
                        else:
                            progress += 1.0/nPasses* 100.0
                            if self.progressUpdater is not None:
                                self.progressUpdater(progress)
            self.progressUpdater(100.0)
        return gridder.xaxis,gridder.yaxis,gridder.zaxis,gridder.data,gridder
    
    
