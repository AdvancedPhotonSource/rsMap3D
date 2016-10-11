'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.mappers.output.abstactgridwriter import AbstractGridWriter
import numpy as np
from vtk.util import numpy_support
import vtk
VTI_WRITER_MERGE_STR = "%s_S%d.vti"

class VTIGridWriter(AbstractGridWriter):
    FILE_EXTENSION = ".vti"
    def setFileInfo(self, fileInfo):
        """
        Set information needed to create the file output.  
        This information is ultimately packed into a tuple
        or list which is used to define a number of parameters.
        [projectName, availableScans, nx, ny, nz (number of points in the 3 dimensions) 
        and the output file name
        """
        if ((fileInfo == None) or (len(fileInfo) == 0)):
            raise ValueError(self.whatFunction() +
                            "passed no filename information " +
                            "requires a tuple with six members:\n"
                            "1. project filename so that a filename can be " +
                            "constructed if filename is blank\n 2. User " +
                            "filename, and number of pixels for output in " + 
                            "x/y/z directions and output file name")
        elif (len( fileInfo) != 6):
            raise ValueError(self.whatFunction() +
                            "passed no filename information " +
                            "requires a tuple with six members:\n"
                            "1. project filename so that a filename can be " +
                            "constructed if filename is blank\n 2. User " +
                            "filename, and number of pixels for output in " + 
                            "x/y/z directions and outputFileName")
        self.fileInfo.append(fileInfo[0])
        self.fileInfo.append(fileInfo[1])
        self.nx = fileInfo[2]
        self.ny = fileInfo[3]
        self.nz = fileInfo[4]
        self.outputFileName = fileInfo[5]
        
        
        
    def write(self):
        qx0 = self.qx.min()
        dqx = (self.qx.max()-qx0)/self.nx
        qy0 = self.qy.min()
        dqy = (self.qx.max()-qy0)/self.ny
        qz0 = self.qz.min()
        dqz = (self.qz.max()-qz0)/self.nz
        
        da = np.transpose(self.gridData).reshape(self.gridData.size)
        data_array = numpy_support.numpy_to_vtk(da)
        
        image_data = vtk.vtkImageData()
        image_data.SetOrigin(qx0,qy0, qz0)
        image_data.SetSpacing(dqx, dqy, dqz)
        print self.nx, self.ny,self.nx
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

