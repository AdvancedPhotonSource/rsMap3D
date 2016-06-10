'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
USE_XPCS = False
import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
from rsMap3D.gui.fileform import FileForm
from rsMap3D.gui.qtsignalstrings import CURRENT_INDEX_CHANGED_SIGNAL
from rsMap3D.gui.input.s34hdfescanfileform import S34HDFEScanFileForm
from rsMap3D.gui.rsmap3dsignals import LOAD_FILE_SIGNAL, CANCEL_LOAD_FILE_SIGNAL,\
    SET_SCAN_LOAD_CANCEL_SIGNAL, SET_SCAN_LOAD_OK_SIGNAL,\
    BLOCK_TABS_FOR_LOAD_SIGNAL, FILE_ERROR_SIGNAL,\
    LOAD_DATASOURCE_TO_SCAN_FORM_SIGNAL
from rsMap3D.datasource.Sector33SpecDataSource import LoadCanceledException
from rsMap3D.exception.rsmap3dexception import ScanDataMissingException,\
    DetectorConfigException, InstConfigException, Transform3DException,\
    RSMap3DException
import traceback
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.transforms.polemaptransform3d import PoleMapTransform3D
try:
    from rsMap3D.gui.input.xpcsspecscanfileform import XPCSSpecScanFileForm
    USE_XPCS = True
except:
    USE_XPCS = False

class FileInputController(qtGui.QDialog):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(FileInputController, self).__init__(parent)
        self.layout = qtGui.QVBoxLayout()
        self.S33SPECXML = "Sector 33 Spec/XML Setup"
        self.S34HDFXML = "Sector 34 HDF/XML Setup"
        self.XPCSSPECXML = "XPCS SPEC/XML Setup"

        controlLayout = qtGui.QHBoxLayout()
        label = qtGui.QLabel("Input from:")
        self.formSelection = qtGui.QComboBox()
        self.formSelection.addItem(self.S33SPECXML)
        self.formSelection.addItem(self.S34HDFXML)
        if (USE_XPCS):
            self.formSelection.addItem(self.XPCSSPECXML)
        controlLayout.addWidget(label)
        controlLayout.addWidget(self.formSelection)
        self.layout.addLayout(controlLayout)
        
        self.formLayout = qtGui.QHBoxLayout()
        self.fileFormWidget = FileForm()
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
        self.connect(self.formSelection, \
                     qtCore.SIGNAL(CURRENT_INDEX_CHANGED_SIGNAL), \
                     self._selectedTypeChanged)
        self.connect(self.fileFormWidget, \
                     qtCore.SIGNAL(LOAD_FILE_SIGNAL), \
                     self._spawnLoadThread)
        self.connect(self.fileFormWidget, \
                     qtCore.SIGNAL(CANCEL_LOAD_FILE_SIGNAL), \
                     self._cancelLoadThread)
        self.connect(self, \
                     qtCore.SIGNAL(SET_SCAN_LOAD_OK_SIGNAL), \
                     self.fileFormWidget.setLoadOK)
        self.connect(self, \
                     qtCore.SIGNAL(SET_SCAN_LOAD_CANCEL_SIGNAL), \
                     self.fileFormWidget.setCancelOK)
        
    def _disconnectSignals(self):
        self.disconnect(self.formSelection, \
                     qtCore.SIGNAL(CURRENT_INDEX_CHANGED_SIGNAL), \
                     self._selectedTypeChanged)
        self.disconnect(self.fileFormWidget, \
                     qtCore.SIGNAL(LOAD_FILE_SIGNAL), \
                     self._spawnLoadThread)
        self.disconnect(self.fileFormWidget, \
                     qtCore.SIGNAL(CANCEL_LOAD_FILE_SIGNAL), \
                     self._cancelLoadThread)
        self.disconnect(self, \
                     qtCore.SIGNAL(SET_SCAN_LOAD_OK_SIGNAL), \
                     self.fileFormWidget.setLoadOK)
        self.disconnect(self, \
                     qtCore.SIGNAL(SET_SCAN_LOAD_CANCEL_SIGNAL), \
                     self.fileFormWidget.setCancelOK)
        
    def loadScanFile(self):
        '''
        Set up to load the scan file
        '''
        self.emit(qtCore.SIGNAL(BLOCK_TABS_FOR_LOAD_SIGNAL))
        if self.fileFormWidget.getOutputType() == self.fileFormWidget.SIMPLE_GRID_MAP_STR:
            self.transform = UnityTransform3D()
        elif self.fileFormWidget.getOutputType() == self.fileFormWidget.POLE_MAP_STR:
            self.transform = \
                PoleMapTransform3D(projectionDirection=\
                                   self.fileForm.getProjectionDirection())
        else:
            self.transform = None
            
             
        try:
            self.dataSource = \
                self.fileFormWidget.getDataSource()
        except LoadCanceledException as e:
            self.emit(qtCore.SIGNAL(BLOCK_TABS_FOR_LOAD_SIGNAL))
            self.emit(qtCore.SIGNAL(SET_SCAN_LOAD_OK_SIGNAL))
            #self.fileForm.setLoadOK()
            return
        except ScanDataMissingException as e:
            self.emit(qtCore.SIGNAL(FILE_ERROR_SIGNAL), str(e))
            return
        except DetectorConfigException as e:
            self.emit(qtCore.SIGNAL(FILE_ERROR_SIGNAL), str(e))
            return
        except InstConfigException as e:
            self.emit(qtCore.SIGNAL(FILE_ERROR_SIGNAL), str(e))
            return
        except Transform3DException as e:
            self.emit(qtCore.SIGNAL(FILE_ERROR_SIGNAL), str(e))
            return 
        except ScanDataMissingException as e:
            self.emit(qtCore.SIGNAL(FILE_ERROR_SIGNAL), str(e))
            return
        except RSMap3DException as e:
            self.emit(qtCore.SIGNAL(FILE_ERROR_SIGNAL), str(e))
            return
        except Exception as e:
            self.emit(qtCore.SIGNAL(FILE_ERROR_SIGNAL), \
                      str(e)  + "\n" + str(traceback.format_exc()))
            return
        
            
        self.emit(qtCore.SIGNAL(LOAD_DATASOURCE_TO_SCAN_FORM_SIGNAL))
        self.emit(qtCore.SIGNAL(SET_SCAN_LOAD_OK_SIGNAL))
        
    def _selectedTypeChanged(self, typeStr):
        self._disconnectSignals()
        self.formLayout.removeWidget(self.fileFormWidget)
        self.fileFormWidget.deleteLater()

        if typeStr == self.S33SPECXML:
            self.fileFormWidget = FileForm()
        elif typeStr == self.S34HDFXML:
            self.fileFormWidget = S34HDFEScanFileForm()
        elif typeStr == self.XPCSSPECXML and USE_XPCS:
            self.fileFormWidget = XPCSSpecScanFileForm()

        self.formLayout.addWidget(self.fileFormWidget)
        self._connectSignals()
        self.update()
            
    def setLoadOK(self):
        self.fileFormWidget.setLoadOK()
    
    def setCancelOK(self):
        self.fileFormWidget.setCancelOK()
    
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
        print("LoadScanThread Running")
        self.controller.loadScanFile()
        
