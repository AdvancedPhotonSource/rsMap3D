'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.mappers.output.abstactgridwriter import AbstractGridWriter
import numpy as np
import os
try:
    from PIL import Image
except ImportError:
    import Image

STACK_OUTFILE_MERGE_STR = "%s_S%d"

def exportTiffStack(qx, qy, qz, intensity, dim=2, filebase="slice"):
    print (qx.shape)
    print (qy.shape)
    print (qz.shape)
    print (intensity.shape)
    print (filebase)
    if dim==0:
        for ind, val in enumerate(qx):
            im = Image.fromarray(np.squeeze(intensity[ind,:,:]))
            filename = "%s_x%.3f.tif" % (filebase, val)
            im.save(filename)
    if dim==1:
        for ind, val in enumerate(qx):
            im = Image.fromarray(np.squeeze(intensity[:,ind,:]))
            filename = "%s_y%.3f.tif" % (filebase, val)
            im.save(filename)
    if dim==2:
        for ind, val in enumerate(qz):
            im = Image.fromarray(np.squeeze(intensity[:,:,ind]))
            filename = "%s_z%.3f.tif" % (filebase, val)
            im.save(filename)



class ImageStackWriter(AbstractGridWriter):
    FILE_EXTENSION = ""

    def __init__(self):
        super(ImageStackWriter, self).__init__()
        self.index = 0
        
    def getSliceIndex(self):
        return self.index
    
    def setFileInfo(self, fileInfo):
        self.fileInfo.append(fileInfo[0])
        self.fileInfo.append(fileInfo[1])
        self.nx = fileInfo[2]
        self.ny = fileInfo[3]
        self.nz = fileInfo[4]
        self.outputFileName = fileInfo[5]
    
    def setSliceIndex(self, index):
        self.index = index
        
    def write(self):
        print ("Entering ImageStackWriter.write ")
        print (self.qx.shape)
        print (self.qy.shape)
        print (self.qz.shape)
        dimX = (self.qx[-1] - self.qx[0])/self.nx
        qxOut = np.linspace(self.qx[0], self.qx[0]+dimX*self.nx, dimX )
        dimY = (self.qy[-1] - self.qy[0])/self.ny
        qyOut = np.linspace(self.qy[0], self.qy[0]+dimY*self.ny, dimY )
        dimZ = (self.qz[-1] - self.qz[0])/self.nz
        qzOut = np.linspace(self.qz[0], self.qz[0]+dimZ*self.nz, dimZ )   
        dims = (self.nx, self.ny, self.nz)
        arrayData = np.reshape(self.gridData, dims[::-1])
        
        arrayData = np.transpose(arrayData)
        datadir = ""
        filePrefix = ""
        if self.outputFileName == "":
            filePrefix = (STACK_OUTFILE_MERGE_STR % 
                               (self.fileInfo[0], \
                                self.fileInfo[1]))
        else:
            datadir, filename = os.path.split(self.outputFileName)
            filePrefix = os.path.splitext(filename)[0]
            
        exportTiffStack(self.qx, self.qy, self.qz, arrayData, \
                        dim=self.index,\
                        filebase=os.path.join(datadir, filePrefix))
        print ("Exiting ImageStackWriter.write")
            
            
        
        
        