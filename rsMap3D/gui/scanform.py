'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
from PyQt4.QtCore import *
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QVBoxLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QListWidget
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QTableWidget
from PyQt4.QtGui import QTableWidgetItem
from PyQt4.QtGui import QListWidgetItem
from PyQt4.QtGui import QBrush
from PyQt4.QtGui import QColor

from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util import numpy_support

import vtk


class ScanForm(QDialog):
    '''
    This class presents a form to display available scans, lists the angles 
    and q values for a selected scan and allows selecting of individual images 
    for exclusion/inclusion in the processing phase.  A window is also provided
    to visualize the q space covered by the included images in the selected
    scan.
    '''
    def __init__(self, parent=None):
        '''
        Constructor - Layout widgets on the form and set up a VTK window for 
        displaying the covered q space 
        '''
        super(ScanForm, self).__init__(parent)
        self.rangeBounds = (float("Infinity"), float("-Infinity"), \
                        float("Infinity"), float("-Infinity"), \
                        float("Infinity"), float("-Infinity"))
        layout = QGridLayout()
        self.scanList = QListWidget()
        layout.addWidget(self.scanList, 0, 0)
        layout.setColumnStretch(0, 10)
        
        rightBox = QVBoxLayout()
        qrange = QGridLayout()
        xLabel = QLabel("X")
        xminLabel = QLabel("min")
        self.xminText = QLineEdit()
        self.xminText.setReadOnly(True)
        xmaxLabel = QLabel("max")
        self.xmaxText = QLineEdit()
        self.xmaxText.setReadOnly(True)
        yLabel = QLabel("Y")
        yminLabel = QLabel("min")
        self.yminText = QLineEdit()
        self.yminText.setReadOnly(True)
        ymaxLabel = QLabel("max")
        self.ymaxText = QLineEdit()
        self.ymaxText.setReadOnly(True)
        zLabel = QLabel("Z")
        zminLabel = QLabel("min")
        self.zminText = QLineEdit()
        self.zminText.setReadOnly(True)
        zmaxLabel = QLabel("max")
        self.zmaxText = QLineEdit()
        self.zmaxText.setReadOnly(True)

        self.selectAll = QPushButton()
        self.selectAll.setText("Select All")
        self.selectAll.setDisabled(True)
        self.deselectAll = QPushButton()
        self.deselectAll.setText("Deselect All")
        self.deselectAll.setDisabled(True)
        self.connect(self.selectAll, SIGNAL("clicked()"), self.selectAllAction)
        self.connect(self.deselectAll, SIGNAL("clicked()"), 
                     self.deselectAllAction)
        
        qrange.addWidget(xLabel, 0,0)
        qrange.addWidget(xminLabel, 0,1)
        qrange.addWidget(self.xminText, 0,2)
        qrange.addWidget(xmaxLabel, 0,3)
        qrange.addWidget(self.xmaxText, 0,4)
        qrange.addWidget(yLabel, 1,0)
        qrange.addWidget(yminLabel, 1,1)
        qrange.addWidget(self.yminText, 1,2)
        qrange.addWidget(ymaxLabel, 1,3)
        qrange.addWidget(self.ymaxText, 1,4)
        qrange.addWidget(zLabel, 2,0)
        qrange.addWidget(zminLabel, 2,1)
        qrange.addWidget(self.zminText, 2,2)
        qrange.addWidget(zmaxLabel, 2,3)
        qrange.addWidget(self.zmaxText, 2,4)
        qrange.addWidget(self.selectAll, 3,0)
        qrange.addWidget(self.deselectAll, 3,1)
        
        rightBox.addLayout(qrange)
        self.detail = QTableWidget()
        rightBox.addWidget(self.detail)
        layout.addLayout(rightBox, 0,1)
        layout.setColumnStretch(1, 45)
        
        self.ren = vtk.vtkRenderer()

        self.vtkMain = QVTKRenderWindowInteractor()
        self.vtkMain.GetRenderWindow().AddRenderer(self.ren)
        self.renWin = self.vtkMain.GetRenderWindow()
        self.vtkMain.Initialize()
        self.renWin.Render()
        self.vtkMain.Start()
        self.vtkMain.show()
        
        self.connect(self.scanList, SIGNAL("itemClicked(QListWidgetItem *)"), 
                self.scanSelected)
         
        self.setLayout(layout);
        
    def addValueToTable(self, value, row, column, coloredBrush):
        '''
        Add a value to a cell in the table setting the value to display and 
        the foreground color
        '''
        item = QTableWidgetItem(str(value))
        item.setForeground(coloredBrush)
        self.detail.setItem(row, column, item)
        
    def checkItemChanged(self,item):
        '''
        Change whether a row is selected or not and register if the associated
        image will be used in analysis
        '''
        scanNo = self.getSelectedScan()
        row = item.row()
        if item.checkState() == Qt.Checked:
            self.dataSource.imageToBeUsed[scanNo][row] = True
        else:
            self.dataSource.imageToBeUsed[scanNo][row] = False
        self.showQs(scanNo)

    def deselectAllAction(self):
        '''
        Change setting for all images in the selected scan so that none of the
        images are used in analysis
        '''
        scanNo = self.getSelectedScan()
        for i in xrange(len(self.dataSource.imageToBeUsed[scanNo])):
            self.dataSource.imageToBeUsed[scanNo][i] = False
        self.showQs(scanNo)

    def loadScanFile(self, dataSource):
        '''
        Load information from the selected dataSource into this form.
        '''
        self.dataSource = dataSource
        self.scanList.clear()
        for curScan in self.dataSource.getAvailableScans():
            item = QListWidgetItem()
            item.setText(str(curScan))
            self.scanList.addItem(item)
        self.detail.setColumnCount(7 + \
                                   len(dataSource.getDetectorAngleNames()) + \
                                   len(dataSource.getSampleAngleNames()))
        self.detail.setHorizontalHeaderLabels(['Use Image'] + \
                                            dataSource.getSampleAngleNames() + \
                                            dataSource.getDetectorAngleNames() + \
                                            ['Min qx', 'Max qx', 'Min qy', \
                                            'Max qy', 'Min qz', 'Max qz'])
        self.emit(SIGNAL("doneLoading"))
        
   
    def getSelectedScan(self):
        '''
        Return the scan number of the selected scan
        '''
        scansSel = self.scanList.selectedItems()
        if len(scansSel) > 1:
            print "Should not be able to select more than one scan."
        scan = scansSel[0]
        scanNo = int(scan.text().split(' ')[0])
        return scanNo
        
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
        
    def renderOverallQs(self):
        '''
        Render bounds for all selected images from all available scans 
        '''
        self.ren.RemoveAllViewProps()
        imageToBeUsed = self.dataSource.getImageToBeUsed()
        for scan in self.dataSource.getAvailableScans():
            minx, maxx, miny, maxy, minz, maxz = \
                self.dataSource.getImageBounds(scan)                
            #set up to skip some images.
            if len(minx) >200:
                step = len(minx)/200 + 1
            else:
                step = 1
            #display scan 
            for i in xrange(0, len(minx)-1,step ):
                if imageToBeUsed[scan][i]:
                    self.renderBounds((minx[i], maxx[i], miny[i], \
                                      maxy[i], minz[i], maxz[i]))
        axes = vtk.vtkCubeAxesActor()
        rangeBounds = self.dataSource.getRangeBounds()
        
        axes.SetBounds((rangeBounds[0], rangeBounds[1], \
                        rangeBounds[2], rangeBounds[3], \
                        rangeBounds[4], rangeBounds[5]))
        axes.SetCamera(self.ren.GetActiveCamera())
        self.ren.AddActor(axes)
        self.ren.ResetCamera()
        self.renWin.Render()
                                
    def scanSelected(self, item):
        '''
        When a scan is selected from the list, change the table to display 
        information about the images in that scan and call to to show the 
        bounds of the selected images in that scan.
        '''
        scanNo = int(item.text().split(' ')[0])
        angles = self.dataSource.getAngles(scanNo)
        self.showAngles(angles)
        self.showQs(scanNo)
        self.selectAll.setEnabled(True)
        self.deselectAll.setEnabled(True)
                
    def selectAllAction(self):
        '''
        Mark all images in the currently selected scan for use in analysis
        '''
        scanNo = self.getSelectedScan()
        for i in xrange(len(self.dataSource.imageToBeUsed[scanNo])):
            self.dataSource.imageToBeUsed[scanNo][i] = True
        self.showQs(scanNo)
                        
    def showAngles(self, angles):
        '''
        Display the angles associated with images in the scan in the table.
        '''
        numAngles = len(self.dataSource.getSampleAngleNames() + \
                        self.dataSource.getDetectorAngleNames())
        self.detail.setRowCount(angles.size)
        blackBrush = QBrush()
        blackBrush.setColor(QColor('black'))
        row = 0
        self.disconnect(self.detail, SIGNAL("itemChanged(QTableWidgetItem *)"), 
                        self.checkItemChanged)

        for angle in angles:
            checkItem = QTableWidgetItem(1)
            checkItem.data(Qt.CheckStateRole)
            checkItem.setCheckState(Qt.Checked)
            self.detail.setItem(row, 0, checkItem)
            for i in xrange(len(angle)):
                self.addValueToTable(angle[i], row, i+1, blackBrush)
            row +=1
        self.connect(self.detail, SIGNAL("itemChanged(QTableWidgetItem *)"), 
                    self.checkItemChanged)

    def showQs(self, scan ):
        '''
        Display q max/min value for the image in the selected scan in the table
        and render the boundaries for those Q values.
        '''
        self.ren.RemoveAllViewProps()
        redBrush = QBrush()
        redBrush.setColor(QColor('red'))
        blackBrush = QBrush()
        blackBrush.setColor(QColor('black'))
        xmin, xmax, ymin, ymax, zmin, zmax = \
            self.dataSource.getImageBounds(scan)
        row = 0
        self.disconnect(self.detail, SIGNAL("itemChanged(QTableWidgetItem *)"), 
                        self.checkItemChanged)
        imageToBeUsed = self.dataSource.getImageToBeUsed()
        numAngles = len(self.dataSource.getSampleAngleNames() + \
                        self.dataSource.getDetectorAngleNames())
        for value in xmin:
            if imageToBeUsed[scan][row]:
                self.addValueToTable(xmin[row], row, numAngles + 1, blackBrush)
                self.addValueToTable(xmax[row], row, numAngles + 2, blackBrush)
                self.addValueToTable(ymin[row], row, numAngles + 3, blackBrush)
                self.addValueToTable(ymax[row], row, numAngles + 4, blackBrush)
                self.addValueToTable(zmin[row], row, numAngles + 5, blackBrush)
                self.addValueToTable(zmax[row], row, numAngles + 6, blackBrush)
                self.renderBounds((xmin[row], xmax[row], ymin[row], ymax[row], \
                    zmin[row], zmax[row]))
                checkItem = self.detail.item(row,0)
                checkItem.setCheckState(Qt.Checked)
            else:
                self.addValueToTable(xmin[row], row, numAngles + 1, redBrush)
                self.addValueToTable(xmax[row], row, numAngles + 2, redBrush)
                self.addValueToTable(ymin[row], row, numAngles + 3, redBrush)
                self.addValueToTable(ymax[row], row, numAngles + 4, redBrush)
                self.addValueToTable(zmin[row], row, numAngles + 5, redBrush)
                self.addValueToTable(zmax[row], row, numAngles + 6, redBrush)
                checkItem = self.detail.item(row,0)
                checkItem.setCheckState(Qt.Unchecked)
            row +=1
        
                         
        scanXmin, scanXmax, scanYmin, scanYmax, scanZmin, scanZmax = \
           self.dataSource.findScanQs(xmin, xmax, ymin, ymax, zmin, zmax)
        self.xminText.setText(str(scanXmin))
        self.xmaxText.setText(str(scanXmax))
        self.yminText.setText(str(scanYmin))
        self.ymaxText.setText(str(scanYmax))
        self.zminText.setText(str(scanZmin))
        self.zmaxText.setText(str(scanZmax))
        self.renderBounds((scanXmin, scanXmax, scanYmin, scanYmax, \
            scanZmin, scanZmax))
        axes = vtk.vtkCubeAxesActor()
        axes.SetBounds((scanXmin, scanXmax, scanYmin, scanYmax, \
            scanZmin, scanZmax))
        axes.SetCamera(self.ren.GetActiveCamera())

        self.ren.AddActor(axes)
        self.ren.ResetCamera()
        self.renWin.Render()
        self.connect(self.detail, SIGNAL("itemChanged(QTableWidgetItem *)"), 
                    self.checkItemChanged)

