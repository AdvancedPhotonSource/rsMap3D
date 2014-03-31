'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.transforms.abstracttransform3d import AbstractTransform3D

class UnityTransform3D(AbstractTransform3D):
    '''
    classdocs
    '''

    def do3DTransform(self, axis1Data, axis2Data, axis3Data):
        '''
        '''
        axis1DataOut = axis1Data
        axis2DataOut = axis2Data
        axis3DataOut = axis3Data
        
        return axis1DataOut, axis2DataOut, axis3DataOut