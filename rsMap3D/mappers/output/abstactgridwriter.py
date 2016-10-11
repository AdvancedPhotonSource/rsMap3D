'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
import abc
import inspect

class AbstractGridWriter(object):
    __metaclass__ = abc.ABCMeta
    '''
    This class is an abstract class to handle the output(writting) format 
    of RSM data:
    '''
    
    def __init__(self):
        self.qx = None
        self.qy = None
        self.qz = None
        self.gridData = None
    
    def setData(self,qx, qy, qz, gridData ):
        self.qx = qx
        self.qy = qy
        self.qz = qz
        self.gridData = gridData
        self.fileInfo = []
        
    @abc.abstractmethod
    def setFileInfo(self, fileInfo):
        """Set information necessary for creating filenames for
        output files that will be created
        :param fileInfo A tuple describing how filenames will be
        generated
        """
        return
        
    @abc.abstractmethod
    def write(self):
        """ Write the output data.  It is necessary to set the data 
        and set the output file info before riting the files"""
        return
        
        
    def whatFunction(self):
        return inspect.stack()[1][3]