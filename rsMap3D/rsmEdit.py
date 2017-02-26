'''
 Copyright (c) 2014,2017 UChicago Argonne, LLC
 See LICENSE file.
'''
import signal
import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
 
from  PyQt4.QtCore import pyqtSignal as Signal
from  PyQt4.QtCore import pyqtSlot as Slot

from rsMap3D.gui.scanform import ScanForm
from rsMap3D.gui.datarange import DataRange
from rsMap3D.gui.dataextentview import DataExtentView

import sys
from rsMap3D.gui.rsmap3dsignals import UNBLOCK_TABS_FOR_LOAD_SIGNAL
from rsMap3D.gui.input.fileinputcontroller import FileInputController
from rsMap3D.gui.output.processscanscontroller import ProcessScansController
import logging
#import logging.handlers
from rsMap3D.gui.rsm3dcommonstrings import LOGGER_NAME, LOGGER_FORMAT
import os
    
#logging.basicConfig()
#logging.basicConfig(format=LOGGER_FORMAT)
logger = logging.getLogger(LOGGER_NAME)
userDir = os.path.expanduser("~")
logFile = os.path.join(userDir, LOGGER_NAME + '.log')
fh = logging.FileHandler(logFile, delay=0)
fh.setLevel(logging.WARNING)
ch = logging.StreamHandler()
ch.setLevel(logging.WARNING)
formatter = logging.Formatter(LOGGER_FORMAT)
fh.setFormatter(formatter)
ch.setFormatter(formatter)
logger.addHandler(fh)
logger.addHandler(ch)

#    logging.config.dictConfig("rsMap.logConfig")
    
class MainDialog(qtGui.QMainWindow):
    '''
    Main dialog for rsMap3D.  This class also serves as the over action 
    controller for the application
    '''
    #define signals to be used here
    unblockTabsForLoad = Signal(name=UNBLOCK_TABS_FOR_LOAD_SIGNAL)
                               
    
    def __init__(self,parent=None):
        '''
        '''
        logger.debug("Starting rsmEdit")
        super(MainDialog, self).__init__(parent)
        #Create and layout the widgets
        self.tabs = qtGui.QTabWidget()
#        self.fileForm =FileForm()
#        self.fileForm = S34HDFEScanFileForm()
        self.fileForm = FileInputController()
        self.scanForm = ScanForm()
        self.dataRange = DataRange()
        self.processScans = ProcessScansController(parent=self)
        self.dataExtentView = DataExtentView()
        self.fileTabIndex = self.tabs.addTab(self.fileForm, "File")
        self.dataTabIndex = self.tabs.addTab(self.dataRange, "Data Range")
        self.scanTabIndex = self.tabs.addTab(self.scanForm, "Scans")
        self.processTabIndex = self.tabs.addTab(self.processScans, 
                                                "Process Data")
        self.tabs.setTabEnabled(self.dataTabIndex, False)
        self.tabs.setTabEnabled(self.scanTabIndex, False)
        self.tabs.setTabEnabled(self.processTabIndex, False)
        self.tabs.show()
        self.setCentralWidget(self.tabs)

        #Connect signals
#         self.connect(self, \
#                      qtCore.SIGNAL(BLOCK_TABS_FOR_LOAD_SIGNAL), \
#                      self._blockTabsForLoad)
        self.unblockTabsForLoad.connect(self._unblockTabsForLoad)
#         self.connect(self, \
#                      qtCore.SIGNAL(FILE_ERROR_SIGNAL), \
#                      self._showFileError)
        self.tabs.currentChanged[int].connect(self._tabChanged)
        self.fileForm.fileError[str].connect(self._showFileError)
        self.fileForm.blockTabsForLoad.connect(self._blockTabsForLoad)
#         self.connect(self.fileForm, \
#                      qtCore.SIGNAL(SET_SCAN_LOAD_OK_SIGNAL), \
#                      self.fileForm.setLoadOK)
#         self.connect(self, \
#                      qtCore.SIGNAL(SET_SCAN_LOAD_CANCEL_SIGNAL), \
#                      self.fileForm.setCancelOK)
        self.fileForm.loadDataSourceToScanForm.\
            connect(self._loadDataSourceToScanForm)
        self.fileForm.inputFormChanged.connect(self.updateOutputForms)
        self.dataRange.rangeChanged.connect(self._setScanRanges)
        self.scanForm.doneLoading.connect(self._setupRanges)
        self.scanForm.showRangeBounds[object].connect( \
            self.dataExtentView.showRangeBounds)
        self.scanForm.clearRenderWindow.connect(
            self.dataExtentView.clearRenderWindow)
        self.scanForm.renderBoundsSignal[object].connect(
            self.dataExtentView.renderBounds)
#         self.processScans.processError[str].connect(self._showProcessError)
        self.processScans.blockTabsForProcess.connect(self._blockTabsForProcess)
        self.processScans.unblockTabsForProcess.connect( \
            self._unblockTabsForProcess)
        
    def _blockTabsForLoad(self):
        '''
        Disable tabs while loading
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, False)
        self.tabs.setTabEnabled(self.scanTabIndex, False)
        self.tabs.setTabEnabled(self.processTabIndex, False)
        
    @Slot()
    def _blockTabsForProcess(self):
        '''
        disable tabs while processing
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, False)
        self.tabs.setTabEnabled(self.scanTabIndex, False)
        self.tabs.setTabEnabled(self.fileTabIndex, False)
        
        
        
    def closeEvent(self, event):
        '''
        process event on window close
        '''
        self.dataExtentView.vtkMain.close()
        
    def getDataSource(self):
        return self.fileForm.dataSource
    
    @qtCore.pyqtSlot()
    def getOutputForms(self):
        return self.fileForm.getOutputForms()    

    def getTransform(self):
        return self.fileForm.transform
        
    @qtCore.pyqtSlot()
    def _loadDataSourceToScanForm(self):
        '''
        When scan is done loading, load the data to the scan form.
        '''
        self.scanForm.loadScanFile(self.fileForm.dataSource)        
        
        
    @qtCore.pyqtSlot()
    def _setupRanges(self):
        '''
        Get the overall data extent from the data source and set these values
        in the dataRange tab.  
        '''
        overallXmin, overallXmax, overallYmin, overallYmax, \
               overallZmin, \
               overallZmax = self.fileForm.dataSource.getOverallRanges()
        self.dataRange.setRanges(overallXmin, \
                                 overallXmax, \
                                 overallYmin, \
                                 overallYmax, \
                                 overallZmin, \
                                 overallZmax)
        self._setScanRanges()
        self.unblockTabsForLoad.emit()
        
    def _setScanRanges(self):
        '''
        Get the data range from the dataRange tab and set the bounds in this 
        class.  Tell scanForm tab to render the Qs for all scans.
        '''
        ranges = self.dataRange.getRanges()
        self.fileForm.dataSource.setRangeBounds(ranges)
        self.scanForm.renderOverallQs()

    @qtCore.pyqtSlot(str)
    def _showFileError(self, error):
        '''
        Show any errors from file loading in a message dialog.  When done, 
        toggle Load and Cancel buttons in file tab to Load Active/Cancel 
        inactive
        '''
        message = qtGui.QMessageBox()
        message.warning(self, \
                            "Load Scan File Warning", \
                             str(error))
        self.fileForm.setLoadOK()
              
#     @Slot(str)
#     def _showProcessError(self, error):
#         '''
#         Show any errors from file processing in a message dialog.  When done, 
#         toggle Load and Cancel buttons in file tab to Load Active/Cancel 
#         inactive
#         '''
#         message = qtGui.QMessageBox()
#         message.warning(self, \
#                             "Processing Scan File Warning", \
#                              str(error))
#         self.processScans.setProcessRunOK.emit()
              
    @Slot(int)
    def _tabChanged(self, index):
        '''
        When changing to the data range tab, display all qs from all scans.
        '''
        if str(self.tabs.tabText(index)) == "Data Range":
            self.scanForm.renderOverallQs()
                                        
    def _unblockTabsForLoad(self):
        '''
        enable tabs when done loading
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, True)
        self.tabs.setTabEnabled(self.scanTabIndex, True)
        self.tabs.setTabEnabled(self.processTabIndex, True)
        
    @Slot()
    def _unblockTabsForProcess(self):
        '''
        enable tabs when done processing
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, True)
        self.tabs.setTabEnabled(self.scanTabIndex, True)
        self.tabs.setTabEnabled(self.fileTabIndex, True)
        
    def updateOutputForms(self):
        newOutputForms = self.fileForm.getOutputForms()
        self.processScans.updateOutputForms(newOutputForms)
        
def ctrlCHandler(signal, frame):
    qtGui.QApplication.closeAllWindows()
    
#This line allows CTRL_C to work with PyQt.
signal.signal(signal.SIGINT, ctrlCHandler)
app = qtGui.QApplication(sys.argv)
mainForm = MainDialog()
mainForm.show()
#timer allows Python interupts to work
timer = qtCore.QTimer()
timer.start(1000)
timer.timeout.connect(lambda: None)
app.exec_()

