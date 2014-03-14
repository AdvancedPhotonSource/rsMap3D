'''
Created on Mar 14, 2014

@author: hammonds
'''
import numpy as np
import time

from vtk.util import numpy_support
import vtk

import rsMap3D.xrayutilities_33bmc_functions as bm
import xrayutilities as xu
from rsMap3D.mappers.abstractmapper import AbstractGridMapper

class QGridMapper(AbstractGridMapper):
    '''
    '''
    
#    def __init__(self, dataSource, nx=200, ny=201, nz=202):
#        '''
#        '''
#        super(QGridMapper, self).__init__(self, \
#                                          dataSource, \
#                                          nx=nx, \
#                                          ny=ny, \
#                                          nz=nz)

    def doMap(self):
        '''
        Produce a q map of the data.
        '''
        print "Doing Grid Map"
        # number of points to be used during the gridding
        
        # read and grid data with helper function
        _start_time = time.time()
        rangeBounds = self.dataSource.getRangeBounds()
        qx, qy, qz, gint, gridder = \
            bm.gridmap(self.dataSource, \
                       self.nx, self.ny, self.nz, \
                       xmin=rangeBounds[0], xmax=rangeBounds[1], \
                       ymin=rangeBounds[2], ymax=rangeBounds[3], \
                       zmin=rangeBounds[4], zmax=rangeBounds[5])
        print 'Elapsed time for gridding: %.3f seconds' % \
               (time.time() - _start_time)
        
        # print some information
        print 'qx: ', qx.min(), ' .... ', qx.max()
        print 'qy: ', qy.min(), ' .... ', qy.max()
        print 'qz: ', qz.min(), ' .... ', qz.max()
        
        # prepare data for export to VTK image file
        INT = xu.maplog(gint, 5.0, 0)
        
        qx0 = qx.min()
        dqx  = (qx.max()-qx.min())/self.nx
        
        qy0 = qy.min()
        dqy  = (qy.max()-qy.min())/self.ny
        
        qz0 = qz.min()
        dqz = (qz.max()-qz.min())/self.nz
        
        INT = np.transpose(INT).reshape((INT.size))
        data_array = numpy_support.numpy_to_vtk(INT)
        
        image_data = vtk.vtkImageData()
        image_data.SetNumberOfScalarComponents(1)
        image_data.SetOrigin(qx0,qy0,qz0)
        image_data.SetSpacing(dqx,dqy,dqz)
        image_data.SetExtent(0, self.nx-1,0, self.ny-1,0, self.nz-1)
        image_data.SetScalarTypeToDouble()
        
        pd = image_data.GetPointData()
        
        pd.SetScalars(data_array)
        #pd.GetScalars().SetName("scattering data")
        
        # export data to file
        writer= vtk.vtkXMLImageDataWriter()
        writer.SetFileName("%s_S%d.vti" % (self.dataSource.projectName, \
                                           self.dataSource.availableScans[0]))
        writer.SetInput(image_data)
        writer.Write()
        
