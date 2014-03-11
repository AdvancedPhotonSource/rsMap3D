'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''

import numpy as np
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QComboBox

from vtk.util import numpy_support
import vtk

import rsMap3D.xrayutilities_33bmc_functions as bm
import xrayutilities as xu

class ProcessScans(QDialog):
    '''
    '''
    POLE_MAP_STR = "Pole Map"
    GRID_MAP_STR = "Grid Map"
    
    def __init__(self, parent=None):
        '''
        '''
        super(ProcessScans, self).__init__(parent)
        layout = QGridLayout()
        label = QLabel("Output Type")        
        layout.addWidget(label, 0, 0)
        self.outTypeChooser = QComboBox()
        self.outTypeChooser.addItem(self.GRID_MAP_STR)
        self.outTypeChooser.addItem(self.POLE_MAP_STR)
        layout.addWidget(self.outTypeChooser, 0,1)
        runButton = QPushButton("Run")
        layout.addWidget(runButton, 2,3)
        self.setLayout(layout)                    
        self.connect(runButton, SIGNAL("clicked()"), self.process)
        
        
    def process(self):
        self.emit(SIGNAL("process"))
        
    def runMapper(self, dataSource):
        '''
        '''
        self.dataSource = dataSource
        print "Selected " + str(self.outTypeChooser.currentText())
        if (self.outTypeChooser.currentText() == self.GRID_MAP_STR):
            self.doGridMap()
        else:
            self.doPoleMap()
            
    def doGridMap(self):
        '''
        '''
        print "Doing Grid Map"
        # number of points to be used during the gridding
        nx, ny, nz = 200, 201, 202
        
        # read and grid data with helper function
        _start_time = time.time()
        rangeBounds = self.dataSource.getRangeBounds()
        qx, qy, qz, gint, gridder = \
            bm.gridmap(self.dataSource.specFile, \
                       self.dataSource.getAvailableScans(), \
                       self.dataSource.getImageToBeUsed(), \
                       self.dataSource.imageFileTmp, \
                       nx, ny, nz, \
                       xmin=rangeBounds[0], xmax=rangeBounds[1], \
                       ymin=rangeBounds[2], ymax=rangeBounds[3], \
                       zmin=rangeBounds[4], zmax=rangeBounds[5], \
                       en=15200.0)
        print 'Elapsed time for gridding: %.3f seconds' % \
               (time.time() - _start_time)
        
        # print some information
        print 'qx: ', qx.min(), ' .... ', qx.max()
        print 'qy: ', qy.min(), ' .... ', qy.max()
        print 'qz: ', qz.min(), ' .... ', qz.max()
        
        # prepare data for export to VTK image file
        INT = xu.maplog(gint, 5.0, 0)
        
        qx0 = qx.min()
        dqx  = (qx.max()-qx.min())/nx
        
        qy0 = qy.min()
        dqy  = (qy.max()-qy.min())/ny
        
        qz0 = qz.min()
        dqz = (qz.max()-qz.min())/nz
        
        INT = np.transpose(INT).reshape((INT.size))
        data_array = numpy_support.numpy_to_vtk(INT)
        
        image_data = vtk.vtkImageData()
        image_data.SetNumberOfScalarComponents(1)
        image_data.SetOrigin(qx0,qy0,qz0)
        image_data.SetSpacing(dqx,dqy,dqz)
        image_data.SetExtent(0,nx-1,0,ny-1,0,nz-1)
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
        
        
    def doPoleMap(self):
        '''
        '''
        print "Doing Pole Map"
        # number of points to be used during the gridding
        nx, ny, nz = 200, 201, 202
        
        # read and grid data with helper function
        _start_time = time.time()
        rangeBounds = self.dataSource.getRangeBounds()
        qx, qy, qz, gint, gridder = \
            bm.polemap(self.dataSource.specFile, \
                       self.dataSource.getAvailableScans(), \
                       self.dataSource.getImageToBeUsed(), \
                       self.dataSource.getImageFileTmp, \
                       nx, ny, nz, \
                       xmin=rangeBounds[0], xmax=rangeBounds[1], \
                       ymin=rangeBounds[2], ymax=rangeBounds[3], \
                       zmin=rangeBounds[4], zmax=rangeBounds[5], \
                       en=15200.0)
        print 'Elapsed time for gridding: %.3f seconds' % \
               (time.time() - _start_time)
        
        # print some information
        print 'qx: ', qx.min(), ' .... ', qx.max()
        print 'qy: ', qy.min(), ' .... ', qy.max()
        print 'qz: ', qz.min(), ' .... ', qz.max()
        
        # prepare data for export to VTK image file
        INT = xu.maplog(gint, 5.0, 0)
        
        qx0 = qx.min()
        dqx  = (qx.max()-qx.min())/nx
        
        qy0 = qy.min()
        dqy  = (qy.max()-qy.min())/ny
        
        qz0 = qz.min()
        dqz = (qz.max()-qz.min())/nz
        
        INT = np.transpose(INT).reshape((INT.size))
        data_array = numpy_support.numpy_to_vtk(INT)
        
        image_data = vtk.vtkImageData()
        image_data.SetNumberOfScalarComponents(1)
        image_data.SetOrigin(qx0,qy0,qz0)
        image_data.SetSpacing(dqx,dqy,dqz)
        image_data.SetExtent(0,nx-1,0,ny-1,0,nz-1)
        image_data.SetScalarTypeToDouble()
        
        pd = image_data.GetPointData()
        
        pd.SetScalars(data_array)
        #pd.GetScalars().SetName("scattering data")
        
        # export data to file
        writer= vtk.vtkXMLImageDataWriter()
        writer.SetFileName("%s_S%d.vti" % (self.dataSource.projectName, 
                                           self.dataSource.availableScans[0]))
        writer.SetInput(image_data)
        writer.Write()
        
 
