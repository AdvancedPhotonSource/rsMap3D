'''
 Copyright (c) 2016, UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
from rsMap3D.gui.qtsignalstrings import CURRENT_INDEX_CHANGED_SIGNAL
from PyQt4.Qt import QComboBox
from rsMap3D.gui.rsmap3dsignals import PROCESS_ERROR_SIGNAL, \
    PROCESS_SIGNAL, CANCEL_PROCESS_SIGNAL, \
    BLOCK_TABS_FOR_PROCESS_SIGNAL, SET_PROCESS_CANCEL_OK_SIGNAL,\
    UNBLOCK_TABS_FOR_PROCESS_SIGNAL, SET_PROCESS_RUN_OK_SIGNAL,\
    OUTPUT_FORM_CHANGED
from rsMap3D.mappers.abstractmapper import ProcessCanceledException
import traceback
from rsMap3D.exception.rsmap3dexception import RSMap3DException
import logging
   
class ProcessScansController(qtGui.QDialog):
    '''
    '''
    
    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(ProcessScansController, self).__init__(parent)
        
        self.parent = parent
        self.Mapper = None
        self.layout = qtGui.QVBoxLayout()
        self.outputForms = []
        # Build a list of forms return Combo box for the selections and 
        # list of names
        self.outputFormSelection, self.outputForms = self.buildFormList()
        controlLayout = qtGui.QHBoxLayout()
        label = qtGui.QLabel('Output To:')
        
        self.outputFormSelection = QComboBox()
        for form in self.outputForms:
            self.outputFormSelection.addItem(form.FORM_TITLE)
        
        controlLayout.addWidget(label)
        controlLayout.addWidget(self.outputFormSelection)
        self.layout.addLayout(controlLayout)

        self.formLayout = qtGui.QHBoxLayout()
        self.outputFormWidget = self.outputForms[0].createInstance()
        self.formLayout.addWidget(self.outputFormWidget)
        self.layout.addLayout(self.formLayout)
        self.setLayout(self.layout)
        
        self._connectSignals()

    def buildFormList(self):
        del self.outputForms[:]
        self.outputForms = self.parent.getOutputForms()
        outputFormSelection = QComboBox()
        for form in self.outputForms:
            outputFormSelection.addItem(form.FORM_TITLE)
        return outputFormSelection, self.outputForms
        
    def _connectSignals(self):
        self.connect(self.outputFormSelection, 
                     qtCore.SIGNAL(CURRENT_INDEX_CHANGED_SIGNAL),
                     self._selectedTypeChanged)
        self.connect(self.outputFormWidget,
                     qtCore.SIGNAL(PROCESS_SIGNAL),
                     self._spawnProcessThread)
        self.connect(self.outputFormWidget,
                     qtCore.SIGNAL(CANCEL_PROCESS_SIGNAL),
                     self._stopMapper)
        self.connect(self, \
                     qtCore.SIGNAL(SET_PROCESS_RUN_OK_SIGNAL), \
                     self.setRunOK)
        self.connect(self, \
                     qtCore.SIGNAL(SET_PROCESS_CANCEL_OK_SIGNAL), \
                     self.setCancelOK)
        self.connect(self.outputFormWidget,
                     qtCore.SIGNAL(PROCESS_ERROR_SIGNAL),
                     self._processFormError)
        
        
    def _disconnectSignals(self):
        self.disconnect(self.outputFormWidget, 
                     qtCore.SIGNAL(CURRENT_INDEX_CHANGED_SIGNAL),
                     self._selectedTypeChanged)
        self.disconnect(self.outputFormWidget,
                     qtCore.SIGNAL(PROCESS_SIGNAL),
                     self._spawnProcessThread)
        self.disconnect(self.outputFormWidget,
                     qtCore.SIGNAL(CANCEL_PROCESS_SIGNAL),
                     self._stopMapper)
        self.disconnect(self, \
                     qtCore.SIGNAL(SET_PROCESS_RUN_OK_SIGNAL), \
                     self.setRunOK)
        self.disconnect(self, \
                     qtCore.SIGNAL(SET_PROCESS_CANCEL_OK_SIGNAL), \
                     self.setCancelOK)
        self.disconnect(self.outputFormWidget,
                     qtCore.SIGNAL(PROCESS_ERROR_SIGNAL),
                     self._processFormError)
        
    def _processFormError(self, message):
        logging.error ("ProcessScanController._processFormError " + message)
        
    def runMapper(self):
        logging.debug("Entering processScanController.runMapper")
        self.emit(qtCore.SIGNAL(BLOCK_TABS_FOR_PROCESS_SIGNAL))
        self.emit(qtCore.SIGNAL(SET_PROCESS_CANCEL_OK_SIGNAL))
        try:
            self.outputFormWidget.runMapper(self.parent.getDataSource(),
                                        self.parent.getTransform())
        except ProcessCanceledException:
            self.emit(qtCore.SIGNAL(UNBLOCK_TABS_FOR_PROCESS_SIGNAL))
            self.parent.getDataSource().resetHaltMap()
        except RSMap3DException as e:
            self.emit(qtCore.SIGNAL(PROCESS_ERROR_SIGNAL), \
                      str(e) + "\n" + str(traceback.format_exc()))
            return
        except Exception as e:
            self.emit(qtCore.SIGNAL(PROCESS_ERROR_SIGNAL), \
                      str(e) + "\n" + str(traceback.format_exc()))
            return
        self.emit(qtCore.SIGNAL(SET_PROCESS_RUN_OK_SIGNAL))
        self.emit(qtCore.SIGNAL(UNBLOCK_TABS_FOR_PROCESS_SIGNAL))
        logging.debug("Leaving processScanController.runMapper")
        
    def _selectedTypeChanged(self, typeStr):
        logging.debug("ProcessScanController::_SelectedType " +
          "Changed updating widget to " 
          + str(typeStr))
        self._disconnectSignals()
        self.formLayout.removeWidget(self.outputFormWidget)
        self.outputFormWidget.deleteLater()
        
        for form in self.outputForms:
            if typeStr == form.FORM_TITLE:
                logging.debug("typeStr:" +str(typeStr) + " class " + form.__name__)
                self.outputFormWidget = form.createInstance()
                
        self.formLayout.addWidget(self.outputFormWidget)
        self._connectSignals()
        self.emit(qtCore.SIGNAL(OUTPUT_FORM_CHANGED))
        self.update()
        
    def setCancelOK(self):
        self.outputFormWidget.setCancelOK()
        
    def setRunOK(self):
        self.outputFormWidget.setRunOK()
        
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
        logging.debug ("Setting output form to " + str(self.outputForms[0].FORM_TITLE))
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
