'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
import sys


from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk

class DataExtentView(qtGui.QFrame):
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
        self.layout = qtGui.QVBoxLayout()
         
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

#    def render(self):
#        self.renWin.Render()
#        
    def renderBounds(self, bounds):
        '''
        Render a box with boundaries from the given input
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
    
    
    def showRangeBounds(self, rangeBounds):
        '''
        Display axes showing the range boundaries
        '''
        axes = vtk.vtkCubeAxesActor()
        #rangeBounds = self.dataSource.getRangeBounds()
        
        axes.SetBounds((rangeBounds[0], rangeBounds[1], \
                        rangeBounds[2], rangeBounds[3], \
                        rangeBounds[4], rangeBounds[5]))
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
 

    
class mainClass(qtGui.QMainWindow):
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
 
    app = qtGui.QApplication(sys.argv)
 
    window = mainClass()
 
    sys.exit(app.exec_())
