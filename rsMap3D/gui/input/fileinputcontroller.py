'''
Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
USE_XPCS = False
import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
from rsMap3D.gui.qtsignalstrings import CURRENT_INDEX_CHANGED_SIGNAL
from rsMap3D.gui.rsmap3dsignals import LOAD_FILE_SIGNAL, CANCEL_LOAD_FILE_SIGNAL,\
    SET_SCAN_LOAD_CANCEL_SIGNAL, SET_SCAN_LOAD_OK_SIGNAL,\
    BLOCK_TABS_FOR_LOAD_SIGNAL, FILE_ERROR_SIGNAL,\
    LOAD_DATASOURCE_TO_SCAN_FORM_SIGNAL, INPUT_FORM_CHANGED
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
try:
    from rsMap3D.gui.input.xpcsspecscanfileform import XPCSSpecScanFileForm
    USE_XPCS = True

except Exception as ex:
    print ex
    traceback.print_exc()
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
        #Build a list of fileForms
        self.fileForms = []
        self.fileForms.append(S33SpecScanFileForm)
        self.fileForms.append(S34HDFEScanFileForm)
        if USE_XPCS:
            self.fileForms.append(XPCSSpecScanFileForm)
            
        controlLayout = qtGui.QHBoxLayout()
        label = qtGui.QLabel("Input from:")
        #populate selection list with available forms.
        self.formSelection = qtGui.QComboBox()
        for form in self.fileForms:
            self.formSelection.addItem(form.FORM_TITLE)
        self.formSelection.setCurrentIndex(0)   
        controlLayout.addWidget(label)
        controlLayout.addWidget(self.formSelection)
        
        self.layout.addLayout(controlLayout)
        
        self.formLayout = qtGui.QHBoxLayout()
        self.fileFormWidget = self.fileForms[0].createInstance()
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
        
    def getOutputForms(self):
        '''
        return the output forms associated with the current file form.
        '''
        return self.fileFormWidget.getOutputForms()
    
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
                                   self.fileFormWidget.getProjectionDirection())
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

        for form in self.fileForms:
            if typeStr == form.FORM_TITLE:
                self.fileFormWidget = form.createInstance()
#         elif typeStr == S34HDFEScanFileForm.FORM_TITLE:
#             self.fileFormWidget = S34HDFEScanFileForm.createInstance()
#         elif typeStr == XPCSSpecScanFileForm.FORM_TITLE and USE_XPCS:
#             self.fileFormWidget = XPCSSpecScanFileForm.createInstance()

        self.formLayout.addWidget(self.fileFormWidget)
        self._connectSignals()
        self.emit(qtCore.SIGNAL(INPUT_FORM_CHANGED))
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