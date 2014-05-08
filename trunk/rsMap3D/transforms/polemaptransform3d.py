'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import numpy as np
from rsMap3D.transforms.abstracttransform3d import AbstractTransform3D
from rsMap3D.exception.rsmap3dexception import Transform3DException

POS_Z_DIRECTION = [0, 0, 1]
NEG_Z_DIRECTION = [0, 0, -1]

class PoleMapTransform3D(AbstractTransform3D):
    '''
    Transform axes for sterographic projection.
    '''
    def __init__(self, projectionDirection=POS_Z_DIRECTION):
        self.projectionDirection = projectionDirection
    
    def do3DTransform(self, axis1Data, axis2Data, axis3Data):
        
        if self.projectionDirection == POS_Z_DIRECTION:
            axis3DataOut = np.sqrt(axis1Data**2 + axis2Data**2 + axis3Data**2)
            axis1DataOut = axis1Data/(axis3DataOut + axis3Data)
            axis2DataOut = axis2Data/(axis3DataOut + axis3Data)
        elif self.projectionDirection == NEG_Z_DIRECTION:
            axis3DataOut = np.sqrt(axis1Data**2 + axis2Data**2 + axis3Data**2)
            axis1DataOut = axis1Data/(axis3DataOut + np.absolute(axis3Data))
            axis2DataOut = axis2Data/(axis3DataOut + np.absolute(axis3Data))
        else:
            raise Transform3DException("Projection direction can be only " +\
                                       "[0,0,1] or [0,0,-1]")    
        return axis1DataOut, axis2DataOut, axis3DataOut