'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource
from rsMap3D.gui.scanform import ScanForm
from rsMap3D.gui.fileform import FileForm
from rsMap3D.gui.datarange import DataRange
from rsMap3D.gui.processscans import ProcessScans
import sys

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

        self.connect(self.fileForm, SIGNAL("loadFile"), self.loadScanFile)
        self.connect(self.scanForm, SIGNAL("doneLoading"), self.setupRanges)
        self.connect(self.dataRange, SIGNAL("rangeChanged"), self.setScanRanges)
        self.connect(self.tabs, SIGNAL("currentChanged(int)"), self.tabChanged)
        self.connect(self.processScans, SIGNAL("doGridMap"), 
                     self.scanForm.doGridMap)      
        self.connect(self.processScans, SIGNAL("doPoleMap"),
                      self.scanForm.doPoleMap)
        self.connect(self.processScans, SIGNAL("process"), self.runMapper)
        
    def loadScanFile(self):
        '''
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, False)
        self.tabs.setTabEnabled(self.scanTabIndex, False)
        self.tabs.setTabEnabled(self.processTabIndex, False)
        self.dataSource = \
            Sector33SpecDataSource(self.fileForm.getProjectDir(), \
                                   self.fileForm.getProjectName(), \
                                   self.fileForm.getInstConfigName(), \
                                   self.fileForm.getDetConfigName())
        
        self.scanForm.loadScanFile(self.dataSource)        

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
        
    def tabChanged(self, index):
        '''
        '''
        if str(self.tabs.tabText(index)) == "Data Range":
            self.scanForm.renderOverallQs()
                                        
    def runMapper(self):
        self.processScans.runMapper(self.dataSource)
        
app = QApplication(sys.argv)
mainForm = MainDialog()
mainForm.show()
app.exec_()
