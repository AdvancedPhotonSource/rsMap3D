'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''

import xrayutilities as xu
from rsMap3D.mappers.abstractmapper import AbstractGridMapper
import numpy as np
from rsMap3D.config.rsmap3dconfig import RSMap3DConfig


class QGridMapper(AbstractGridMapper):
    '''
    This map provides an x, y, z grid of the data.
    '''
    def processMap(self, **kwargs):
        """
        read ad frames and grid them in reciprocal space
        angular coordinates are taken from the spec file
    
        **kwargs are passed to the rawmap function
        """
        rsMap3DConfig = RSMap3DConfig()
        maxImageMem = rsMap3DConfig.getMaxImageMemory()
        gridder = xu.Gridder3D(self.nx, self.ny, self.nz)
        gridder.KeepData(True)
        rangeBounds = self.dataSource.getRangeBounds()
        try:
            # xrayutilities 1.0.6 and below
            gridder.dataRange((rangeBounds[0], rangeBounds[1]), 
                              (rangeBounds[2], rangeBounds[3]), 
                              (rangeBounds[4], rangeBounds[5]), 
                              True)
        except:
            # repository version or xrayutilities > 1.0.6
            gridder.dataRange(rangeBounds[0], rangeBounds[1], 
                              rangeBounds[2], rangeBounds[3], 
                              rangeBounds[4], rangeBounds[5], 
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
                    if self.progressUpdater <> None:
                        self.progressUpdater(progress)
                else:
                    nPasses = imageSize*4*numImages/ maxImageMem + 1
                    
                    for thisPass in range(nPasses):
                        imageToBeUsedInPass = np.array(imageToBeUsed[scan])
                        imageToBeUsedInPass[:thisPass*numImages/nPasses] = False
                        imageToBeUsedInPass[(thisPass+1)*numImages/nPasses:] = False
                        
                        kwargs['mask'] = imageToBeUsedInPass
                        qx, qy, qz, intensity = \
                            self.dataSource.rawmap((scan,), **kwargs)
                        # convert data to rectangular grid in reciprocal space
                        gridder(qx, qy, qz, intensity)
                    
                        progress += 1.0/nPasses* 100.0
                        if self.progressUpdater <> None:
                            self.progressUpdater(progress)
            
        return gridder.xaxis,gridder.yaxis,gridder.zaxis,gridder.data,gridder
