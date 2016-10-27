'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
from rsMap3D.gui.output.processvtioutputform import ProcessVTIOutputForm
from rsMap3D.gui.output.processxpcsgridlocationform import ProcessXpcsGridLocationForm

try:
    from rsMap3D.datasource.xpcsspecdatasource import XPCSSpecDataSource
except ImportError as ex:
    raise ex
from rsMap3D.transforms.polemaptransform3d import PoleMapTransform3D
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.gui.input.specxmldrivenfileform import SpecXMLDrivenFileForm
from rsMap3D.gui.rsm3dcommonstrings import BROWSE_STR, EMPTY_STR, WARNING_STR
from rsMap3D.gui.qtsignalstrings import CLICKED_SIGNAL, EDIT_FINISHED_SIGNAL
import os


XPCS_FILE_DIALOG_TITLE = "XPCS File Input"
XPCS_FILE_FILTER = "*.imm"


class XPCSSpecScanFileForm(SpecXMLDrivenFileForm):
    '''
    '''
    FORM_TITLE = "XPCS SPEC/XML Setup"
    
    DET_ROI_REGEXP_1 =  "^(\d*,*)+$"
    DET_ROI_REGEXP_2 =  "^(\d)+,(\d)+,(\d)+,(\d)+$"
    SCAN_LIST_REGEXP = "((\d)+(-(\d)+)?\,( )?)+"

    @staticmethod
    def createInstance(parent=None):
        return XPCSSpecScanFileForm(parent)
    
    def __init__(self, parent=None):
        super(XPCSSpecScanFileForm, self).__init__(parent)

        self.imageFileDialogFilter = XPCS_FILE_FILTER
        
    def _browseForXPCSFile(self):
        if self.xpcsDataFileTxt.text() == EMPTY_STR:
            fileName = qtGui.QFileDialog.getOpenFileName(None, \
                                                   XPCS_FILE_DIALOG_TITLE, \
                                                   filter=XPCS_FILE_FILTER)
        else:
            fileDirectory = os.path.dirname(str(self.xpcsDataFileTxt.text()))
            fileName = qtGui.QFileDialog.getOpenFileName(None,\
                                                   XPCS_FILE_FILTER, \
                                                   directory = fileDirectory,
                                                   filter=XPCS_FILE_FILTER)
            
        if fileName != EMPTY_STR:
            self.xpcsDataFileTxt.setText(fileName)
            self.xpcsDataFileTxt.emit(qtCore.SIGNAL(EDIT_FINISHED_SIGNAL))
    
    def _createDataBox(self):
        dataBox = super(XPCSSpecScanFileForm, self)._createDataBox()
        dataLayout = dataBox.layout()
        #grab present row count so we can add to the end.
        row = dataLayout.rowCount()
        self._createInstConfig(dataLayout, row)

        row = dataLayout.rowCount() + 1
        self._createDetConfig(dataLayout, row)

        row = dataLayout.rowCount() + 1
        self._createDetectorROIInput(dataLayout, row)
        
        row = dataLayout.rowCount() + 1
        self._createScanNumberInput(dataLayout, row)
            
        row = dataLayout.rowCount() + 1
        self._createOutputType(dataLayout, row)

        row = dataLayout.rowCount() + 1
        self._createHKLOutput(dataLayout, row)

        row = dataLayout.rowCount() + 1
        label = qtGui.QLabel("XPCS Data:")
        self.xpcsDataFileTxt = qtGui.QLineEdit()
        self.xpcsBrowseButton = qtGui.QPushButton(BROWSE_STR)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.xpcsDataFileTxt, row, 1)
        dataLayout.addWidget(self.xpcsBrowseButton, row, 2)
        
        self.connect(self.xpcsBrowseButton,
                     qtCore.SIGNAL(CLICKED_SIGNAL),
                     self._browseForXPCSFile)
        self.connect(self.xpcsDataFileTxt,
                     qtCore.SIGNAL(EDIT_FINISHED_SIGNAL),
                     self._xpcsFileNameChanged)
        
        dataBox.setLayout(dataLayout)
        return dataBox

    def getDataSource(self):
        if self.getOutputType() == self.SIMPLE_GRID_MAP_STR:
            self.transform = UnityTransform3D()
        elif self.getOutputType() == self.POLE_MAP_STR:
            self.transform = \
                PoleMapTransform3D(projectionDirection=\
                                   self.fileForm.getProjectionDirection())
        else:
            self.transform = None
            
        self.dataSource = \
            XPCSSpecDataSource(str(self.getProjectDir()), \
                                   str(self.getProjectName()), \
                                   str(self.getProjectExtension()), \
                                   str(self.getInstConfigName()), \
                                   str(self.getDetConfigName()), \
                                   str(self.getImmFileName()), \
                                   scanList = self.getScanList(), \
                                   transform = self.transform, \
                                  )
        self.dataSource.setProgressUpdater(self.updateProgress)
        self.dataSource.setCurrentDetector(self.currentDetector)
        self.dataSource.loadSource(mapHKL = self.getMapAsHKL())
        return self.dataSource
        

    def getImmFileName(self):
        '''
        Return the IMM file name with XPCS images
        '''
        return str(self.xpcsDataFileTxt.text())
    
    def getOutputForms(self):
        outputForms = []
        outputForms.append(ProcessXpcsGridLocationForm)
        outputForms.append(ProcessVTIOutputForm)
        return outputForms

    def _xpcsFileNameChanged(self):
        if os.path.isfile(self.xpcsDataFileTxt.text()) or \
            self.xpcsDataFileTxt.text() == EMPTY_STR:
            self.checkOkToLoad()
        else:
            message = qtGui.QMessageBox()
            message.warning(self, \
                             WARNING_STR
                             , \
                             "The IMM file entered is invalid")
