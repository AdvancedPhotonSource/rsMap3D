'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import QWidget
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QTabWidget
from PyQt4.QtGui import QMessageBox
from PyQt4.QtGui import QApplication
 
from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource
from rsMap3D.datasource.Sector33SpecDataSource import LoadCanceledException
from rsMap3D.gui.scanform import ScanForm
from rsMap3D.gui.fileform import FileForm
from rsMap3D.gui.datarange import DataRange
from rsMap3D.gui.processscans import ProcessScans
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.transforms.polemaptransform3d import PoleMapTransform3D

import sys
import traceback

class MainDialog(QWidget):
    '''
    '''
    def __init__(self,parent=None):
        '''
        '''
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
        self.processTabIndex = self.tabs.addTab(self.processScans, 
                                                "Process Data")
        self.tabs.setTabEnabled(self.dataTabIndex, False)
        self.tabs.setTabEnabled(self.scanTabIndex, False)
        self.tabs.setTabEnabled(self.processTabIndex, False)
        self.tabs.show()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

        self.connect(self.fileForm, SIGNAL("loadFile"), self.spawnLoadThread)
        self.connect(self.fileForm, SIGNAL("cancelLoadFile"), 
                     self.cancelLoadThread)
        self.connect(self.scanForm, SIGNAL("doneLoading"), self.setupRanges)
        self.connect(self.dataRange, SIGNAL("rangeChanged"), self.setScanRanges)
        self.connect(self.tabs, SIGNAL("currentChanged(int)"), self.tabChanged)
        self.connect(self.processScans, SIGNAL("process"), self.runMapper)
        self.connect(self, SIGNAL("fileError"), self.showFileError)
        
    def cancelLoadThread(self):
        self.dataSource.signalCancelLoadSource()
        
        
    def loadScanFile(self):
        '''
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, False)
        self.tabs.setTabEnabled(self.scanTabIndex, False)
        self.tabs.setTabEnabled(self.processTabIndex, False)
        if self.fileForm.getOutputType() == self.fileForm.SIMPLE_GRID_MAP_STR:
            self.transform = UnityTransform3D()
        elif self.fileForm.getOutputType() == self.fileForm.POLE_MAP_STR:
            self.transform = PoleMapTransform3D()
        else:
            self.transform = None
            
             
        try:
            self.dataSource = \
                Sector33SpecDataSource(str(self.fileForm.getProjectDir()), \
                                       str(self.fileForm.getProjectName()), \
                                       str(self.fileForm.getProjectExtension()), \
                                       str(self.fileForm.getInstConfigName()), \
                                       str(self.fileForm.getDetConfigName()), \
                                       transform = self.transform, \
                                       scanList = self.fileForm.getScanList(), \
                                       roi = self.fileForm.getDetectorROI(), \
                                       pixelsToAverage = \
                                          self.fileForm.getPixelsToAverage()
                                          )
            self.dataSource.loadSource()
        except LoadCanceledException as e:
            print "LoadCanceled"
            self.tabs.setTabEnabled(self.dataTabIndex, False)
            self.tabs.setTabEnabled(self.scanTabIndex, False)
            self.tabs.setTabEnabled(self.processTabIndex, False)
            self.fileForm.setLoadOK()
            return
        except Exception as e:
            self.emit(SIGNAL("fileError"), str(e))
            print traceback.format_exc()
            return
        
        self.scanForm.loadScanFile(self.dataSource)        
        self.fileForm.setLoadOK()
        
    def spawnLoadThread(self):
        self.fileForm.setCancelOK()
        self.loadThread = LoadScanThread(self, parent=None)
        self.loadThread.start()
        
    def setupRanges(self):
        '''
        '''
        overallXmin, overallXmax, overallYmin, overallYmax, \
               overallZmin, overallZmax = self.dataSource.getOverallRanges()
        self.dataRange.setRanges(overallXmin, \
                                 overallXmax, \
                                 overallYmin, \
                                 overallYmax, \
                                 overallZmin, \
                                 overallZmax)
        self.setScanRanges()
        self.tabs.setTabEnabled(self.dataTabIndex, True)
        self.tabs.setTabEnabled(self.scanTabIndex, True)
        self.tabs.setTabEnabled(self.processTabIndex, True)
    
    def setScanRanges(self):
        '''
        '''
        ranges = self.dataRange.getRanges()
        self.dataSource.setRangeBounds(ranges)
        self.scanForm.renderOverallQs()

    def showFileError(self, error):
        message = QMessageBox()
        message.warning(self, \
                            "Load Scanfile Warning", \
                             str(error))
              
    def tabChanged(self, index):
        '''
        '''
        if str(self.tabs.tabText(index)) == "Data Range":
            self.scanForm.renderOverallQs()
                                        
    def runMapper(self):
        self.processScans.runMapper(self.dataSource, self.transform)
        
class LoadScanThread(QThread):
    def __init__(self, controller, **kwargs):
        super(LoadScanThread, self).__init__( **kwargs)
        self.controller = controller
        
    def run(self):
        self.controller.loadScanFile()
        
        
app = QApplication(sys.argv)
mainForm = MainDialog()
mainForm.show()
app.exec_()

