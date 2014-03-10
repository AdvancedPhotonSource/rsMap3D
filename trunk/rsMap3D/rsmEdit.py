import sys
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pyspec import spec
import xrayutilities as xu
import numpy as np
import vtk
from vtk.qt4.QVTKRenderWindowInteractor import  QVTKRenderWindowInteractor
import xrayutilities_33bmc_functions as bm
import time
from vtk.util import numpy_support
from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource

class MainDialog(QWidget):
    def __init__(self,parent=None):
        super(MainDialog, self).__init__(parent)
        layout = QGridLayout()
        self.tabs = QTabWidget()
        self.fileForm =FileForm()
        self.scanForm = ScanForm()
        self.dataRange = DataRange()
        self.processScans = ProcessScans()
        self.fileTabIndex = self.tabs.addTab(self.fileForm, "File")
        self.dataTabIndex = self.tabs.addTab(self.dataRange, "Data Range")
        self.scanTabIndex = self.tabs.addTab(self.scanForm, "Scans")
        self.processTabIndex = self.tabs.addTab(self.processScans, "Process Data")
        self.tabs.setTabEnabled(self.dataTabIndex, False)
        self.tabs.setTabEnabled(self.scanTabIndex, False)
        self.tabs.setTabEnabled(self.processTabIndex, False)
        self.tabs.show()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.connect(self.fileForm, SIGNAL("loadFile"), self.loadScanFile)
        self.connect(self.scanForm, SIGNAL("doneLoading"), self.setupRanges)
        self.connect(self.dataRange, SIGNAL("rangeChanged"), self.setScanRanges)
        self.connect(self.tabs, SIGNAL("currentChanged(int)"), self.tabChanged)
        self.connect(self.processScans, SIGNAL("doGridMap"), self.scanForm.doGridMap)      
        self.connect(self.processScans, SIGNAL("doPoleMap"), self.scanForm.doPoleMap)
        
    def loadScanFile(self):
        self.tabs.setTabEnabled(self.dataTabIndex, False)
        self.tabs.setTabEnabled(self.scanTabIndex, False)
        self.tabs.setTabEnabled(self.processTabIndex, False)
        self.dataSource = Sector33SpecDataSource(self.fileForm.getProjectDir(), \
                            self.fileForm.getProjectName(), \
                            self.fileForm.getInstConfigName(), \
                            self.fileForm.getDetConfigName())
        
        self.scanForm.loadScanFile(self.dataSource)        

    def setupRanges(self):
        overallXmin, overallXmax, overallYmin, overallYmax, \
               overallZmin, overallZmax = self.dataSource.getOverallRanges()
        self.dataRange.setRanges(overallXmin, overallXmax, overallYmin, overallYmax, \
               overallZmin, overallZmax)
        self.setScanRanges()
        self.tabs.setTabEnabled(self.dataTabIndex, True)
        self.tabs.setTabEnabled(self.scanTabIndex, True)
        self.tabs.setTabEnabled(self.processTabIndex, True)
    
    def setScanRanges(self):
        ranges = self.dataRange.getRanges()
        self.dataSource.setRangeBounds(ranges)
        self.scanForm.renderOverallQs()
        
    def tabChanged(self, index):
        if str(self.tabs.tabText(index)) == "Data Range":
            self.scanForm.renderOverallQs()
                                        
class FileForm(QDialog):
    def __init__(self,parent=None):
        super(FileForm, self).__init__(parent)
        layout = QGridLayout()

        label = QLabel("Project Directory:");
        self.projDirTxt = QLineEdit()
        layout.addWidget(label, 0, 0)
        layout.addWidget(self.projDirTxt, 0, 1)

        label = QLabel("Project Name:");
        self.projNameTxt = QLineEdit()
        layout.addWidget(label, 1, 0)
        layout.addWidget(self.projNameTxt, 1, 1)

        label = QLabel("Instrument Config File:");
        self.instConfigTxt = QLineEdit()
        self.instConfigFileButton = QPushButton("Browse")
        layout.addWidget(label, 2, 0)
        layout.addWidget(self.instConfigTxt, 2, 1)
        layout.addWidget(self.instConfigFileButton, 2, 2)

        label = QLabel("Detector Config File:");
        self.detConfigTxt = QLineEdit()
        self.detConfigFileButton = QPushButton("Browse")
        layout.addWidget(label, 3, 0)
        layout.addWidget(self.detConfigTxt, 3, 1)
        layout.addWidget(self.detConfigFileButton, 3, 2)
        
        
        loadButton = QPushButton("Load")        
        layout.addWidget(loadButton,4 , 1)
        
        self.connect(loadButton, SIGNAL("clicked()"), self.loadFile)
        self.connect(self.instConfigFileButton, SIGNAL("clicked()"), 
                     self.browseForInstFile)
        self.connect(self.detConfigFileButton, SIGNAL("clicked()"), 
                     self.browseForDetFile)
        
        self.setLayout(layout);
        
    def loadFile(self):
        self.emit(SIGNAL("loadFile"))
        
    def browseForInstFile(self):
        print "Browsing for inst file"

    def browseForDetFile(self):
        print "Browsing for Det file"

    def getProjectDir(self):
        return self.projDirTxt.text()
        
    def getProjectName(self):
        return self.projNameTxt.text()
    
    def getInstConfigName(self):
        return self.instConfigTxt.text()

    def getDetConfigName(self):
        return self.detConfigTxt.text()

class DataRange(QDialog):
    def __init__(self, parent=None):                
        super(DataRange, self).__init__(parent)
        self._initializeRanges()
        
        layout = QGridLayout()
        xLabel = QLabel("X")
        xminLabel = QLabel("min")
        self.xminText = QLineEdit()
        xmaxLabel = QLabel("max")
        self.xmaxText = QLineEdit()
        yLabel = QLabel("Y")
        yminLabel = QLabel("min")
        self.yminText = QLineEdit()
        ymaxLabel = QLabel("max")
        self.ymaxText = QLineEdit()
        zLabel = QLabel("Z")
        zminLabel = QLabel("min")
        self.zminText = QLineEdit()
        zmaxLabel = QLabel("max")
        self.zmaxText = QLineEdit()
        buttonLayout = QHBoxLayout()
        resetButton = QPushButton("Reset")
        applyButton = QPushButton("Apply")
        buttonLayout.addWidget(resetButton)
        
        self.connect(resetButton, SIGNAL("clicked()"), self.resetRange)
        self.connect(applyButton, SIGNAL("clicked()"), self.applyRange)
        
        buttonLayout.addWidget(applyButton)
        
        layout.addWidget(xLabel, 0,0)
        layout.addWidget(xminLabel, 0,1)
        layout.addWidget(self.xminText, 0,2)
        layout.addWidget(xmaxLabel, 0,3)
        layout.addWidget(self.xmaxText, 0,4)
        layout.addWidget(yLabel, 1,0)
        layout.addWidget(yminLabel, 1,1)
        layout.addWidget(self.yminText, 1,2)
        layout.addWidget(ymaxLabel, 1,3)
        layout.addWidget(self.ymaxText, 1,4)
        layout.addWidget(zLabel, 2,0)
        layout.addWidget(zminLabel, 2,1)
        layout.addWidget(self.zminText, 2,2)
        layout.addWidget(zmaxLabel, 2,3)
        layout.addWidget(self.zmaxText, 2,4)
        layout.addLayout(buttonLayout, 3,4)
        self.connect(self.xminText, SIGNAL("editingFinished()"), 
            self.xminChanged)
        self.connect(self.xmaxText, SIGNAL("editingFinished()"), 
            self.xmaxChanged)
        self.connect(self.yminText, SIGNAL("editingFinished()"), 
            self.yminChanged)
        self.connect(self.ymaxText, SIGNAL("editingFinished()"), 
            self.ymaxChanged)
        self.connect(self.zminText, SIGNAL("editingFinished()"), 
            self.zminChanged)
        self.connect(self.zmaxText, SIGNAL("editingFinished()"), 
            self.zmaxChanged)
        self.setLayout(layout)
        
    def xminChanged(self):
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def xmaxChanged(self):
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def yminChanged(self):
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def ymaxChanged(self):
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def zminChanged(self):
        #make sure this can be a float also make sure min < max
        print 'change)'
    
    def zmaxChanged(self):
        #make sure this can be a float also make sure min < max
        print 'change)'
        
    def resetRange(self):
        self.xminText.setText(str(self.ranges[0]))
        self.xmaxText.setText(str(self.ranges[1]))
        self.yminText.setText(str(self.ranges[2]))
        self.ymaxText.setText(str(self.ranges[3]))
        self.zminText.setText(str(self.ranges[4]))
        self.zmaxText.setText(str(self.ranges[5]))
        
    def applyRange(self):
        self.ranges = (float(self.xminText.text()),
                       float(self.xmaxText.text()),
                       float(self.yminText.text()),
                       float(self.ymaxText.text()),
                       float(self.zminText.text()),
                       float(self.zmaxText.text()))
        self.emit(SIGNAL("rangeChanged"))
        
    def setRanges(self, xmin, xmax, ymin, ymax, zmin, zmax):
        self.ranges = (xmin, xmax, ymin, ymax, zmin, zmax)
        self.xminText.setText(str(xmin))
        self.xmaxText.setText(str(xmax))
        self.yminText.setText(str(ymin))
        self.ymaxText.setText(str(ymax))
        self.zminText.setText(str(zmin))
        self.zmaxText.setText(str(zmax))
        
    def getRanges(self):
        return self.ranges
        
    def _initializeRanges(self):
        self.ranges = (float("Infinity"), float("-Infinity"), \
                        float("Infinity"), float("-Infinity"), \
                        float("Infinity"), float("-Infinity"))
        
        
class ScanForm(QDialog):
    def __init__(self, parent=None):
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
        self.connect(self.deselectAll, SIGNAL("clicked()"), self.deselectAllAction)
        
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
        self.detail.setColumnCount(11)
        self.detail.setHorizontalHeaderLabels(['Use Image', 'X2mtheta', 'theta', 'phi', 
                                            'chi', 'Min qx', 'Max qx', 'Min qy',
                                            'Max qy', 'Min qz', 'Max qz'])
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
        
    def loadScanFile(self, dataSource):
        #------------------------------------- self.projectDir = str(projectDir)
        #----------------------------------- self.projectName = str(projectName)
        # self.specFile = os.path.join(self.projectDir, self.projectName + ".spc")
        # imageDir = os.path.join(self.projectDir, "images/%s" % self.projectName)
        #-------------------------- self.imageFileTmp = os.path.join(imageDir, \
                                # "S%%03d/%s_S%%03d_%%05d.tif" % (self.projectName))
        #------------------------------------------------------------------ try:
            #------------------------ self.sd = spec.SpecDataFile(self.specFile)
            #--------------------------------------------- self.scanList.clear()
            #------------------------------ maxScan = max(self.sd.findex.keys())
#------------------------------------------------------------------------------ 
            #--------------------------------------- scans = range(1, maxScan+1)
            #------------------------------------------------------- print scans
            #------------------------- imagePath = os.path.join(str(projectDir),
                            #------------------- "images/%s" % str(projectName))
#------------------------------------------------------------------------------ 
            #--------------------------------------------- self.imageBounds = {}
            #------------------------------------------- self.imageToBeUsed = {}
            #------------------------------------------ self.availableScans = []
            #------------------------------------------------ for scan in scans:
                #- if (os.path.exists(os.path.join(imagePath, "S%03d" % scan))):
                    #----------------------------------- curScan = self.sd[scan]
                    #---------------------------------- item = QListWidgetItem()
                    #-------------------- item.setText(str(curScan.scan) + " " +
                                #---------------------------- curScan.scan_type)
                    #------------------------------- self.scanList.addItem(item)
                    # curScan.geo_angle_names=['X2mtheta', 'theta', 'phi', 'chi']
                    #-------------------------- self.availableScans.append(scan)
                    #---------------------------------- #curScan = self.sd[scan]
                    #------------------------- angles = curScan.get_geo_angles()
                    #------------------------------------------- ub = curScan.UB
                    #---------------------------------------------- en = 15200.0
                    #- self.imageBounds[scan] = self.findImageQs(angles, ub, en)
            #---------------------------------- self.emit(SIGNAL("doneLoading"))
        #------------------------------------------------------- except IOError:
            #-------------------- print "Cannot open file " + str(self.specFile)
        self.dataSource = dataSource
        for curScan in self.dataSource.getAvailableScans():
            item = QListWidgetItem()
            item.setText(str(curScan))
            self.scanList.addItem(item)
        self.emit(SIGNAL("doneLoading"))
        
    def scanSelected(self, item):
        scanNo = int(item.text().split(' ')[0])
#        scan = self.sd[scanNo]
#        angles = scan.get_geo_angles()
        angles = self.dataSource.getAngles(scanNo)
        self.showAngles(angles)
        self.showQs(scanNo)
        self.selectAll.setEnabled(True)
        self.deselectAll.setEnabled(True)
                
    def showAngles(self, angles):
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
            self.addValueToTable(angle[0], row, 1, blackBrush)
            self.addValueToTable(angle[1], row, 2, blackBrush)
            self.addValueToTable(angle[2], row, 3, blackBrush)
            self.addValueToTable(angle[3], row, 4, blackBrush)
            row +=1
        self.connect(self.detail, SIGNAL("itemChanged(QTableWidgetItem *)"), 
                    self.checkItemChanged)

    def checkItemChanged(self,item):
        scanNo = self.getSelectedScan()
        row = item.row()
        if item.checkState() == Qt.Checked:
            self.imageToBeUsed[scanNo][row] = True
        else:
            self.imageToBeUsed[scanNo][row] = False
        self.showQs(scanNo)

    def showQs(self, scan ):
        self.ren.RemoveAllViewProps()
        redBrush = QBrush()
        redBrush.setColor(QColor('red'))
        blackBrush = QBrush()
        blackBrush.setColor(QColor('black'))
        xmin, xmax, ymin, ymax, zmin, zmax = self.dataSource.getImageBounds(scan)
        row = 0
        self.disconnect(self.detail, SIGNAL("itemChanged(QTableWidgetItem *)"), 
                        self.checkItemChanged)
        imageToBeUsed = self.dataSource.getImageToBeUsed()
        for value in xmin:
            if imageToBeUsed[scan][row]:
                self.addValueToTable(xmin[row], row, 5, blackBrush)
                self.addValueToTable(xmax[row], row, 6, blackBrush)
                self.addValueToTable(ymin[row], row, 7, blackBrush)
                self.addValueToTable(ymax[row], row, 8, blackBrush)
                self.addValueToTable(zmin[row], row, 9, blackBrush)
                self.addValueToTable(zmax[row], row, 10, blackBrush)
                self.renderBounds((xmin[row], xmax[row], ymin[row], ymax[row], \
                    zmin[row], zmax[row]))
                checkItem = self.detail.item(row,0)
                checkItem.setCheckState(Qt.Checked)
            else:
                self.addValueToTable(xmin[row], row, 5, redBrush)
                self.addValueToTable(xmax[row], row, 6, redBrush)
                self.addValueToTable(ymin[row], row, 7, redBrush)
                self.addValueToTable(ymax[row], row, 8, redBrush)
                self.addValueToTable(zmin[row], row, 9, redBrush)
                self.addValueToTable(zmax[row], row, 10, redBrush)
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

    def renderOverallQs(self):
        self.ren.RemoveAllViewProps()
        imageToBeUsed = self.dataSource.getImageToBeUsed()
        for scan in self.dataSource.getAvailableScans():
            minx, maxx, miny, maxy, minz, maxz = self.dataSource.getImageBounds(scan)                
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
                                
    #---------------------------- def findImageQs(self, angles, ub, en=13000.0):
        # qconv = xu.experiment.QConversion(['z-', 'y+', 'z-'], ['z-'], [0,1,0])
        #-------------- hxrd = xu.HXRD([0, 1, 0], [1, 0, 0], en=en, qconv=qconv)
        #------------------------------------------------------- cch = [206, 85]
        #---------------------------------------------------- chpdeg = [106,106]
        #----------------------------------------------------------- nav = [1,1]
        #------------------------------------------------- roi = [0,487, 0, 195]
        #-- hxrd.Ang2Q.init_area('x-', 'z+', cch1=cch[0], cch2=cch[1], Nch1=487,
           #-- Nch2=195, chpdeg1=chpdeg[0], chpdeg2=chpdeg[1], Nav=nav, roi=roi)
#------------------------------------------------------------------------------ 
        # qx, qy, qz = hxrd.Ang2Q.area(angles[:,1], angles[:,3], angles[:,2], angles[:,0], \
                     #---------------------------------------- roi=roi, Nav=nav)
        #-------------------------------------------------- idx = range(len(qx))
        #----------------------------------- xmin = [np.min(qx[i]) for i in idx]
        #----------------------------------- xmax = [np.max(qx[i]) for i in idx]
        #----------------------------------- ymin = [np.min(qy[i]) for i in idx]
        #----------------------------------- ymax = [np.max(qy[i]) for i in idx]
        #----------------------------------- zmin = [np.min(qz[i]) for i in idx]
        #----------------------------------- zmax = [np.max(qz[i]) for i in idx]
#------------------------------------------------------------------------------ 
        #--------------------------- return (xmin, xmax, ymin, ymax, zmin, zmax)
           
    #----------------- def findScanQs(self, xmin, xmax, ymin, ymax, zmin, zmax):
        #---------------------------------------------- scanXmin = np.min( xmin)
        #---------------------------------------------- scanXmax = np.max( xmax)
        #---------------------------------------------- scanYmin = np.min( ymin)
        #--------------------------------------------- scanYmax = np.max(  ymax)
        #--------------------------------------------- scanZmin = np.min(  zmin)
        #--------------------------------------------- scanZmax = np.max(  zmax)
        #----- return scanXmin, scanXmax, scanYmin, scanYmax, scanZmin, scanZmax

    #----------------------------------------------- def getOverallRanges(self):
        #--------------------------------------- overallXmin = float("Infinity")
        #-------------------------------------- overallXmax = float("-Infinity")
        #--------------------------------------- overallYmin = float("Infinity")
        #-------------------------------------- overallYmax = float("-Infinity")
        #--------------------------------------- overallZmin = float("Infinity")
        #-------------------------------------- overallZmax = float("-Infinity")
        #------------------------ imageBounds = self.dataSource.getImageBounds()
        #-------------------------------------- for scan in self.availableScans:
            #----- overallXmin = min( overallXmin, np.min(imageBounds[scan][0]))
            #----- overallXmax = max( overallXmax, np.max(imageBounds[scan][1]))
            #----- overallYmin = min( overallYmin, np.min(imageBounds[scan][2]))
            #----- overallYmax = max( overallYmax, np.max(imageBounds[scan][3]))
            #----- overallZmin = min( overallZmin, np.min(imageBounds[scan][4]))
            #----- overallZmax = max( overallZmax, np.max(imageBounds[scan][5]))
#------------------------------------------------------------------------------ 
        #---------- return overallXmin, overallXmax, overallYmin, overallYmax, \
               #--------------------------------------- overallZmin, overallZmax
       
    #------------------------------------ def setRangeBounds(self, rangeBounds):
        #--------------------------------------- self.rangeBounds = rangeBounds;
        #------------------------------------------- self.processImageToBeUsed()
        #---------------------------- if len(self.scanList.selectedItems()) > 0:
            #---------------------------------------------- print "do something"
#------------------------------------------------------------------------------ 
    #------------------------------------------- def processImageToBeUsed(self):
        #----------------------------------------------- self.imageToBeUsed = {}
        #-------------------------------------- for scan in self.availableScans:
            #-------------------------------------------------------- inUse = []
            #------------------ for i in xrange(len(self.imageBounds[scan][0])):
                #------------------------------- bounds = self.imageBounds[scan]
                 # if self.inBounds(bounds[0][i], bounds[1][i], bounds[2][i], bounds[3][i], \
                    #------------------------------ bounds[4][i], bounds[5][i]):
                    #---------------------------------------- inUse.append(True)
                #--------------------------------------------------------- else:
                    #--------------------------------------- inUse.append(False)
            #---------------------------------- self.imageToBeUsed[scan] = inUse
#------------------------------------------------------------------------------ 
        
                                            
    #------------------- def inBounds(self, xmin, xmax, ymin, ymax, zmin, zmax):
        # return ((xmin >= self.rangeBounds[0] and xmin <= self.rangeBounds[1]) or \
           # (xmax >= self.rangeBounds[0] and xmax <= self.rangeBounds[1])) and \
           # ((ymin >= self.rangeBounds[2] and ymin <= self.rangeBounds[3]) or \
           # (ymax >= self.rangeBounds[2] and ymax <= self.rangeBounds[3])) and \
           # ((zmin >= self.rangeBounds[4] and zmin <= self.rangeBounds[5]) or \
           #----- (zmax >= self.rangeBounds[4] and zmax <= self.rangeBounds[5]))
   
    def addValueToTable(self, value, row, column, coloredBrush):
        item = QTableWidgetItem(str(value))
        item.setForeground(coloredBrush)
        self.detail.setItem(row, column, item)
        
    def renderBounds(self, bounds):
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
        
    def getSelectedScan(self):
        scansSel = self.scanList.selectedItems()
        if len(scansSel) > 1:
            print "Should not be able to select more than one scan."
        scan = scansSel[0]
        scanNo = int(scan.text().split(' ')[0])
        return scanNo
        
    def selectAllAction(self):
        scanNo = self.getSelectedScan()
        for i in xrange(len(self.imageToBeUsed[scanNo])):
            self.imageToBeUsed[scanNo][i] = True
        self.showQs(scanNo)
                        
    def deselectAllAction(self):
        scanNo = self.getSelectedScan()
        for i in xrange(len(self.imageToBeUsed[scanNo])):
            self.imageToBeUsed[scanNo][i] = False
        self.showQs(scanNo)

    def doGridMap(self):
        print "Doing Grid Map"
        # number of points to be used during the gridding
        nx, ny, nz = 200, 201, 202
        
        # read and grid data with helper function
        _start_time = time.time()
        qx, qy, qz, gint, gridder = \
            bm.gridmap(self.specFile, self.availableScans, \
                       self.imageToBeUsed, self.imageFileTmp, nx, ny, nz, \
                       xmin=self.rangeBounds[0], xmax=self.rangeBounds[1], \
                       ymin=self.rangeBounds[2], ymax=self.rangeBounds[3], \
                       zmin=self.rangeBounds[4], zmax=self.rangeBounds[5], en=15200.0)
        #qx, qy, qz, gint, gridder = bm.polemap(specfile, scanno, imagefiletmp, nx, ny, nz)
        print 'Elapsed time for gridding: %.3f seconds' % (time.time() - _start_time)
        
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
        writer.SetFileName("%s_S%d.vti" % (self.projectName, self.availableScans[0]))
        writer.SetInput(image_data)
        writer.Write()
        
        
    def doPoleMap(self):
        print "Doing Pole Map"
        # number of points to be used during the gridding
        nx, ny, nz = 200, 201, 202
        
        # read and grid data with helper function
        _start_time = time.time()
        qx, qy, qz, gint, gridder = \
            bm.polemap(self.specFile, self.availableScans, \
                       self.imageToBeUsed, self.imageFileTmp, nx, ny, nz, \
                       xmin=self.rangeBounds[0], xmax=self.rangeBounds[1], \
                       ymin=self.rangeBounds[2], ymax=self.rangeBounds[3], \
                       zmin=self.rangeBounds[4], zmax=self.rangeBounds[5], en=15200.0)
        #qx, qy, qz, gint, gridder = bm.polemap(specfile, scanno, imagefiletmp, nx, ny, nz)
        print 'Elapsed time for gridding: %.3f seconds' % (time.time() - _start_time)
        
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
        writer.SetFileName("%s_S%d.vti" % (self.projectName, self.availableScans[0]))
        writer.SetInput(image_data)
        writer.Write()
        
class ProcessScans(QDialog):
    POLE_MAP_STR = "Pole Map"
    GRID_MAP_STR = "Grid Map"
    
    def __init__(self, parent=None):
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
        self.connect(runButton, SIGNAL("clicked()"), self.runMapper)
        
    def runMapper(self):
        print "Selected " + str(self.outTypeChooser.currentText())
        if (self.outTypeChooser.currentText() == self.GRID_MAP_STR):
            self.emit(SIGNAL("doGridMap"))
        else:
            self.emit(SIGNAL("doPoleMap"))
                                                                                                                                                                                                                                                                                                                                             
app = QApplication(sys.argv)
mainForm = MainDialog()
mainForm.show()
app.exec_()
