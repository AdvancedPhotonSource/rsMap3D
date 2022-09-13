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

SCAN_WIN_SIZE = 4


class MPIQGridMapper(AbstractGridMapper):
    '''
    Override parent class to add in output type
    '''
    def __init__(self, dataSource, \
                 outputFileName, \
                 outputType, \
                 mpi_comm, \
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
        self.mpi_comm = mpi_comm
        self.mpi_rank = mpi_comm.Get_rank()
        
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
        progress = 0
        

        # Init gridder buffer on proc 0
        if self.mpi_rank == 0:
            gridder_pickle = pickle.dumps(gridder)
            win_size = round(len(gridder_pickle) * 1.5)
        else:
            win_size = 0

        gridderWin = MPI.Win.Allocate(win_size, comm=self.mpi_comm)

        if self.mpi_rank == 0:
            gridderWin.Lock(rank=0)
            gridderWin.Put([gridder_pickle, MPI.BYTE], target_rank=0)
            gridderWin.Unlock(rank=0)

        # Sync forced here
        gridder_buff_size = self.mpi_comm.bcast(win_size, root=0)


        scans = self.dataSource.getAvailableScans()

        if self.mpi_rank == 0:
            scanWinSize = SCAN_WIN_SIZE
        else:
            scanWinSize = 0
        
        scanWin = MPI.Win.Allocate(scanWinSize, comm=self.mpi_comm)

        scanIdx = self.mpi_rank
        if self.mpi_rank == 0:
            scanWin.Lock(rank=0)
            scanWin.Put([self.mpi_comm.size.to_bytes(SCAN_WIN_SIZE, 'little'), MPI.BYTE], target_rank=0)
            scanWin.Unlock(rank=0)
        
        self.mpi_comm.Barrier()

        while scanIdx < len(scans):
            print(f'Starting Scan {scanIdx} of {len(scans)}')
            scan = scans[scanIdx]

            if True in imageToBeUsed[scan]:
                imageSize = self.dataSource.getDetectorDimensions()[0] * \
                            self.dataSource.getDetectorDimensions()[1]
                numImages = len(imageToBeUsed[scan])
                if imageSize*4*numImages <= maxImageMem:
                    kwargs['mask'] = imageToBeUsed[scan]
                    print(f'R: {self.mpi_rank} Mapping {datetime.now():%M:%S}')
                    qx, qy, qz, intensity = self.dataSource.rawmap((scan,), **kwargs)

                    try:
                        
                        gridder_buff = bytearray(gridder_buff_size)
                        gridderWin.Lock(rank=0)
                        print(f'R: {self.mpi_rank} Acquired Gridder {datetime.now():%M:%S}')
                        gridderWin.Get([gridder_buff, MPI.BYTE], target_rank=0)
                        print(f'Gridder Loaded {datetime.now():%M:%S}')
                        gridder = pickle.loads(gridder_buff)
                        gridder(qx, qy, qz, intensity)
                        print(f'R: {self.mpi_rank} Gridding Complete {datetime.now():%M:%S}')
                        gridder_buff = pickle.dumps(gridder)
                        gridderWin.Put([gridder_buff, MPI.BYTE], target_rank=0)
                        print(f'Gridder Sent {datetime.now():%M:%S}')
                        print(f'R: {self.mpi_rank} Released Complete {datetime.now():%M:%S}\n\n')
                        gridderWin.Unlock(rank=0)
                
                    except InputError as ex:
                        print ("Wrong Input to gridder")
                        print ("qx Size: " + str( qx.shape))
                        print ("qy Size: " + str( qy.shape))
                        print ("qz Size: " + str( qz.shape))
                        print ("intensity Size: " + str(intensity.shape))
                        raise InputError(ex)

                    
                    progress += 100
                    if self.progressUpdater is not None:
                        self.progressUpdater(progress)
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
                                
                                gridder_buff = bytearray(gridder_buff_size)
                                gridderWin.Lock(rank=0)
                                print(f'R: {self.mpi_rank} Acquired Gridder {datetime.now():%M:%S}')
                                gridderWin.Get([gridder_buff, MPI.BYTE], target_rank=0)
                                print(f'Gridder Loaded {datetime.now():%M:%S}')
                                gridder = pickle.loads(gridder_buff)
                                gridder(qx, qy, qz, intensity)
                                print(f'R: {self.mpi_rank} Gridding Complete {datetime.now():%M:%S}')
                                gridder_buff = pickle.dumps(gridder)
                                gridderWin.Put([gridder_buff, MPI.BYTE], target_rank=0)
                                print(f'Gridder Sent {datetime.now():%M:%S}')
                                print(f'R: {self.mpi_rank} Released Complete {datetime.now():%M:%S}\n\n')
                                gridderWin.Unlock(rank=0)
                        
                                progress += 1.0/nPasses* 100.0
                                if self.progressUpdater is not None:
                                    self.progressUpdater(progress)
                            except InputError as ex:
                                print ("Wrong Input to gridder")
                                print ("qx Size: " + str( qx.shape))
                                print ("qy Size: " + str( qy.shape))
                                print ("qz Size: " + str( qz.shape))
                                print ("intensity Size: " + str(intensity.shape))
                                raise InputError(ex)
                        else:
                            progress += 1.0/nPasses* 100.0
                            if self.progressUpdater is not None:
                                self.progressUpdater(progress)
                        
            scanBuff = bytearray(SCAN_WIN_SIZE)
            scanWin.Lock(rank=0)
            scanWin.Get([scanBuff, MPI.BYTE], target_rank=0)
            scanIdx = int.from_bytes(scanBuff, 'little')
            print(f'Recieved Scan {scanIdx}')
            scanNext = scanIdx + 1
            scanWin.Put([scanNext.to_bytes(SCAN_WIN_SIZE, 'little'), MPI.BYTE], target_rank=0)
            scanWin.Unlock(rank=0)


            self.progressUpdater(100.0)

        self.mpi_comm.Barrier()

        if self.mpi_rank == 0:
            gridder_buff = bytearray(gridder_buff_size)
            gridderWin.Lock(rank=0)
            gridderWin.Get([gridder_buff, MPI.BYTE], target_rank=0)
            gridder = pickle.loads(gridder_buff)
            gridderWin.Unlock(rank=0)
        
        return gridder.xaxis,gridder.yaxis,gridder.zaxis,gridder.data,gridder
    
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
        
        if self.mpi_rank == 0:
            # print some information
            print ('qx: ', qx.min(), ' .... ', qx.max())
            print ('qy: ', qy.min(), ' .... ', qy.max())
            print ('qz: ', qz.min(), ' .... ', qz.max())
            self.gridWriter.setData(qx, qy, qz, gint)
            self.gridWriter.setFileInfo(self.getFileInfo())
            self.gridWriter.write()