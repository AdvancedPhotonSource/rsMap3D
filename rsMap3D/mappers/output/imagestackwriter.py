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

STACK_OUTFILE_MERGE_STR = "%s_S%d.vti"

def exportTiffStack(self, qx, qy, qz, intensity, dim=2, filebase="slice"):
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
    
    def setFileInfo(self, fileInfo):
        self.fileInfo.append(fileInfo[0])
        self.fileInfo.append(fileInfo[1])
        self.nx = fileInfo[2]
        self.ny = fileInfo[3]
        self.nz = fileInfo[4]
        self.outputFileName = fileInfo[5]
    
    def write(self):
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
            datadir, filename = os.path.split(self.outputfile)
            filePrefix = os.path.splitext(filename)[0]
            
        exportTiffStack(qxOut, qyOut, qzOut, arrayData, dim=2,\
                        filebase=os.path.join(datadir, filePrefix, filePrefix))
            
            
        
        
        