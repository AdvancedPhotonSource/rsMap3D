'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import abc

class AbstractTransform3D():
    '''
    '''
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def do3DTransform(self, axis1Data, axis2Data, axis3Data):
        print ("Using AbstractTransform3D.doTransform3D")