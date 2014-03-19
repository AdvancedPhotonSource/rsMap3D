'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import numpy as np
from rsMap3D.transforms.abstracttransform3d import AbstractTransform3D

class PoleMapTransform3D(AbstractTransform3D):
    '''
    classdocs
    '''


    def do3DTransform(self, axis1Data, axis2Data, axis3Data):
        '''
        '''
        axis3DataOut = np.sqrt(axis1Data**2 + axis2Data**2 + axis3Data**2)
        axis1DataOut = axis1Data/(axis3DataOut + axis3Data)
        axis2DataOut = axis2Data/(axis3DataOut + axis3Data)

        return axis1DataOut, axis2DataOut, axis3DataOut