'''
 Copyright (c) 2014,2017 UChicago Argonne, LLC
 See LICENSE file.
'''
import signal
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets
 
from  PyQt5.QtCore import pyqtSignal as Signal
from  PyQt5.QtCore import pyqtSlot as Slot
from rsMap3D.gui.scanform import ScanForm
from rsMap3D.gui.datarange import DataRange
from rsMap3D.gui.dataextentview import DataExtentView

import sys
import logging
import logging.config

import os
from configparser import NoSectionError
from rsMap3D.config.rsmap3dlogging import LOGGER_NAME, LOGGER_DEFAULT,\
    METHOD_EXIT_STR, METHOD_ENTER_STR
from rsMap3D.gui.rsmap3dsignals import UNBLOCK_TABS_FOR_LOAD_SIGNAL
from rsMap3D.gui.input.fileinputcontroller import FileInputController
from rsMap3D.gui.output.processscanscontroller import ProcessScansController
from rsMap3D.config.rsmap3dconfigparser import RSMap3DConfigParser
    
userDir = os.path.expanduser("~")
logConfigFile = os.path.join(userDir, LOGGER_NAME + 'Log.config')
if os.path.exists(logConfigFile):
    print ("logConfigFile " + logConfigFile )
    try:
        logging.config.fileConfig(logConfigFile, disable_existing_loggers=False)
        print("Success Openning logfile")
    except (NoSectionError,TypeError) as ex:
        print ("In Exception to load dictConfig package %s\n %s" % (LOGGER_NAME, ex))
        logging.config.dictConfig(LOGGER_DEFAULT)
    except KeyError as ex:
        print ("logfile %s was missing or had errant sections %s" %(logConfigFile, ex.args))

else:
    logging.config.dictConfig(LOGGER_DEFAULT)
    
logger = logging.getLogger(LOGGER_NAME)
    
class MainDialog(qtWidgets.QMainWindow):
    '''
    Main dialog for rsMap3D.  This class also serves as the over action 
    controller for the application
    '''
    #define signals to be used here
    unblockTabsForLoad = Signal(name=UNBLOCK_TABS_FOR_LOAD_SIGNAL)
                               
    
    def __init__(self,parent=None):
        '''
        '''
        logger.debug(METHOD_ENTER_STR)
        super(MainDialog, self).__init__(parent)
        #Create and layout the widgets
        self.appConfig = RSMap3DConfigParser()
        self.tabs = qtWidgets.QTabWidget()
        self.fileForm = FileInputController(appConfig=self.appConfig)
        self.scanForm = ScanForm()
        self.dataRange = DataRange()
        self.processScans = ProcessScansController(parent=self, \
                                                   appConfig=self.appConfig)
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
        self.unblockTabsForLoad.connect(self._unblockTabsForLoad)
        self.tabs.currentChanged[int].connect(self._tabChanged)
        self.fileForm.fileError[str].connect(self._showFileError)
        self.fileForm.blockTabsForLoad.connect(self._blockTabsForLoad)
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
        self.processScans.blockTabsForProcess.connect(self._blockTabsForProcess)
        self.processScans.unblockTabsForProcess.connect( \
            self._unblockTabsForProcess)
        logger.debug(METHOD_EXIT_STR)
        
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
        message = qtWidgets.QMessageBox()
        message.warning(self, \
                            "Load Scan File Warning", \
                             str(error))
        self.fileForm.setScanLoadOK.emit()
              
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
    qtWidgets.QApplication.closeAllWindows()
    
if __name__ == "__main__":
    #This line allows CTRL_C to work with PyQt.
    logger.debug(METHOD_ENTER_STR)
    signal.signal(signal.SIGINT, ctrlCHandler)
    app = qtWidgets.QApplication(sys.argv)
    mainForm = MainDialog()
    mainForm.show()
    #timer allows Python interupts to work
    timer = qtCore.QTimer()
    timer.start(1000)
    timer.timeout.connect(lambda: None)
    app.exec_()

