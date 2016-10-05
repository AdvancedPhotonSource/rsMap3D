'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''

import PyQt4.QtCore as qtCore
import PyQt4.QtGui as qtGui

from rsMap3D.gui.input.abstractimageperfileview import AbstractImagePerFileView
from rsMap3D.gui.rsm3dcommonstrings import EMPTY_STR,\
    SELECT_DETECTOR_CONFIG_TITLE, DETECTOR_CONFIG_FILE_FILTER,\
    SELECT_INSTRUMENT_CONFIG_TITLE, INSTRUMENT_CONFIG_FILE_FILTER, WARNING_STR,\
    QLINEEDIT_COLOR_STYLE, RED, BLACK, COMMA_STR, BROWSE_STR, SPEC_FILE_FILTER,\
    SELECT_SPEC_FILE_TITLE
from rsMap3D.gui.qtsignalstrings import EDIT_FINISHED_SIGNAL, CLICKED_SIGNAL,\
    TEXT_CHANGED_SIGNAL, CURRENT_INDEX_CHANGED_SIGNAL
import os
from rsMap3D.exception.rsmap3dexception import DetectorConfigException,\
    RSMap3DException, InstConfigException
from rsMap3D.utils.srange import srange
from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader import DetectorGeometryForXrayutilitiesReader
from rsMap3D.datasource.InstForXrayutilitiesReader import InstForXrayutilitiesReader


class SpecXMLDrivenFileForm(AbstractImagePerFileView):

    DET_ROI_REGEXP_1 =  "^(\d*,*)+$"
    DET_ROI_REGEXP_2 =  "^(\d)+,(\d)+,(\d)+,(\d)+$"
    SCAN_LIST_REGEXP = "((\d)+(-(\d)+)?\,( )?)+"

    def __init__(self, parent=None):
        super(SpecXMLDrivenFileForm, self).__init__(parent)
        
        self.roixmin = 1
        self.roixmax = 680
        self.roiymin = 1
        self.roiymax = 480
        self.currentDetector = ""
        
        self.fileDialogTitle = SELECT_SPEC_FILE_TITLE
        self.fileDialogFilter = SPEC_FILE_FILTER

        self.dataBox = self._createDataBox()
        controlBox = self._createControlBox()
        
        self.layout.addWidget(self.dataBox)
        self.layout.addWidget(controlBox)
        self.setLayout(self.layout);

    def _createDetConfig(self, layout, row):
        label = qtGui.QLabel("Detector Config File:");
        self.detConfigTxt = qtGui.QLineEdit()
        self.detConfigFileButton = qtGui.QPushButton(BROWSE_STR)
        layout.addWidget(label, row, 0)
        layout.addWidget(self.detConfigTxt, row, 1)
        layout.addWidget(self.detConfigFileButton, row, 2)

        row += 1
        label = qtGui.QLabel("Select Detector")
        self.detSelect = qtGui.QComboBox()
        layout.addWidget(label, row, 0)
        layout.addWidget(self.detSelect, row, 1)
        
        self.connect(self.detConfigFileButton, \
                     qtCore.SIGNAL(CLICKED_SIGNAL), \
                     self._browseForDetFile)
        self.connect(self.detConfigTxt, \
                     qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), \
                     self._detConfigChanged)
        self.connect(self.detSelect,
                     qtCore.SIGNAL(CURRENT_INDEX_CHANGED_SIGNAL),
                     self._currentDetectorChanged)

    def _createInstConfig(self, layout, row):
        label = qtGui.QLabel("Instrument Config File:");
        self.instConfigTxt = qtGui.QLineEdit()
        self.instConfigFileButton = qtGui.QPushButton(BROWSE_STR)
        layout.addWidget(label, row, 0)
        layout.addWidget(self.instConfigTxt, row, 1)
        layout.addWidget(self.instConfigFileButton, row, 2)
        self.connect(self.instConfigFileButton, \
                     qtCore.SIGNAL(CLICKED_SIGNAL), \
                     self._browseForInstFile)
        self.connect(self.instConfigTxt, \
                     qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), \
                     self._instConfigChanged)

    def _createDetectorROIInput(self, layout, row):
        label = qtGui.QLabel("Detector ROI:");
        self.detROITxt = qtGui.QLineEdit()
        self.updateROITxt()
        rxROI = qtCore.QRegExp(self.DET_ROI_REGEXP_1)
        self.detROITxt.setValidator(qtGui.QRegExpValidator(rxROI,self.detROITxt))
        
        layout.addWidget(label, row, 0)
        layout.addWidget(self.detROITxt, row, 1)
        self.connect(self.detROITxt,
                     qtCore.SIGNAL(TEXT_CHANGED_SIGNAL),
                     self._detROITxtChanged)
    
    def _createHKLOutput(self, layout, row):
        label = qtGui.QLabel("HKL output")
        layout.addWidget(label, row, 0)
        self.hklCheckbox = qtGui.QCheckBox()
        layout.addWidget(self.hklCheckbox, row, 1)

        
    def _createOutputType(self, layout, row):
        label = qtGui.QLabel("Output Type")
        self.outTypeChooser = qtGui.QComboBox()
        self.outTypeChooser.addItem(self.SIMPLE_GRID_MAP_STR)
        self.outTypeChooser.addItem(self.POLE_MAP_STR)
        layout.addWidget(label, row, 0)
        layout.addWidget(self.outTypeChooser, row, 1)
        self.connect(self.outTypeChooser, \
                     qtCore.SIGNAL(CURRENT_INDEX_CHANGED_SIGNAL), \
                     self._outputTypeChanged)
        
        
    def _createScanNumberInput(self, layout, row):
        label = qtGui.QLabel("Scan Numbers")
        self.scanNumsTxt = qtGui.QLineEdit()
        rx = qtCore.QRegExp(self.SCAN_LIST_REGEXP)
        self.scanNumsTxt.setValidator(qtGui.QRegExpValidator(rx,self.scanNumsTxt))
        layout.addWidget(label, row, 0)
        layout.addWidget(self.scanNumsTxt, row, 1)
        
    def _currentDetectorChanged(self, currentDetector):
        print currentDetector
        self.currentDetector = currentDetector
        self.updateROIandNumAvg()
        
    def _browseForDetFile(self):
        '''
        Launch file selection dialog for Detector file.
        '''
        if self.detConfigTxt.text() == EMPTY_STR:
            fileName = qtGui.QFileDialog.getOpenFileName(None, \
                                            SELECT_DETECTOR_CONFIG_TITLE, \
                                            filter=DETECTOR_CONFIG_FILE_FILTER)
        else:
            fileDirectory = os.path.dirname(str(self.detConfigTxt.text()))
            fileName = qtGui.QFileDialog.getOpenFileName(None, \
                                         SELECT_DETECTOR_CONFIG_TITLE, \
                                         filter=DETECTOR_CONFIG_FILE_FILTER, \
                                         directory = fileDirectory)
        if fileName != EMPTY_STR:
            self.detConfigTxt.setText(fileName)
            self.detConfigTxt.emit(qtCore.SIGNAL(EDIT_FINISHED_SIGNAL))

    def _browseForInstFile(self):
        '''
        Launch file selection dialog for instrument file.
        '''
        if self.instConfigTxt.text() == EMPTY_STR:
            fileName = qtGui.QFileDialog.getOpenFileName(None, 
                                        SELECT_INSTRUMENT_CONFIG_TITLE, 
                                        filter=INSTRUMENT_CONFIG_FILE_FILTER)
        else:
            fileDirectory = os.path.dirname(str(self.instConfigTxt.text()))
            fileName = qtGui.QFileDialog.getOpenFileName(None, 
                                        SELECT_INSTRUMENT_CONFIG_TITLE, 
                                        filter=INSTRUMENT_CONFIG_FILE_FILTER, \
                                        directory = fileDirectory)
        if fileName != EMPTY_STR:
            self.instConfigTxt.setText(fileName)
            self.instConfigTxt.emit(qtCore.SIGNAL(EDIT_FINISHED_SIGNAL))

    def _detConfigChanged(self):
        '''
        '''
        if os.path.isfile(self.detConfigTxt.text()) or \
           self.detConfigTxt.text() == "":
            self.checkOkToLoad()
            try:
                self.updateDetectorList()
                self.updateROIandNumAvg()
            except DetectorConfigException:
                message = qtGui.QMessageBox()
                message.warning(self, \
                                 WARNING_STR,\
                                 "Trouble getting ROI or Num average " + \
                                 "from the detector config file")
        else:
            message = qtGui.QMessageBox()
            message.warning(self, \
                             WARNING_STR,\
                             "The filename entered for the detector " + \
                             "configuration is invalid")
        

    def _detROITxtChanged(self, text):
        '''
        Check to make sure the text for detector roi is valid and indicate 
        by a color change 
        '''
        if self.detROIValid(text):
            self.detROITxt.setStyleSheet(QLINEEDIT_COLOR_STYLE % BLACK)
        else: 
            self.detROITxt.setStyleSheet(QLINEEDIT_COLOR_STYLE % RED)
        self.checkOkToLoad()

    def detROIValid(self, text):
        '''
        Check to make sure the text for is a vaid detector roi
        '''
        rxROI = qtCore.QRegExp(self.DET_ROI_REGEXP_2)
        validator = qtGui.QRegExpValidator(rxROI, None)
        pos = 0
        if validator.validate(text, pos)[0] == qtGui.QValidator.Acceptable:
            roiVals = self.getDetectorROI(rois=str(text))
            if (roiVals[0] <= roiVals[1]) and \
               (roiVals[2] <= roiVals[3]):
                return True
            else:
                return False
        else:
            return False
        
    def getDetConfigName(self):
        '''
        Return the selected Detector Configuration file
        '''
        return self.detConfigTxt.text()

    def getDetectorROI(self, rois=EMPTY_STR):
        '''
        :param rois: a string list with the roi values
        :return: The detector ROI as a list
        :raises RSMap3DException: if the string is not a 4 element list
        '''
        if rois == EMPTY_STR:
            roiStrings = str(self.detROITxt.text()).split(COMMA_STR)
        else:
            roiStrings = rois.split(COMMA_STR)
            
        roi = []
        if len(roiStrings) <> 4:
            raise RSMap3DException("Detector ROI needs 4 values. " + \
                                   str(len(roiStrings)) + \
                                   " were given.")
        for value in roiStrings:
            roi.append(int(value))
        return roi
    
    def getInstConfigName(self):
        '''
        Return the Instrument config file name
        '''
        return self.instConfigTxt.text()

    def getMapAsHKL(self):
        '''
        '''
#        Not sure if we need this JPH
        return self.hklCheckbox.isChecked()
#        return False
    
    def getOutputType(self):
        '''
        Get the output type to be used.
        '''
        return self.outTypeChooser.currentText()
    
    def getScanList(self):
        '''
        return a list of scans to be used for loading data
        '''
        if str(self.scanNumsTxt.text()) == EMPTY_STR:
            return None
        else:
            scans = srange(str(self.scanNumsTxt.text()))
            return scans.list() 
        
    def _instConfigChanged(self):
        '''
        When the inst config file name changes check to make sure we have a 
        valid file (if not empty) and the check to see if it is OK to enable
        the Load button.  Also, grab the projection direction from the file.
        '''
        if os.path.isfile(self.instConfigTxt.text()) or \
           self.instConfigTxt.text() == EMPTY_STR:
            self.checkOkToLoad()
            try:
                self.updateProjectionDirection()
            except InstConfigException :
                message = qtGui.QMessageBox()
                message.warning(self, \
                                WARNING_STR, \
                                 "Trouble getting the projection direction " + \
                                 "from the instrument config file.")
        else:
            message = qtGui.QMessageBox()
            message.warning(self, \
                            WARNING_STR, \
                             "The filename entered for the instrument " + \
                             "configuration is invalid")
        
    def _outputTypeChanged(self, typeStr):
        '''
        If the output is selected to be a simple grid map type then allow
        the user to select HKL as an output.
        :param typeStr: String holding the outpu type
        '''
        if typeStr == self.SIMPLE_GRID_MAP_STR:
            self.hklCheckbox.setEnabled(True)
        else:
            self.hklCheckbox.setDisabled(True)
            self.hklCheckbox.setCheckState(False)
            

    def updateDetectorList(self):
        oldNumDet = self.detSelect.count()
        for index in reversed(range(oldNumDet)):
            self.detSelect.removeItem(index)
            
        detConfig = \
            DetectorGeometryForXrayutilitiesReader(self.detConfigTxt.text())
        detectors = detConfig.getDetectors()
        for detector in detectors:
            self.detSelect.addItem(detConfig.getDetectorID(detector))
            
        self.detSelect.itemText(0)
        
    def updateProjectionDirection(self):
        '''
        update the stored value for the projection direction
        '''
        instConfig = \
            InstForXrayutilitiesReader(self.instConfigTxt.text())
        self.projectionDirection = instConfig.getProjectionDirection()
        
    def updateROIandNumAvg(self):
        '''
        Set default values into the ROI and number of pixel to average text 
        boxes
        '''
        detConfig = \
            DetectorGeometryForXrayutilitiesReader(self.detConfigTxt.text())
        detector = detConfig.getDetectorById(self.currentDetector)
        detSize = detConfig.getNpixels(detector)
        xmax = detSize[0]
        ymax = detSize[1]
        self.roixmax = xmax
        self.roiymax = ymax
        self.updateROITxt()

    def updateROITxt(self):
        '''
        Update the ROI string with the current value of the ROI
        '''
        roiStr = str(self.roixmin) +\
                COMMA_STR +\
                str(self.roixmax) +\
                COMMA_STR +\
                str(self.roiymin) +\
                COMMA_STR +\
                str(self.roiymax)
        self.detROITxt.setText(roiStr)

