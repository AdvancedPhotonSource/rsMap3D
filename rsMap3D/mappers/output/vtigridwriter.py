'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.mappers.output.abstactgridwriter import AbstractGridWriter
import numpy as np
from vtk.util import numpy_support
import vtk
from rsMap3D.gui.rsm3dcommonstrings import ASCII_OUTPUT
VTI_WRITER_MERGE_STR = "%s_S%d.vti"
import logging
logger = logging.getLogger(__name__)

class VTIGridWriter(AbstractGridWriter):
    
    def setFileInfo(self, fileInfo):
        """
        Set information needed to create the file output.  
        This information is ultimately packed into a tuple
        or list which is used to define a number of parameters.
        [projectName, availableScans, nx, ny, nz (number of points in the 3 dimensions) 
        and the output file name
        """
        if ((fileInfo is None) or (len(fileInfo) == 0)):
            raise ValueError(self.whatFunction() +
                            "passed no filename information " +
                            "requires a tuple with six members:\n"
                            "1. project filename so that a filename can be " +
                            "constructed if filename is blank\n 2. User " +
                            "filename\n" +
                            "3,4,5 - number of pixels for output in " + 
                            "x/y/z directions" +
                            "6 - output file name" + 
                            "7. outputFileType")
        elif (len( fileInfo) != 7):
            raise ValueError(self.whatFunction() +
                            "passed no filename information " +
                            "requires a tuple with six members:\n"
                            "1. project filename so that a filename can be " +
                            "constructed if filename is blank\n 2. User " +
                            "filename\n" +
                            "3,4,5 - number of pixels for output in " + 
                            "x/y/z directions" +
                            "6 - output file name" + 
                            "7. outputFileType")
        self.fileInfo.append(fileInfo[0])
        self.fileInfo.append(fileInfo[1])
        self.nx = fileInfo[2]
        self.ny = fileInfo[3]
        self.nz = fileInfo[4]
        self.outputFileName = fileInfo[5]
        self.outType = fileInfo[6]
        
        
        
    def write(self):
        qx0 = self.qx.min()
        dqx = (self.qx.max()-qx0)/self.nx
        qy0 = self.qy.min()
        dqy = (self.qy.max()-qy0)/self.ny
        qz0 = self.qz.min()
        dqz = (self.qz.max()-qz0)/self.nz
        
        logger.debug("self.gridData.shape: " + str(self.gridData.shape))
        da = np.transpose(self.gridData).reshape(self.gridData.size)
        logger.debug("da.shape: " + str(da.shape)) 
        data_array = numpy_support.numpy_to_vtk(da)
        logger.debug("self.gridData.shape: " + str(self.gridData.shape))
        
        image_data = vtk.vtkImageData()
        image_data.SetOrigin(qx0,qy0, qz0)
        image_data.SetSpacing(dqx, dqy, dqz)
        logger.debug ("Gridsize %d, %d, %d" % (self.nx, self.ny,self.nz))
        image_data.SetExtent(0, self.nx-1,\
                             0, self.ny-1,\
                             0, self.nz-1)
        if vtk.VTK_MAJOR_VERSION <= 5:
            image_data.SetNumberOfScalarComponents(1)
            image_data.SetScalarTypeToDouble()
        else:
            image_data.AllocateScalars(vtk.VTK_DOUBLE, 1)
               
        pd = image_data.GetPointData()
        
        pd.SetScalars(data_array)
        
        # Export data to file
        writer= vtk.vtkXMLImageDataWriter()
        if self.outType == ASCII_OUTPUT:
            writer.SetDataModeToAscii()
            
        if self.outputFileName == "":
            writer.SetFileName(VTI_WRITER_MERGE_STR % 
                               (self.fileInfo[0], \
                                self.fileInfo[1]))
        else:
            writer.SetFileName(self.outputFileName)
            
        if vtk.VTK_MAJOR_VERSION <= 5:
            writer.SetInput(image_data)
        else:
            writer.SetInputData(image_data)
            
        writer.Write()

