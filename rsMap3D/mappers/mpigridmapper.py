'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''

import time
from xml.dom.expatbuilder import InternalSubsetExtractor
import xrayutilities as xu
from rsMap3D.mappers.abstractmapper import AbstractGridMapper
import numpy as np
from xrayutilities.exception import InputError
import logging
from mpi4py import MPI
logger = logging.getLogger(__name__)
from datetime import datetime
import sys
import pickle
import math

SCAN_WIN_SIZE = 4


class MPIQGridMapper(AbstractGridMapper):
    '''
    Override parent class to add in output type
    '''
    def __init__(self, dataSource, \
                 outputFileName, \
                 outputType, \
                 mpiComm, \
                 nx=200, ny=201, nz=202, \
                 transform = None, \
                 gridWriter = None, 
                 **kwargs):
        super(MPIQGridMapper, self).__init__(dataSource, \
                 outputFileName, \
                 nx=nx, ny=ny, nz=nz, \
                 transform = transform, \
                 gridWriter = gridWriter, \
                 **kwargs)
        self.outputType = outputType
        self.mpiComm = mpiComm
        self.mpiRank = mpiComm.Get_rank()
        
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
        

        scans = self.dataSource.getAvailableScans()

        if self.mpiRank == 0:
            scanWinSize = SCAN_WIN_SIZE
        else:
            scanWinSize = 0
        
        scanWin = MPI.Win.Allocate(scanWinSize, comm=self.mpiComm)

        scanIdx = self.mpiRank
        if self.mpiRank == 0:
            scanWin.Lock(rank=0)
            scanWin.Put([self.mpiComm.size.to_bytes(SCAN_WIN_SIZE, 'little'), MPI.BYTE], target_rank=0)
            scanWin.Unlock(rank=0)
        
        self.mpiComm.Barrier()

        while scanIdx < len(scans):
            scan = scans[scanIdx]

            if True in imageToBeUsed[scan]:
                imageSize = self.dataSource.getDetectorDimensions()[0] * \
                            self.dataSource.getDetectorDimensions()[1]
                numImages = len(imageToBeUsed[scan])
                if imageSize*4*numImages <= maxImageMem:
                    kwargs['mask'] = imageToBeUsed[scan]
                    qx, qy, qz, intensity = self.dataSource.rawmap((scan,), **kwargs)

                    try:
                        
                        gridder(qx, qy, qz, intensity)
                
                    except InputError as ex:
                        print ("Wrong Input to gridder")
                        print ("qx Size: " + str( qx.shape))
                        print ("qy Size: " + str( qy.shape))
                        print ("qz Size: " + str( qz.shape))
                        print ("intensity Size: " + str(intensity.shape))
                        raise InputError(ex)

                    
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
                        
                            except InputError as ex:
                                print ("Wrong Input to gridder")
                                print ("qx Size: " + str( qx.shape))
                                print ("qy Size: " + str( qy.shape))
                                print ("qz Size: " + str( qz.shape))
                                print ("intensity Size: " + str(intensity.shape))
                                raise InputError(ex)
                        
            scanBuff = bytearray(SCAN_WIN_SIZE)
            scanWin.Lock(rank=0)
            scanWin.Get([scanBuff, MPI.BYTE], target_rank=0)
            scanIdx = int.from_bytes(scanBuff, 'little')
            if scanIdx < len(scans):
                print(f'Proc {self.mpiRank} Gridding {scanIdx+1}/{len(scans)}')
            else:
                print(f'Proc {self.mpiRank} finished grid. Beginning merge.')

            scanNext = scanIdx + 1
            scanWin.Put([scanNext.to_bytes(SCAN_WIN_SIZE, 'little'), MPI.BYTE], target_rank=0)
            scanWin.Unlock(rank=0)




        gridder = self.mergeGridders(gridder)
        self.mpiComm.Barrier()
        
        return gridder.xaxis,gridder.yaxis,gridder.zaxis,gridder.data,gridder
    

    def mergeGridders(self, gridder):
        """
        Merges gridders, combining their grids till all data is collated at proc 0. 
        Similar to the upward execution of a distributed merge-sort. 
        """
        worldSize = self.mpiComm.Get_size()

        depth = math.floor(np.log2(worldSize)) + 1
        for currDepth in range(depth):

            # Exclude procs that have merged
            if self.mpiRank % (2**currDepth) != 0:
                break

            # Determine if sending or receiving
            if (self.mpiRank / (2**currDepth)) % 2 == 0:
                source = self.mpiRank + (2**currDepth)

                # Odd # world size
                if source >= worldSize:
                    continue

                incomingGrid = self.mpiComm.recv(source=source)
                # Normalization must be OFF and range must be FIXED for this to work
                # These are the defaults as of the current version of xu (1.7.3)
                gridder._gdata += incomingGrid._gdata
                gridder._gnorm += incomingGrid._gnorm
            
            else:
                dest = self.mpiRank - (2 ** currDepth)
                self.mpiComm.send(gridder, dest=dest)
        return gridder


    def doMap(self):
        '''
        Produce a q map of the data.  This is the method typically called to 
        run the mapper.  This method calls the processMap method which is an 
        abstract method which needs to be defined in subclasses.
        '''
        
        # read and grid data with helper function
        _start_time = time.time()
        #rangeBounds = self.dataSource.getRangeBounds()
        qx, qy, qz, gint, gridder = \
            self.processMap()
        print ('Elapsed time for gridding: %.3f seconds' % \
               (time.time() - _start_time))
        
        if self.mpiRank == 0:
            # print some information
            print ('qx: ', qx.min(), ' .... ', qx.max())
            print ('qy: ', qy.min(), ' .... ', qy.max())
            print ('qz: ', qz.min(), ' .... ', qz.max())
            self.gridWriter.setData(qx, qy, qz, gint)
            self.gridWriter.setFileInfo(self.getFileInfo())
            self.gridWriter.write()