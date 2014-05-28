'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.transforms.abstracttransform3d import AbstractTransform3D

class UnityTransform3D(AbstractTransform3D):
    '''
    Performs transform that leaves all axes unchanged,
    '''

    def do3DTransform(self, axis1Data, axis2Data, axis3Data):
        '''Perform the actual transform of the data.  Note that in this parent 
        class this method is abstract
        :param axis1Data:  data from axis 1 to be transformed
        :param axis2Data:  data from axis 2 to be transformed
        :param axis3Data:  data from axis 3 to be transformed
        :return: Transformed axes: x -> x, y -> y and z -> x
        '''
        axis1DataOut = axis1Data
        axis2DataOut = axis2Data
        axis3DataOut = axis3Data
        
        return axis1DataOut, axis2DataOut, axis3DataOut