'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import signal
import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
 
from rsMap3D.gui.scanform import ScanForm
from rsMap3D.gui.datarange import DataRange
from rsMap3D.gui.dataextentview import DataExtentView

import sys
from rsMap3D.gui.qtsignalstrings import CURRENT_TAB_CHANGED
from rsMap3D.gui.rsmap3dsignals import DONE_LOADING_SIGNAL, \
    RANGE_CHANGED_SIGNAL, FILE_ERROR_SIGNAL, PROCESS_ERROR_SIGNAL,\
    BLOCK_TABS_FOR_LOAD_SIGNAL, UNBLOCK_TABS_FOR_LOAD_SIGNAL,\
    BLOCK_TABS_FOR_PROCESS_SIGNAL, UNBLOCK_TABS_FOR_PROCESS_SIGNAL,\
    SET_PROCESS_RUN_OK_SIGNAL, SET_SCAN_LOAD_OK_SIGNAL,\
    SET_SCAN_LOAD_CANCEL_SIGNAL,\
    LOAD_DATASOURCE_TO_SCAN_FORM_SIGNAL, SHOW_RANGE_BOUNDS_SIGNAL,\
    CLEAR_RENDER_WINDOW_SIGNAL, RENDER_BOUNDS_SIGNAL, INPUT_FORM_CHANGED
from rsMap3D.gui.input.fileinputcontroller import FileInputController
from rsMap3D.gui.output.processscanscontroller import ProcessScansController
import logging
from rsMap3D.gui.rsm3dcommonstrings import LOGGER_NAME, LOGGER_FORMAT
from os.path import expanduser, join
    
    
class MainDialog(qtGui.QMainWindow):
    '''
    Main dialog for rsMap3D.  This class also serves as the over action 
    controller for the application
    '''
    logging.getLogger(LOGGER_NAME)
    userDir = expanduser("~")
    logConfig = join(userDir,".rsMap3D.logConfig")

#    logging.config.dictConfig("rsMap.logConfig")

    logging.basicConfig(level=logging.INFO, format=LOGGER_FORMAT)
    
    def __init__(self,parent=None):
        '''
        '''
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
        self.connect(self.scanForm, \
                     qtCore.SIGNAL(DONE_LOADING_SIGNAL), \
                     self._setupRanges)
        self.connect(self.dataRange, \
                     qtCore.SIGNAL(RANGE_CHANGED_SIGNAL), \
                     self._setScanRanges)
        self.connect(self.tabs, \
                     qtCore.SIGNAL(CURRENT_TAB_CHANGED), 
                     self._tabChanged)
        self.connect(self, \
                     qtCore.SIGNAL(FILE_ERROR_SIGNAL), \
                     self._showFileError)
        self.connect(self.fileForm, \
                     qtCore.SIGNAL(FILE_ERROR_SIGNAL), \
                     self._showFileError)
        self.connect(self.processScans, \
                     qtCore.SIGNAL(PROCESS_ERROR_SIGNAL), \
                     self._showProcessError)
        self.connect(self.fileForm, \
                     qtCore.SIGNAL(BLOCK_TABS_FOR_LOAD_SIGNAL), \
                     self._blockTabsForLoad)
        self.connect(self, \
                     qtCore.SIGNAL(BLOCK_TABS_FOR_LOAD_SIGNAL), \
                     self._blockTabsForLoad)
        self.connect(self, \
                     qtCore.SIGNAL(UNBLOCK_TABS_FOR_LOAD_SIGNAL), \
                     self._unblockTabsForLoad)
        self.connect(self.processScans, \
                     qtCore.SIGNAL(BLOCK_TABS_FOR_PROCESS_SIGNAL), \
                     self._blockTabsForProcess)
        self.connect(self.processScans, \
                     qtCore.SIGNAL(UNBLOCK_TABS_FOR_PROCESS_SIGNAL), \
                     self._unblockTabsForProcess)
        self.connect(self.fileForm, \
                     qtCore.SIGNAL(SET_SCAN_LOAD_OK_SIGNAL), \
                     self.fileForm.setLoadOK)
        self.connect(self, \
                     qtCore.SIGNAL(SET_SCAN_LOAD_CANCEL_SIGNAL), \
                     self.fileForm.setCancelOK)
        self.connect(self.fileForm, \
                     qtCore.SIGNAL(LOAD_DATASOURCE_TO_SCAN_FORM_SIGNAL), \
                     self._loadDataSourceToScanForm)
        self.connect(self.scanForm, \
                     qtCore.SIGNAL(SHOW_RANGE_BOUNDS_SIGNAL),
                     self.dataExtentView.showRangeBounds)
        self.connect(self.scanForm, \
                     qtCore.SIGNAL(CLEAR_RENDER_WINDOW_SIGNAL),
                     self.dataExtentView.clearRenderWindow)
        self.connect(self.scanForm, \
                     qtCore.SIGNAL(RENDER_BOUNDS_SIGNAL),
                     self.dataExtentView.renderBounds)
        self.connect(self.fileForm, \
                     qtCore.SIGNAL(INPUT_FORM_CHANGED),
                     self.updateOutputForms)
        
    def _blockTabsForLoad(self):
        '''
        Disable tabs while loading
        '''
        self.tabs.setTabEnabled(self.dataTabIndex, False)
        self.tabs.setTabEnabled(self.scanTabIndex, False)
        self.tabs.setTabEnabled(self.processTabIndex, False)
        
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
    
    def getOutputForms(self):
        return self.fileForm.getOutputForms()    

    def getTransform(self):
        return self.fileForm.transform
        
    def _loadDataSourceToScanForm(self):
        '''
        When scan is done loading, load the data to the scan form.
        '''
        self.scanForm.loadScanFile(self.fileForm.dataSource)        
        
        
    def _setupRanges(self):
        '''
        Get the overall data extent from the data source and set these values
        in the dataRange tab.  
        '''
        overallXmin, overallXmax, overallYmin, overallYmax, \
               overallZmin, overallZmax = self.fileForm.dataSource.getOverallRanges()
        self.dataRange.setRanges(overallXmin, \
                                 overallXmax, \
                                 overallYmin, \
                                 overallYmax, \
                                 overallZmin, \
                                 overallZmax)
        self._setScanRanges()
        self.emit(qtCore.SIGNAL(UNBLOCK_TABS_FOR_LOAD_SIGNAL))
        
    def _setScanRanges(self):
        '''
        Get the data range from the dataRange tab and set the bounds in this 
        class.  Tell scanForm tab to render the Qs for all scans.
        '''
        ranges = self.dataRange.getRanges()
        self.fileForm.dataSource.setRangeBounds(ranges)
        self.scanForm.renderOverallQs()

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
              
    def _showProcessError(self, error):
        '''
        Show any errors from file processing in a message dialog.  When done, 
        toggle Load and Cancel buttons in file tab to Load Active/Cancel 
        inactive
        '''
        message = qtGui.QMessageBox()
        message.warning(self, \
                            "Processing Scan File Warning", \
                             str(error))
        self.emit(qtCore.SIGNAL(SET_PROCESS_RUN_OK_SIGNAL))
              
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

