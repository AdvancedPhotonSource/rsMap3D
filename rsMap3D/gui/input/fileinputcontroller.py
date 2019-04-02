'''
Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
USE_XPCS = False
import logging
logger = logging.getLogger(__name__)
import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets
from rsMap3D.gui.rsmap3dsignals import BLOCK_TABS_FOR_LOAD_SIGNAL, \
    FILE_ERROR_SIGNAL, LOAD_DATASOURCE_TO_SCAN_FORM_SIGNAL, INPUT_FORM_CHANGED
from rsMap3D.datasource.Sector33SpecDataSource import LoadCanceledException
from rsMap3D.exception.rsmap3dexception import ScanDataMissingException,\
    DetectorConfigException, InstConfigException, Transform3DException,\
    RSMap3DException
import traceback
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.transforms.polemaptransform3d import PoleMapTransform3D
# Input forms Looking for a way to set these up.
from rsMap3D.gui.input.s33specscanfileform import S33SpecScanFileForm
from rsMap3D.gui.input.s34hdfescanfileform import S34HDFEScanFileForm
from rsMap3D.gui.input.s1highenergydiffractionform import S1HighEnergyDiffractionForm
try:
    from rsMap3D.gui.input.xpcsspecscanfileform import XPCSSpecScanFileForm
    USE_XPCS = True

except Exception as ex:
    logger.debug( ex)
    traceback.print_exc()
    USE_XPCS = False

class FileInputController(qtWidgets.QDialog):
    '''
    classdocs
    '''
    #define qtSignals to be used here
    setScanLoadOK = qtCore.pyqtSignal()
    setScanLoadCancelOK = qtCore.pyqtSignal()
    fileErrorSignal = qtCore.pyqtSignal(str, name=FILE_ERROR_SIGNAL)
    blockTabsForLoad = qtCore.pyqtSignal(name=BLOCK_TABS_FOR_LOAD_SIGNAL)
    loadDataSourceToScanForm = qtCore.pyqtSignal(
                name = LOAD_DATASOURCE_TO_SCAN_FORM_SIGNAL)
    inputFormChanged = qtCore.pyqtSignal(name = INPUT_FORM_CHANGED)
    
    def __init__(self, parent=None, appConfig=None):
        '''
        Constructor
        '''
        super(FileInputController, self).__init__(parent)
        self.appConfig = None
        if not (appConfig is None):
            self.appConfig = appConfig
        else:
            raise RSMap3DException("FileInputController recieved no AppConfig" +\
                                   "object.")
        self.layout = qtWidgets.QVBoxLayout()
        #Build a list of fileForms
        self.fileForms = []
        self.fileForms.append(S33SpecScanFileForm)
        self.fileForms.append(S34HDFEScanFileForm)
        self.fileForms.append(S1HighEnergyDiffractionForm)
        if USE_XPCS:
            self.fileForms.append(XPCSSpecScanFileForm)
            
        controlLayout = qtWidgets.QHBoxLayout()
        label = qtWidgets.QLabel("Input from:")
        #populate selection list with available forms.
        self.formSelection = qtWidgets.QComboBox()
        for form in self.fileForms:
            self.formSelection.addItem(form.FORM_TITLE)
        self.formSelection.setCurrentIndex(0)   
        controlLayout.addWidget(label)
        controlLayout.addWidget(self.formSelection)
        
        self.layout.addLayout(controlLayout)
        
        self.formLayout = qtWidgets.QHBoxLayout()
        self.fileFormWidget = self.fileForms[0].createInstance(appConfig=\
                                                               self.appConfig)
        #print dir(self.fileFormWidget)
        self.formLayout.addWidget(self.fileFormWidget)
        self.layout.addLayout(self.formLayout)
        self.setLayout(self.layout)

        self._connectSignals()

    def _cancelLoadThread(self):
        '''
        Let the data source know that a cancel has been requested.
        '''
        self.fileFormWidget.dataSource.signalCancelLoadSource()
        
    def _connectSignals(self):
        self.formSelection.currentIndexChanged[str].\
            connect(self._selectedTypeChanged)
        self.fileFormWidget.loadFile.connect(self._spawnLoadThread)
        self.fileFormWidget.cancelLoadFile.connect(self._cancelLoadThread)
        self.setScanLoadOK.connect(self.fileFormWidget.setLoadOK)
        self.setScanLoadCancelOK.connect(self.fileFormWidget.setCancelOK)
        
    def _disconnectSignals(self):
        self.formSelection.currentIndexChanged[str].\
            disconnect(self._selectedTypeChanged)
        self.fileFormWidget.loadFile.disconnect(self._spawnLoadThread)
        self.fileFormWidget.cancelLoadFile.disconnect(self._cancelLoadThread)
        self.setScanLoadOK.disconnect(self.fileFormWidget.setLoadOK)
        self.setScanLoadCancelOK.disconnect(self.fileFormWidget.setCancelOK)
        
    def getOutputForms(self):
        '''
        return the output forms associated with the current file form.
        '''
        return self.fileFormWidget.getOutputForms()
    
    def loadScanFile(self):
        '''
        Set up to load the scan file
        '''
        self.blockTabsForLoad.emit()
        if self.fileFormWidget.getOutputType() == self.fileFormWidget.SIMPLE_GRID_MAP_STR:
            self.transform = UnityTransform3D()
        elif self.fileFormWidget.getOutputType() == self.fileFormWidget.POLE_MAP_STR:
            self.transform = \
                PoleMapTransform3D(projectionDirection=\
                                   self.fileFormWidget.getProjectionDirection())
        else:
            self.transform = None
            
             
        try:
            self.dataSource = \
                self.fileFormWidget.getDataSource()
        except LoadCanceledException as e:
            self.blockTabsForLoad.emit()
            self.setScanLoadOK.emit()
            #self.fileForm.setLoadOK()
            return
        except ScanDataMissingException as e:
            self.fileError.emit(str(e))
            return
        except DetectorConfigException as e:
            self.fileError.emit(str(e))
            return
        except InstConfigException as e:
            self.fileError.emit(str(e))
            return
        except Transform3DException as e:
            self.fileError.emit(str(e))
            return 
        except ScanDataMissingException as e:
            self.fileError.emit(str(e))
            return
        except RSMap3DException as e:
            self.fileError.emit(str(e))
            return
        except Exception as e:
            self.fileError.emit(str(e)  + "\n" + str(traceback.format_exc()))
            return
        
            
        self.loadDataSourceToScanForm.emit()
        self.setScanLoadOK.emit()
        
    @qtCore.pyqtSlot(str)
    def _selectedTypeChanged(self, typeStr):
        self._disconnectSignals()
        self.formLayout.removeWidget(self.fileFormWidget)
        self.fileFormWidget.deleteLater()

        for form in self.fileForms:
            if typeStr == form.FORM_TITLE:
                self.fileFormWidget = form.createInstance(appConfig= \
                                                          self.appConfig)

        self.formLayout.addWidget(self.fileFormWidget)
        self._connectSignals()
        self.inputFormChanged.emit()
        self.update()
            
#     def setLoadOK(self):
#         self.fileFormWidget.setLoadOK()
#     
#     def setCancelOK(self):
#         self.fileFormWidget.setCancelOK()
    
    def _spawnLoadThread(self):
        '''
        Spawn a new thread to load the scan so that scan may be canceled later 
        and so that this does not interfere with the GUI operation.
        '''
        self.fileFormWidget.setCancelOK()
        self.loadThread = LoadScanThread(self, parent=None)
        self.loadThread.start()
        

class LoadScanThread(qtCore.QThread):
    '''
    Small thread class to launch the scan loading process
    '''
    def __init__(self, controller, **kwargs):
        super(LoadScanThread, self).__init__( **kwargs)
        self.controller = controller
        
    def run(self):
        self.controller.loadScanFile()