'''
 Copyright (c) 2017 UChicago Argonne, LLC
 See LICENSE file.
'''
import logging
from rsMap3D.config.rsmap3dlogging import METHOD_ENTER_STR, METHOD_EXIT_STR
from rsMap3D.gui.rsm3dcommonstrings import EMPTY_STR, SAVE_FILE_STR, WARNING_STR
import os
from rsMap3D.mappers.powderscanmapper import PowderScanMapper, X_COORD_OPTIONS,\
    Y_SCALING_OPTIONS
from rsMap3D.mappers.output.powderscanwriter import PowderScanWriter
logger = logging.getLogger(__name__)

import PyQt5.QtGui as qtGui
import PyQt5.QtWidgets as qtWidgets

from rsMap3D.gui.output.abstractoutputview import AbstractOutputView

XYE_FILTER_STR = "*.xye"

class ProcessPowderScanForm(AbstractOutputView):
    '''
    This class gives a front end to an external script that has been used at 
    sector 33 for some time.  The original powderscan script was written by 
    Christian Schleputz, (originally at the APS and now at PSI). This script 
    allows processing many scans but places the results of each into a separate
    file. 
    '''
    FORM_TITLE = "Powder Scan Output"
    
    @staticmethod
    def createInstance(parent=None, appConfig=None):
        return ProcessPowderScanForm(parent=parent, appConfig=appConfig)
    
    def __init__(self, **kwargs):
        super(ProcessPowderScanForm, self).__init__(**kwargs)
        logger.debug(METHOD_ENTER_STR)
        self.mapper = None
        self.outputFileName = None
        layout = qtWidgets.QVBoxLayout()
        self.dataBox = self._createDataBox()
        controlBox = self._createControlBox()
        
        layout.addWidget(self.dataBox)
        layout.addWidget(controlBox)
        self.setLayout(layout)
        #self.outputType = BINARY_OUTPUT
        logger.debug(METHOD_EXIT_STR)
        
    def _browseForOutputFile(self):
        '''
        Launch File Browser to select output file name and directory.  Checks 
        are done to make sure the selected directory exists and that the 
        selected file is writable
        '''
        logger.debug(METHOD_ENTER_STR)
        if self.outFileNameTxt == EMPTY_STR:
            fileName = str(qtWidgets.QFileDialog.getSaveFileName(None, 
                                                             SAVE_FILE_STR,
                                                             filter=XYE_FILTER_STR)[0])
        else:
            inFileName = str(self.outFileNameTxt.text())
            fileName = str(qtWidgets.QFileDialog.getSaveFileName(None,
                                                             SAVE_FILE_STR,
                                                             filter=XYE_FILTER_STR,
                                                             directory=inFileName)[0])
        if fileName != EMPTY_STR:
            if os.path.exists(os.path.dirname(str(fileName))):
                self.outFileNameTxt.setText(fileName)
                self.outputFileName = fileName
                self.outFileNameTxt.editingFinished.emit()
            else:
                message = qtWidgets.QMessageBox()
                message.warning(self, WARNING_STR, 
                                "The specified directory does not exist")
                
                self.outFileNameTxt.setText(fileName)
                self.outputFileName = fileName
                self.outFileNameTxt.editingFinished.emit()
            if not os.access(os.path.dirname(fileName), os.W_OK):
                message = qtWidgets.QMessageBox()
                message.warning(self, WARNING_STR,
                                "The specified file is not writable")
        else:
            self.outputFileName = EMPTY_STR
            self.setFileName.emit(EMPTY_STR)
                
    def _createDataBox(self):
        '''
        create the GUI for this processing.  This should be run in __init__
        '''
        logger.debug(METHOD_ENTER_STR)
        dataBox = super(ProcessPowderScanForm, self)._createDataBox()
        dataLayout = dataBox.layout()
        row = dataLayout.rowCount()

        label = qtWidgets.QLabel("Output File Name:")
        self.outFileNameTxt = qtWidgets.QLineEdit()
        self.outFileNameButton = qtWidgets.QPushButton("Browse")
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.outFileNameTxt, row, 1)
        dataLayout.addWidget(self.outFileNameButton, row, 2)
        
        row = dataLayout.rowCount()
        label = qtWidgets.QLabel("Data Coordinate:")
        self.dataCoordinate = qtWidgets.QComboBox()
        self.dataCoordinate.addItems(X_COORD_OPTIONS) 
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.dataCoordinate, row, 1)
        
        row = dataLayout.rowCount() + 1
        label = qtWidgets.QLabel("Output Data Range - leave max/min blank for automatic range")
        dataLayout.addWidget(label, row, 0, 2, -1)

        row = dataLayout.rowCount()
        label = qtWidgets.QLabel("Min:")
        self.outMinTxt = qtWidgets.QLineEdit()
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.outMinTxt, row, 1)

        row = dataLayout.rowCount()
        label = qtWidgets.QLabel("Max:")
        self.outMaxTxt = qtWidgets.QLineEdit()
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.outMaxTxt, row, 1)
        
        row = dataLayout.rowCount()
        label = qtWidgets.QLabel("Step:")
        self.outStepTxt = qtWidgets.QLineEdit("0.01")
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.outStepTxt, row, 1)
        
        row = dataLayout.rowCount() +1
        label = qtWidgets.QLabel("Plot Results:")
        self.plotResults = qtWidgets.QCheckBox()
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.plotResults, row, 1)
        
        row = dataLayout.rowCount()
        label = qtWidgets.QLabel("Y Scaling:")
        self.yScaling = qtWidgets.QComboBox()
        self.yScaling.addItems(Y_SCALING_OPTIONS)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.yScaling, row, 1)
        
        row = dataLayout.rowCount() +1
        label = qtWidgets.QLabel("Write xye file:")
        self.writeFile = qtWidgets.QCheckBox()
        self.writeFile.setChecked(True)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.writeFile, row, 1)
        
        self.outFileNameTxt.editingFinished.connect(self._editFinishedOutFileName)
        self.outFileNameButton.clicked.connect(self._browseForOutputFile)
        self.setFileName[str].connect(self.setOutFileNameText)
        
        
        logger.debug(METHOD_EXIT_STR)
        return dataBox
        
    def _editFinishedOutFileName(self):
        '''
        process the output file name when user has finished entering this into 
        the text box.  This may also be entered by browsing.
        '''
        logger.debug(METHOD_ENTER_STR)
        fileName = str(self.outFileNameTxt.text())
        if fileName != EMPTY_STR:
            if os.path.exists(os.path.dirname(fileName)):
                self.outputFileName = fileName
            else:
                if os.path.dirname(fileName) == EMPTY_STR:
                    curDir = os.path.realpath(os.path.curdir)
                    fileName = str(os.path.join(curDir, fileName))
                else:
                    message = qtWidgets.QMessageBox()
                    message.warning(self,
                                    WARNING_STR,
                                    "The specified directory \n" + \
                                    str(os.path.dirname(fileName)) + \
                                    "\does not exist")
                self.setFileName.emit(fileName)
        if not os.access(os.path.dirname(fileName), os.W_OK):
            self.outputFileName = EMPTY_STR
            #self.setFileName.emit(EMPTY_STR)
        
        logger.debug(METHOD_EXIT_STR)

    def runMapper(self, dataSource, transform, gridWriter=None):
        '''
        This method is run by the runMapper method of the ProcessScanController,
        This will launch proceesing by a mapper appropriate for the data that we 
        have & requested output.  This ultimately runs the doMap of the selected
        Mapper
        '''
        logger.debug(METHOD_ENTER_STR)
        self.dataSource = dataSource
        
#         if self.outputFileName == "" or self.outputFileName is None:
#             self.outputFileName = os.path.join(dataSource.projectDir,
#                                                "%s.xye" % dataSource.projectName)
#             self.setFileName[str].emit(self.outputFileName)
#        if os.access(os.path.dirname(self.outputFileName), os.W_OK):
        logger.debug("Loading PowderScanMapper with xmin %s, xmax %s, xstep %s" % \
                     (str(self.outMinTxt.text()),
                      str(self.outMaxTxt.text()),
                      str(self.outStepTxt.text())))
        self.mapper = PowderScanMapper(self.dataSource,
                                       self.outputFileName,
                                       transform=transform,
                                       appConfig = self.appConfig,
                                       dataCoord = str(self.dataCoordinate.currentText()),
                                       xCoordMin = str(self.outMinTxt.text()),
                                       xCoordMax = str(self.outMaxTxt.text()),
                                       xCoordStep = str(self.outStepTxt.text()),
                                       plotResults = self.plotResults.isChecked(),
                                       yScaling = str(self.yScaling.currentText()),
                                       writeXyeFile = self.writeFile.isChecked())
        self.mapper.setGridWriter(PowderScanWriter())
        self.mapper.setProgressUpdater(self._updateProgress)
        self.mapper.doMap()
                                           
                                          
    def setOutFileNameText(self, outFile):
        '''
        Method to help with coordination between browsing for the fike and typing
        it into the text box.
        ''' 
        logger.debug(METHOD_ENTER_STR)
        self.outFileNameTxt.setText(outFile)
        self.outFileNameTxt.editingFinished.emit()