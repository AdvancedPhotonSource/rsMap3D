'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets

from  PyQt5.QtCore import pyqtSignal as Signal
from  PyQt5.QtCore import pyqtSlot as Slot

from rsMap3D.gui.rsmap3dsignals import BLOCK_TABS_FOR_PROCESS_SIGNAL, \
    SET_PROCESS_CANCEL_OK_SIGNAL,\
    UNBLOCK_TABS_FOR_PROCESS_SIGNAL, SET_PROCESS_RUN_OK_SIGNAL,\
    OUTPUT_FORM_CHANGED, PROCESS_ERROR_SIGNAL
from rsMap3D.mappers.abstractmapper import ProcessCanceledException
import traceback
from rsMap3D.exception.rsmap3dexception import RSMap3DException
import logging
from PyQt5.uic.Compiler.qtproxies import QtWidgets
logger = logging.getLogger(__name__)

class ProcessScansController(qtWidgets.QDialog):
    '''
    '''
    setProcessRunOK = Signal(name=SET_PROCESS_RUN_OK_SIGNAL)
    setProcessCancelOK = Signal(name=SET_PROCESS_CANCEL_OK_SIGNAL)
    blockTabsForProcess = Signal(name=BLOCK_TABS_FOR_PROCESS_SIGNAL)
    unblockTabsForProcess = Signal(name=UNBLOCK_TABS_FOR_PROCESS_SIGNAL)
    outputFormChanged = Signal(name=OUTPUT_FORM_CHANGED)
    processError = Signal(str, name=PROCESS_ERROR_SIGNAL)
    
    def __init__(self, parent=None, appConfig=None):
        '''
        Constructor
        '''
        super(ProcessScansController, self).__init__(parent)
        
        self.parent = parent
        self.appConfig = appConfig
        self.Mapper = None
        self.layout = qtWidgets.QVBoxLayout()
        self.outputForms = []
        # Build a list of forms return Combo box for the selections and 
        # list of names
        self.outputFormSelection, self.outputForms = self.buildFormList()
        controlLayout = qtWidgets.QHBoxLayout()
        label = qtWidgets.QLabel('Output To:')
        
        self.outputFormSelection = qtWidgets.QComboBox()
        for form in self.outputForms:
            self.outputFormSelection.addItem(form.FORM_TITLE)
        
        controlLayout.addWidget(label)
        controlLayout.addWidget(self.outputFormSelection)
        self.layout.addLayout(controlLayout)

        self.formLayout = qtWidgets.QHBoxLayout()
        self.outputFormWidget = self.outputForms[0].createInstance(appConfig= \
                                                            self.appConfig)
        self.formLayout.addWidget(self.outputFormWidget)
        self.layout.addLayout(self.formLayout)
        self.setLayout(self.layout)
        
        self._connectSignals()

    def buildFormList(self):
        del self.outputForms[:]
        self.outputForms = self.parent.getOutputForms()
        outputFormSelection = qtWidgets.QComboBox()
        for form in self.outputForms:
            outputFormSelection.addItem(form.FORM_TITLE)
        return outputFormSelection, self.outputForms
        
    def _connectSignals(self):
        self.outputFormSelection.currentIndexChanged[str].connect(
            self._selectedTypeChanged)
        self.outputFormWidget.process.connect(self._spawnProcessThread)
        self.outputFormWidget.cancel.connect(self._stopMapper)
        self.setProcessRunOK.connect(self.setRunOK)
        self.setProcessCancelOK.connect(self.setCancelOK)
        self.processError[str].connect(self._processFormError)
        
        
    def _disconnectSignals(self):
        self.outputFormSelection.currentIndexChanged[str].disconnect(
            self._selectedTypeChanged)
        self.outputFormWidget.process.disconnect(self._spawnProcessThread)
        self.outputFormWidget.cancel.disconnect(self._stopMapper)
        self.setProcessRunOK.disconnect(self.setRunOK)
        self.setProcessCancelOK.disconnect(self.setCancelOK)
        self.processError[str].disconnect(self._processFormError)
        
    @Slot(str)
    def _processFormError(self, message):
        messageBox = qtWidgets.QMessageBox()
        messageBox.warning(self, \
                            "Processing Scan File Warning", \
                             str(message))
        self.setProcessRunOK.emit()
        logger.error ("ProcessScanController._processFormError " + str(message))
        
    def runMapper(self):
        logger.debug("Entering processScanController.runMapper")
        self.blockTabsForProcess.emit()
        self.setProcessCancelOK.emit()
        try:
            self.outputFormWidget.runMapper(self.parent.getDataSource(),
                                        self.parent.getTransform())
        except ProcessCanceledException:
            self.unblockTabsForProcess.emit()
            self.parent.getDataSource().resetHaltMap()
        except RSMap3DException as e:
            self.processError.emit(str(e) + "\n" + str(traceback.format_exc()))
            return
        except Exception as e:
            self.processError.emit(str(e) + "\n" + str(traceback.format_exc()))
            return
        self.setProcessRunOK.emit()
        self.unblockTabsForProcess.emit()
        logger.debug("Leaving processScanController.runMapper")
        
    @Slot(str)
    def _selectedTypeChanged(self, typeStr):
        logger.debug("ProcessScanController::_SelectedType " +
          "Changed updating widget to " 
          + str(typeStr))
        self._disconnectSignals()
        self.formLayout.removeWidget(self.outputFormWidget)
        self.outputFormWidget.deleteLater()
        
        for form in self.outputForms:
            if typeStr == form.FORM_TITLE:
                logger.debug("typeStr:" +str(typeStr) + " class " + str(form.__name__))
                self.outputFormWidget = form.createInstance(appConfig = \
                                                            self.appConfig)
                
        self.formLayout.addWidget(self.outputFormWidget)
        self._connectSignals()
        self.outputFormChanged.emit()
        self.update()
        
    @Slot()
    def setCancelOK(self):
        self.outputFormWidget.setCancelOK()
        
    @Slot()
    def setRunOK(self):
        self.outputFormWidget.setRunOK()
        
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
              
    @Slot()
    def _spawnProcessThread(self):
        '''
        Spawn a new thread to load the scan so that scan may be canceled later 
        and so that this does not interfere with the GUI operation.
        '''
        self.outputFormWidget.setProgressLimits(0, 
                                len(self.parent.getDataSource().getAvailableScans())*100)
        self.outputFormWidget.setProgress(0)
        self.setCancelOK()
        self.processThread = ProcessScanThread(self, 
                                               self.parent.getDataSource(),  
                                               self.parent.getTransform(),
                                               parent=None)
        self.processThread.start()

    @Slot()
    def _stopMapper(self):
        '''
        Tell the processScans tab to stop the mapper.
        '''
        self.outputFormWidget.stopMapper()
        
    def updateOutputForms(self, newForms):
        del self.outputForms[:]
        self.outputForms = newForms
        self.outputFormSelection.clear()
        
        for form in self.outputForms:
            self.outputFormSelection.addItem(form.FORM_TITLE)
        logger.debug ("Setting output form to " + str(self.outputForms[0].FORM_TITLE))
        self._selectedTypeChanged(self.outputForms[0].FORM_TITLE)
        self.update()
        
        
class ProcessScanThread(qtCore.QThread):
    '''
    Small thread class to launch data processing
    '''
    def __init__(self, controller,dataSource, transform, **kwargs):
        super(ProcessScanThread, self).__init__( **kwargs)
        self.controller = controller

    def run(self):
        self.controller.runMapper()
