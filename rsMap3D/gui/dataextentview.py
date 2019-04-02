'''
 Copyright (c) 2014, 2017 UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets
import sys


from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
from rsMap3D.gui.rsm3dcommonstrings import XMIN_INDEX, XMAX_INDEX, YMAX_INDEX,\
    YMIN_INDEX, ZMIN_INDEX, ZMAX_INDEX

class DataExtentView(qtWidgets.QFrame):
    '''
    This class will hold a vtk widget to show the extent of data.  This extent
    will be shown as a series of boxes, one for each image.  Each box will 
    extend to xmin, xmax, ymin, ymax zmin, zmax.  Depending on the transform 
    used, this may represent q's, hkl, etc. 
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(DataExtentView,self).__init__(parent)
        self.layout = qtWidgets.QVBoxLayout()
         
        self.vtkMain = QVTKRenderWindowInteractor()
        #self.layout.addWidget(self.vtkMain)

        self.ren = vtk.vtkRenderer()
        self.vtkMain.GetRenderWindow().AddRenderer(self.ren)
        self.setLayout(self.layout)
        
        self.renWin = self.vtkMain.GetRenderWindow()


        self.vtkMain.show()
        
        self.vtkMain.Start()
        self.setGeometry(qtCore.QRect(0, 0, 400, 400)) 
        self.vtkMain.setGeometry(qtCore.QRect(0, 0, 400, 400)) 
        self.renWin.GetInteractor().Initialize()
        self.renWin.Render()
        
    @qtCore.pyqtSlot()
    def clearRenderWindow(self):
        '''
        Delete all previous objects that were displayed.
        '''
        self.vtkMain.show()
        self.ren.RemoveAllViewProps()
       
    def getFrame(self):
        '''
        return the frame holding the vtk window
        '''
        return self.vtkMain

    @qtCore.pyqtSlot(object)
    def renderBounds(self, bounds):
        '''
        Render a box with boundaries from the given input
        :param bounds: Tuple holding max/min axes values
        '''
        cube = vtk.vtkOutlineSource()
        cube.SetBounds(bounds)
        cube.Update()
        cubeMapper = vtk.vtkPolyDataMapper()
        cubeMapper.SetInputConnection(cube.GetOutputPort())
        cubeActor = vtk.vtkActor()
        cubeActor.SetMapper(cubeMapper)
        cubeActor.GetProperty().SetColor(0.6,0,0)
        self.ren.AddActor(cubeActor)
        return cube
    
    
    @qtCore.pyqtSlot(object)
    def showRangeBounds(self, rangeBounds):
        '''
        Display axes showing the range boundaries
        :params rangeBounds: min/max values for the axes to be shown.
        '''
        axes = vtk.vtkCubeAxesActor()
        #rangeBounds = self.dataSource.getRangeBounds()
        
        axes.SetBounds((rangeBounds[XMIN_INDEX], rangeBounds[XMAX_INDEX], \
                        rangeBounds[YMIN_INDEX], rangeBounds[YMAX_INDEX], \
                        rangeBounds[ZMIN_INDEX], rangeBounds[ZMAX_INDEX]))
        axes.SetCamera(self.ren.GetActiveCamera())
        self.ren.AddActor(axes)
        self.ren.ResetCamera()
        self.renWin.Render()

    def testRender(self):
        '''
        A small bit of test code.
        '''
        # Create source
        source = vtk.vtkSphereSource()
        source.SetCenter(0, 0, 0)
        source.SetRadius(5.0)
 
        # Create a mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(source.GetOutputPort())
 
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
 
        self.ren.AddActor(actor)
 
        self.ren.ResetCamera()
 

    
class mainClass(qtWidgets.QMainWindow):
    '''
    A small class for testing via the main method
    '''
    def __init__(self, parent=None):
        super(mainClass,self).__init__(parent)
        dataView = DataExtentView()
        dataView.testRender()
        self.setCentralWidget(dataView)
        self.show()
        
if __name__ == "__main__":
    '''
    Main method for small scale testing.
    '''
 
    app = qtWidgets.QApplication(sys.argv)
 
    window = mainClass()
 
    sys.exit(app.exec_())

