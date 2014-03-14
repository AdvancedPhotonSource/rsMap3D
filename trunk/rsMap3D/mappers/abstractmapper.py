'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import abc

class AbstractGridMapper(object):
    __metaclass__ = abc.ABCMeta
    '''
    classdocs
    '''


    def __init__(self, dataSource, nx=200, ny=201, nz=202):
        '''
        Constructor
        '''
        self.dataSource = dataSource
        self.nx = nx
        self.ny = ny
        self.nz = nz


    @abc.abstractmethod
    def doMap(self):
        print "Accessing abstract method"
        
    def setGridSize(self, nx, ny, nz):
        self.nx = nx
        self.ny = ny
        self.nz = nz        