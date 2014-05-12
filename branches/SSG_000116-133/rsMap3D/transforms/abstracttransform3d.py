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
        '''Perform the actual transform of the data.  Note that in this parent 
        class this method is abstract
        :param axis1Data:  data from axis 1 to be transformed
        :param axis2Data:  data from axis 2 to be transformed
        :param axis3Data:  data from axis 3 to be transformed
        '''
        print ("Using AbstractTransform3D.doTransform3D")