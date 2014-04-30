'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''

from PyQt4.QtCore import SIGNAL
from PyQt4.QtCore import QThread
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
from rsMap3D.mappers.abstractmapper import ProcessCanceledException
from rsMap3D.exception.rsmap3dexception import ScanDataMissingException,\
    DetectorConfigException, InstConfigException, Transform3DException

class MainDialog(QWidget):
    '''
    Main dialog for rsMap3D.  This class also serves as the over action 
    controller for the application
    '''
    def __init__(self,parent=None):
        '''
        '''
        super(MainDialog, self).__init__(parent)
        #Create and layout the widgets
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

        #Connect signals
        self.connect(self.fileForm, SIGNAL("loadFile"), self.spawnLoadThread)
        self.connect(self.fileForm, SIGNAL("cancelLoadFile"), 
                     self.cancelLoadThread)
        self.connect(self.scanForm, SIGNAL("doneLoading"), self.setupRanges)
        self.connect(self.dataRange, SIGNAL("rangeChanged"), self.setScanRanges)
        self.connect(self.tabs, SIGNAL("currentChanged(int)"), self.tabChanged)
        self.connect(self.processScans, SIGNAL("process"), \
                     self.spawnProcessThread)
        self.connect(self.processScans, SIGNAL("cancelProcess"), \
                     self.stopMapper)
        self.connect(self, SIGNAL("fileError"), self.showFileError)
        self.connect(self, SIGNAL("processError"), self.showProcessError)
        self.connect(self.processScans, SIGNAL("processError"), 
                     self.showProcessError)
        
        self.connect(self, SIGNAL("blockTabsForLoad"), 
                     self.blockTabsForLoad)
        self.connect(self, SIGNAL("unblockTabsForLoad"), 
                     self.unblockTabsForLoad)
        self.connect(self, SIGNAL("blockTabsForProcess"), 
                     self.blockTabsForProcess)
        self.connect(self, SIGNAL("unblockTabsForProcess"), 
                     self.unblockTabsForProcess)
        self.connect(self, SIGNAL("setProcessRunOK"), 
                     self.processScans.setRunOK)
        self.connect(self, SIGNAL("setProcessCancelOK"), 
                     self.processScans.setCancelOK)
        self.connect(self, SIGNAL("setScanLoadOK"), 
                     self.fileForm.setLoadOK)
        self.connect(self, SIGNAL("setScanLoadCancelOK"), 
                     self.fileForm.setCancelOK)
        self.connect(self, SIGNAL("loadDataSourceToScanForm"), 
                     self.loadDataSourceToScanForm)
        
    def blockTabsForLoad(self):
        '''
        Disable tabs while loading
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, False)
        self.tabs.setTabEnabled(self.scanTabIndex, False)
        self.tabs.setTabEnabled(self.processTabIndex, False)
        
    def blockTabsForProcess(self):
        '''
        disable tabs while processing
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, False)
        self.tabs.setTabEnabled(self.scanTabIndex, False)
        self.tabs.setTabEnabled(self.fileTabIndex, False)
        
        
    def cancelLoadThread(self):
        '''
        Let the data source know that a cancel has been requested.
        '''
        self.dataSource.signalCancelLoadSource()
        
        
    def loadDataSourceToScanForm(self):
        '''
        '''
        self.scanForm.loadScanFile(self.dataSource)        
        
    def loadScanFile(self):
        '''
        Set up to load the scan file
        '''
        self.emit(SIGNAL("blockTabsForLoad"))
        if self.fileForm.getOutputType() == self.fileForm.SIMPLE_GRID_MAP_STR:
            self.transform = UnityTransform3D()
        elif self.fileForm.getOutputType() == self.fileForm.POLE_MAP_STR:
            self.transform = \
                PoleMapTransform3D(projectionDirection=\
                                   self.fileForm.getProjectionDirection())
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
                                          self.fileForm.getPixelsToAverage(), \
                                       badPixelFile = \
                                          self.fileForm.getBadPixelFileName(), \
                                       flatFieldFile = \
                                          self.fileForm.getFlatFieldFileName() \
                                      )
            self.dataSource.setProgressUpdater(self.fileForm.updateProgress)
            self.dataSource.loadSource(mapHKL = self.fileForm.getMapAsHKL())
        except LoadCanceledException as e:
            print "LoadCanceled"
            self.emit(SIGNAL("blockTabsForLoad"))
            self.emit(SIGNAL("setScanLoadOK"))
            #self.fileForm.setLoadOK()
            return
        except ScanDataMissingException as e:
            self.emit(SIGNAL("fileError"), str(e))
            return
        except DetectorConfigException as e:
            self.emit(SIGNAL("fileError"), str(e))
            return
        except InstConfigException as e:
            self.emit(SIGNAL("fileError"), str(e))
            return
        except Transform3DException as e:
            self.emit(SIGNAL("fileError"), str(e))
            return 
        except ScanDataMissingException as e:
            self.emit(SIGNAL("fileError"), str(e))
            return
        except Exception as e:
            self.emit(SIGNAL("fileError"), str(e))
            print traceback.format_exc()
            return
        
            
        self.emit(SIGNAL("loadDataSourceToScanForm"))
        self.emit(SIGNAL("setScanLoadOK"))
        
    def spawnLoadThread(self):
        '''
        Spawm a new thread to load the scan so that scan may be canceled later 
        and so that this does not interfere with the GUI operation.
        '''
        self.fileForm.setCancelOK()
        self.loadThread = LoadScanThread(self, parent=None)
        self.loadThread.start()
        
    def spawnProcessThread(self):
        '''
        Spawm a new thread to load the scan so that scan may be canceled later 
        and so that this does not interfere with the GUI operation.
        '''
        self.processScans.setProgressLimits(1, 
                                len(self.dataSource.getAvailableScans()))
        self.processScans.setCancelOK()
        self.processThread = ProcessScanThread(self, parent=None)
        self.processThread.start()
        
    def setupRanges(self):
        '''
        Get the overall data extent from the datasource and set these values
        in the dataRange tab.  
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
        self.emit(SIGNAL("unblockTabsForLoad"))
        
    def setScanRanges(self):
        '''
        Get the datarange from the dataRange tab and set the bounds in this 
        class.  Tell scanForm tab to render the Qs for all scans.
        '''
        ranges = self.dataRange.getRanges()
        self.dataSource.setRangeBounds(ranges)
        self.scanForm.renderOverallQs()

    def showFileError(self, error):
        '''
        Show any errors from file loading in a message dialog.  When done, 
        toggle Load and Cancel buttons in file tab to Load Active/Cancel 
        inactive
        '''
        message = QMessageBox()
        message.warning(self, \
                            "Load Scanfile Warning", \
                             str(error))
        self.fileForm.setLoadOK()
              
    def tabChanged(self, index):
        '''
        When changing to the datarange tab, display all qs from all scans.
        '''
        if str(self.tabs.tabText(index)) == "Data Range":
            self.scanForm.renderOverallQs()
                                        
    def runMapper(self):
        '''
        Tell the processScans tab to launch the mapper.
        '''
        self.emit(SIGNAL("blockTabsForProcess"))
        self.emit(SIGNAL("setProcessCancelOK"))
        try:
            self.processScans.runMapper(self.dataSource, self.transform)
        except ProcessCanceledException:
            self.emit(SIGNAL("unblockTabsForProcess"))
        except Exception as e:
            self.emit(SIGNAL("processError"), str(e))
            print traceback.format_exc()
            return
        self.emit(SIGNAL("setProcessRunOK"))
        self.emit(SIGNAL("unblockTabsForProcess"))
        
    def showProcessError(self, error):
        '''
        Show any errors from file processing in a message dialog.  When done, 
        toggle Load and Cancel buttons in file tab to Load Active/Cancel 
        inactive
        '''
        message = QMessageBox()
        message.warning(self, \
                            "Processing Scanfile Warning", \
                             str(error))
        self.emit(SIGNAL("setProcessRunOK"))
              
    def stopMapper(self):
        '''
        Tell the processScans tab to stop the mapper.
        '''
        self.processScans.stopMapper()
        
    def unblockTabsForLoad(self):
        '''
        enable tabs when done loading
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, True)
        self.tabs.setTabEnabled(self.scanTabIndex, True)
        self.tabs.setTabEnabled(self.processTabIndex, True)
        
    def unblockTabsForProcess(self):
        '''
        enable tabs when done processing
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, True)
        self.tabs.setTabEnabled(self.scanTabIndex, True)
        self.tabs.setTabEnabled(self.fileTabIndex, True)
        
        
class LoadScanThread(QThread):
    def __init__(self, controller, **kwargs):
        super(LoadScanThread, self).__init__( **kwargs)
        self.controller = controller
        
    def run(self):
        self.controller.loadScanFile()
        
class ProcessScanThread(QThread):
    def __init__(self, controller, **kwargs):
        super(ProcessScanThread, self).__init__( **kwargs)
        self.controller = controller

    def run(self):
        self.controller.runMapper()
        
app = QApplication(sys.argv)
mainForm = MainDialog()
mainForm.show()
app.exec_()

