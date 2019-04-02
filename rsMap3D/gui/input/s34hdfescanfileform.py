'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import os.path
import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets

from rsMap3D.gui.input.abstractimageperfileview import AbstractImagePerFileView
from rsMap3D.gui.rsm3dcommonstrings import BROWSE_STR, EMPTY_STR,\
     SELECT_DETECTOR_CONFIG_TITLE, DETECTOR_CONFIG_FILE_FILTER, WARNING_STR,\
    SELECT_HDF_FILE_TITLE, HDF_FILE_FILTER
from rsMap3D.datasource.sector34nexusescansource import Sector34NexusEscanSource
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.transforms.polemaptransform3d import PoleMapTransform3D
from rsMap3D.gui.output.processvtioutputform import ProcessVTIOutputForm

class S34HDFEScanFileForm(AbstractImagePerFileView):
    '''
    classdocs
    '''
    FORM_TITLE = "Sector 34 HDF/XML Setup"
    
    @staticmethod
    def createInstance(parent=None, appConfig=None):
        return S34HDFEScanFileForm(parent=parent, appConfig=appConfig)
        
    def __init__(self, **kwargs):
        '''
        Constructor
        '''
        super(S34HDFEScanFileForm, self).__init__(**kwargs)

        self.fileDialogTitle = SELECT_HDF_FILE_TITLE
        self.fileDialogFilter = HDF_FILE_FILTER

        self.dataBox = self._createDataBox()
        controlBox = self._createControlBox()
        
        self.layout.addWidget(self.dataBox)
        self.layout.addWidget(controlBox)
        self.setLayout(self.layout);

    @qtCore.pyqtSlot()
    def _browseForDetFile(self):
        '''
        Launch file selection dialog for Detector file.
        '''
        if self.detConfigTxt.text() == EMPTY_STR:
            fileName = qtWidgets.QFileDialog.getOpenFileName(None, \
                                            SELECT_DETECTOR_CONFIG_TITLE, \
                                            filter=DETECTOR_CONFIG_FILE_FILTER)[0]
        else:
            fileDirectory = os.path.dirname(str(self.detConfigTxt.text()))
            fileName = qtWidgets.QFileDialog.getOpenFileName(None, \
                                         SELECT_DETECTOR_CONFIG_TITLE, \
                                         filter=DETECTOR_CONFIG_FILE_FILTER, \
                                         directory = fileDirectory)[0]
        if fileName != EMPTY_STR:
            self.detConfigTxt.setText(fileName)
            self.detConfigTxt.editingFinished.emit()

    def checkOkToLoad(self):
        '''
        Make sure we have valid file names for project, instrument config, 
        and the detector config.  If we do enable load button.  If not disable
        the load button
        '''
        projFileOK = AbstractImagePerFileView.checkOkToLoad(self)
        if projFileOK and \
            os.path.isfile(self.detConfigTxt.text()):
            retVal = True
            self.loadButton.setEnabled(retVal)
        else:
            retVal = False
            self.loadButton.setDisabled(not retVal)
        self.okToLoad.emit(retVal)

        return retVal
    
    def _createDataBox(self):
        '''
        Create widgets for collecting data
        '''
        super(S34HDFEScanFileForm, self)._createDataBox()
        dataBox = super(S34HDFEScanFileForm, self)._createDataBox()
        dataLayout = dataBox.layout()

        row = dataLayout.rowCount() + 1
        label = qtWidgets.QLabel("Detector Config File:");
        self.detConfigTxt = qtWidgets.QLineEdit()
        self.detConfigFileButton = qtWidgets.QPushButton(BROWSE_STR)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.detConfigTxt, row, 1)
        dataLayout.addWidget(self.detConfigFileButton, row, 2)

#         row = dataLayout.rowCount() + 1
#         self._createDetectorROIInput(dataLayout, row, silent=True)
# 
#         row = dataLayout.rowCount() + 1
#         self._createNumberOfPixelsToAverage(dataLayout, row, silent=True)

        row = dataLayout.rowCount() + 1
        label = qtWidgets.QLabel("Output Type")
        self.outTypeChooser = qtWidgets.QComboBox()
        self.outTypeChooser.addItem(self.SIMPLE_GRID_MAP_STR)
        #self.outTypeChooser.addItem(self.POLE_MAP_STR)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.outTypeChooser, row, 1)
        
#         row = dataLayout.rowCount() + 1
#         self._createHKLOutput(dataLayout, row)


        dataBox.setLayout(dataLayout)
        
        # Add Signals between widgets
        self.detConfigFileButton.clicked.connect(self._browseForDetFile)
        self.detConfigTxt.editingFinished.connect(self._detConfigChanged)
        self.outTypeChooser.currentIndexChanged[str].\
            connect(self._outputTypeChanged)
        
        return dataBox

    @qtCore.pyqtSlot()
    def _detConfigChanged(self):
        '''
        '''
        if os.path.isfile(self.detConfigTxt.text()) or \
           self.detConfigTxt.text() == "":
            self.checkOkToLoad()
#             try:
#                 self.updateROIandNumAvg()
#             except DetectorConfigException:
#                 message = qtGui.QMessageBox()
#                 message.warning(self, \
#                                  WARNING_STR,\
#                                  "Trouble getting ROI or Num average " + \
#                                  "from the detector config file")
        else:
            message = qtWidgets.QMessageBox()
            message.warning(self, \
                             WARNING_STR,\
                             "The filename entered for the detector " + \
                             "configuration is invalid")
        
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
            Sector34NexusEscanSource(str(self.getProjectDir()), \
                                   str(self.getProjectName()), \
                                   str(self.getProjectExtension()), \
                                   str(self.getDetConfigName()), \
                                   appConfig = self.appConfig)
        self.dataSource.setProgressUpdater(self.updateProgress)
        self.dataSource.loadSource()
        return self.dataSource
    
    def getDetConfigName(self):
        '''
        Return the selected Detector Configuration file
        '''
        return self.detConfigTxt.text()

    def getOutputType(self):
        '''
        Get the output type to be used.
        '''
        return self.outTypeChooser.currentText()
    
    def getOutputForms(self):
        outputForms = []
        outputForms.append(ProcessVTIOutputForm)
        return outputForms

    @qtCore.pyqtSlot(str)
    def _outputTypeChanged(self, typeStr):
        '''
        If the output is selected to be a simple grid map type then allow
        the user to select HKL as an output.
        :param typeStr: String holding the outpu type
        '''
        pass
        #
#         if typeStr == self.SIMPLE_GRID_MAP_STR:
#             self.hklCheckbox.setEnabled(True)
#         else:
#             self.hklCheckbox.setDisabled(True)
#             self.hklCheckbox.setCheckState(False)
