'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import os
import logging
from rsMap3D.gui.rsm3dcommonstrings import LOGGER_NAME
logger = logging.getLogger(LOGGER_NAME + '.gui.input.usesxmldetectorconfig')

import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore

from rsMap3D.gui.input.abstractfileview import AbstractFileView
from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader import DetectorGeometryForXrayutilitiesReader
from rsMap3D.exception.rsmap3dexception import RSMap3DException,\
    DetectorConfigException
from rsMap3D.gui.rsm3dcommonstrings import COMMA_STR, EMPTY_STR,\
    QLINEEDIT_COLOR_STYLE, WARNING_STR, BROWSE_STR, DETECTOR_CONFIG_FILE_FILTER,\
    SELECT_DETECTOR_CONFIG_TITLE, BLACK, RED

class UsesXMLDetectorConfig(AbstractFileView):
    '''
    class to provide functionality provided by the XML detector configuration 
    file.  Designed for use along with other view classes.  Use multiple inheritance
    such as "class myView(specXmlDrivenFileForm, usesXMLDetectorConfig):
    then add the gui blocks in _createDataBox to add fike selection stuff. 
    This provides gui that allows file selection, then detector selection since
    multiple detectors can be defined in a file and then ROI selection.
    '''
    DET_ROI_REGEXP_1 =  "^(\d*,*)+$"
    DET_ROI_REGEXP_2 =  "^(\d)+,(\d)+,(\d)+,(\d)+$"

    #UPDATE_PROGRESS_SIGNAL = "updateProgress"
    # Regular expressions for string validation
    PIX_AVG_REGEXP_1 =  "^(\d*,*)+$"
    PIX_AVG_REGEXP_2 =  "^((\d)+,*){2}$"

    def __init__(self, parent=None):
        '''
        constructor
        '''
        super(UsesXMLDetectorConfig, self).__init__(parent)
        
        self.roixmin = 1
        self.roixmax = 680
        self.roiymin = 1
        self.roiymax = 480
        self.currentDetector = ""

#    @qtCore.pyqtSlot()
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
            self.detConfigTxt.editingFinished.emit()

    def _createDetConfig(self, layout, row):
        '''
        Add in gui elements for selecting a detector config file and then
        selecting from the list of detectors provided.
        '''
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
        
        # use new style to emit edit finished signal
        self.detConfigFileButton.clicked.connect(self._browseForDetFile)
        self.detConfigTxt.editingFinished.connect(self._detConfigChanged)
        self.detSelect.currentIndexChanged[str].connect(self._currentDetectorChanged)
        

    def _createDetectorROIInput(self, layout, row, silent=False):
        '''
        Adds gui elements for entering the ROI
        '''
        label = qtGui.QLabel("Detector ROI:");
        self.detROITxt = qtGui.QLineEdit()
        self.updateROITxt()
        rxROI = qtCore.QRegExp(self.DET_ROI_REGEXP_1)
        self.detROITxt.setValidator(qtGui.QRegExpValidator(rxROI,self.detROITxt))
        
        if (silent==False):
            layout.addWidget(label, row, 0)
            layout.addWidget(self.detROITxt, row, 1)
        
        # use new style to emit edit finished signal
        self.detROITxt.textChanged.connect(self._detROITxtChanged)
    
    def _createNumberOfPixelsToAverage(self, layout, row, silent=False):
        label = qtGui.QLabel("Number of Pixels To Average:");
        self.pixAvgTxt = qtGui.QLineEdit("1,1")
        rxAvg = qtCore.QRegExp(self.PIX_AVG_REGEXP_1)
        self.pixAvgTxt.setValidator(qtGui.QRegExpValidator(rxAvg,self.pixAvgTxt))
        if (silent == False):
            layout.addWidget(label, row, 0)
            layout.addWidget(self.pixAvgTxt, row, 1)

#    @qtCore.pyqtSlot(str)
    def _currentDetectorChanged(self, currentDetector):
        logger.info("Setting current detector to " + str(currentDetector))
        self.currentDetector = currentDetector
        self.updateROIandNumAvg()
        
#    @qtCore.pyqtSlot()
    def _detConfigChanged(self):
        '''
        '''

        logger.debug("Entering _detConfigChanged")
        if self.detFileExists() or \
           self.detConfigTxt.text() == "":
            self.checkOkToLoad()
            if self.detConfigTxt.text() != "":
                try:
                    self.updateDetectorList()
                    #self.updateROIandNumAvg()
                except DetectorConfigException as ex:
                    logger.error( ex)
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


    def detFileExists(self):
        return os.path.isfile(self.detConfigTxt.text())

    def isDetFileOk(self):
        detFileExists = self.detFileExists()
        if detFileExists:
            try:
                self.updateDetectorList()
                self.updateROIandNumAvg()
            except DetectorConfigException:
                # not a well formed deteector config
                return False
        return detFileExists
        
#    @qtCore.pyqtSlot(str)
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
        self.detSelect.currentIndexChanged[str].emit(self.detSelect.itemText(0))
        
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

