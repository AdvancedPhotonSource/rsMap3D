# coding=utf-8
'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
import os
import logging
from rsMap3D.config.rsmap3dlogging import METHOD_ENTER_STR, METHOD_EXIT_STR
logger = logging.getLogger(__name__)

import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets

from rsMap3D.gui.input.abstractfileview import AbstractFileView
from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader \
    import DetectorGeometryForXrayutilitiesReader
from rsMap3D.exception.rsmap3dexception import RSMap3DException,\
    DetectorConfigException
from rsMap3D.gui.rsm3dcommonstrings import COMMA_STR, EMPTY_STR,\
    QLINEEDIT_COLOR_STYLE, WARNING_STR, BROWSE_STR, \
    DETECTOR_CONFIG_FILE_FILTER,\
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

    def __init__(self, parent=None, **kwargs):
        '''
        constructor
        '''
        super(UsesXMLDetectorConfig, self).__init__(parent, **kwargs)
        logger.debug(METHOD_ENTER_STR)
        self.roixmin = 1
        self.roixmax = 680
        self.roiymin = 1
        self.roiymax = 480
        self.currentDetector = ""
        self.detConfig = None
        self.detFileOk = False
        logger.debug(METHOD_EXIT_STR)
        
#    @qtCore.pyqtSlot()
    def _browseForDetFile(self):
        '''
        Launch file selection dialog for Detector file.
        '''
        logger.debug(METHOD_ENTER_STR)
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
        logger.debug(METHOD_EXIT_STR)

    def _createDetConfig(self, layout, row):
        '''
        Add in gui elements for selecting a detector config file and then
        selecting from the list of detectors provided.
        '''
        logger.debug(METHOD_ENTER_STR)
        label = qtWidgets.QLabel("Detector Config File:");
        self.detConfigTxt = qtWidgets.QLineEdit()
        self.detConfigFileButton = qtWidgets.QPushButton(BROWSE_STR)
        layout.addWidget(label, row, 0)
        layout.addWidget(self.detConfigTxt, row, 1)
        layout.addWidget(self.detConfigFileButton, row, 2)

        row += 1
        label = qtWidgets.QLabel("Select Detector")
        self.detSelect = qtWidgets.QComboBox()
        layout.addWidget(label, row, 0)
        layout.addWidget(self.detSelect, row, 1)
        
        # use new style to emit edit finished signal
        self.detConfigFileButton.clicked.connect(self._browseForDetFile)
        self.detConfigTxt.editingFinished.connect(self._detConfigChanged)
        self.detSelect.currentIndexChanged[str].connect(self._currentDetectorChanged)
        logger.debug(METHOD_EXIT_STR)
        

    def _createDetectorROIInput(self, layout, row, silent=False):
        '''
        Adds gui elements for entering the ROI
        '''
        logger.debug(METHOD_ENTER_STR)
        label = qtWidgets.QLabel("Detector ROI:");
        self.detROITxt = qtWidgets.QLineEdit()
        self.updateROITxt()
        rxROI = qtCore.QRegExp(self.DET_ROI_REGEXP_1)
        self.detROITxt.setValidator(qtGui.QRegExpValidator(rxROI,self.detROITxt))
        
        if (silent==False):
            layout.addWidget(label, row, 0)
            layout.addWidget(self.detROITxt, row, 1)
        
        # use new style to emit edit finished signal
        self.detROITxt.textChanged.connect(self._detROITxtEntered)
        logger.debug(METHOD_EXIT_STR)
    
    def _createNumberOfPixelsToAverage(self, layout, row, silent=False):
        logger.debug(METHOD_ENTER_STR)
        label = qtWidgets.QLabel("Number of Pixels To Average:");
        self.pixAvgTxt = qtWidgets.QLineEdit("1,1")
        rxAvg = qtCore.QRegExp(self.PIX_AVG_REGEXP_1)
        self.pixAvgTxt.setValidator(qtGui.QRegExpValidator(rxAvg,self.pixAvgTxt))
        if (silent == False):
            layout.addWidget(label, row, 0)
            layout.addWidget(self.pixAvgTxt, row, 1)
        logger.debug(METHOD_EXIT_STR)

#    @qtCore.pyqtSlot(str)
    def _currentDetectorChanged(self, currentDetector):
        logger.debug(METHOD_ENTER_STR % str(currentDetector))
        self.currentDetector = str(currentDetector)
        self.updateROIandNumAvg()
        logger.debug(METHOD_EXIT_STR  % self.currentDetector)
        
#    @qtCore.pyqtSlot()
    def _detConfigChanged(self):
        '''
        '''
        logger.debug(METHOD_ENTER_STR)
        if self.detFileExists() or \
           self.detConfigTxt.text() == "":
            if self.detConfigTxt.text() != "":
                try:
                    self.detFileOk = self.isDetFileOk()
                    #self.updateDetectorList()
                    #self.updateROIandNumAvg()
                except DetectorConfigException as ex:
                    logger.error( ex)
                    message = qtWidgets.QMessageBox()
                    message.warning(self, \
                                     WARNING_STR,\
                                     "Trouble getting ROI or Num average " + \
                                     "from the detector config file")
            self.checkOkToLoad()
        else:
            message = qtWidgets.QMessageBox()
            message.warning(self, \
                             WARNING_STR,\
                             "The filename entered for the detector " + \
                             "configuration is invalid")
            logger.debug(METHOD_EXIT_STR)


    def detFileExists(self):
        logger.debug(METHOD_ENTER_STR)
        fileExists = os.path.isfile(self.detConfigTxt.text())
        logger.debug(METHOD_EXIT_STR + str(fileExists))
        return fileExists

    def isDetFileOk(self):
        logger.debug(METHOD_ENTER_STR)
        detFileExists = self.detFileExists()
        if detFileExists:
            try:
                self.updateDetectorList()
                #self.updateROIandNumAvg()
            except DetectorConfigException:
                # not a well formed deteector config
                logger.debug("Exiting by Exception")
                return False
        logger.debug(METHOD_EXIT_STR + str(detFileExists))
        return detFileExists
        
#    @qtCore.pyqtSlot(str)
    def _detROITxtChanged(self, text):
        '''
        Check to make sure the text for detector roi is valid and indicate 
        by a color change 
        '''
        logger.debug(METHOD_ENTER_STR)
        if self.detROIValid(text):
            self.detROITxt.setStyleSheet(QLINEEDIT_COLOR_STYLE % BLACK)
        else: 
            self.detROITxt.setStyleSheet(QLINEEDIT_COLOR_STYLE % RED)
        logger.debug(METHOD_ENTER_STR)

    def _detROITxtEntered(self, text):
        logger.debug(METHOD_ENTER_STR)
        self._detROITxtChanged(text)
        self.checkOkToLoad()
        logger.debug(METHOD_EXIT_STR)

    def detROIValid(self, text):
        '''
        Check to make sure the text for is a vaid detector roi
        '''
        logger.debug(METHOD_ENTER_STR)
        rxROI = qtCore.QRegExp(self.DET_ROI_REGEXP_2)
        validator = qtGui.QRegExpValidator(rxROI, None)
        pos = 0
        if validator.validate(text, pos)[0] == qtGui.QValidator.Acceptable:
            roiVals = self.getDetectorROI(rois=str(text))
            if (roiVals[0] <= roiVals[1]) and \
               (roiVals[2] <= roiVals[3]):
                logger.debug(METHOD_EXIT_STR + str(True))
                return True
            else:
                logger.debug(METHOD_EXIT_STR + str(False))
                return False
        else:
            logger.debug(METHOD_EXIT_STR + str(False))
            return False
        
    def getDetConfigName(self):
        '''
        Return the selected Detector Configuration file
        '''
        logger.debug(METHOD_ENTER_STR)
        nameText = self.detConfigTxt.text()
        logger.debug(METHOD_EXIT_STR % nameText)
        return nameText

    def getDetectorROI(self, rois=EMPTY_STR):
        '''
        :param rois: a string list with the roi values
        :return: The detector ROI as a list
        :raises RSMap3DException: if the string is not a 4 element list
        '''
        logger.debug(METHOD_ENTER_STR)
        if rois == EMPTY_STR:
            roiStrings = str(self.detROITxt.text()).split(COMMA_STR)
        else:
            roiStrings = rois.split(COMMA_STR)
            
        roi = []
        if len(roiStrings) != 4:
            logger.debug("Exiting via exception" +
                          "Detector ROI needs 4 values. " + \
                                   str(len(roiStrings)) + \
                                   " were given.")
            raise RSMap3DException("Detector ROI needs 4 values. " + \
                                   str(len(roiStrings)) + \
                                   " were given.")
        for value in roiStrings:
            roi.append(int(value))
        logger.debug(METHOD_EXIT_STR)
        return roi
    
    def updateDetectorList(self):
        logger.debug(METHOD_ENTER_STR)
        oldNumDet = self.detSelect.count()
        for index in reversed(range(oldNumDet)):
            self.detSelect.removeItem(index)
        detConfigFileName = str(self.detConfigTxt.text())
        logger.debug("detectorConfigFile - " + detConfigFileName)    
        self.detConfig = \
            DetectorGeometryForXrayutilitiesReader(detConfigFileName)
        detectors = self.detConfig.getDetectors()
        for detector in detectors:
            detID = self.detConfig.getDetectorID(detector)
            self.detSelect.addItem(detID)
            logger.debug("updateDetectorList - " + str(detID))
        self.detSelect.itemText(0)
        
        self.detSelect.currentIndexChanged[str].emit(self.detSelect.itemText(0))
        logger.debug(METHOD_EXIT_STR)
        
    def updateROIandNumAvg(self):
        '''
        Set default values into the ROI and number of pixel to average text 
        boxes
        '''
        logger.debug(METHOD_ENTER_STR)
#         detConfig = \
#             DetectorGeometryForXrayutilitiesReader(self.detConfigTxt.text())
        logger.debug("self.currentDetector " + str(self.currentDetector))
        detector = self.detConfig.getDetectorById(str(self.currentDetector))
        detSize = self.detConfig.getNpixels(detector)
        xmax = detSize[0]
        ymax = detSize[1]
        self.roixmax = xmax
        self.roiymax = ymax
        self.updateROITxt()
        logger.debug(METHOD_EXIT_STR)

    def updateROITxt(self):
        '''
        Update the ROI string with the current value of the ROI
        '''
        logger.debug(METHOD_ENTER_STR)
        roiStr = str(self.roixmin) +\
                COMMA_STR +\
                str(self.roixmax) +\
                COMMA_STR +\
                str(self.roiymin) +\
                COMMA_STR +\
                str(self.roiymax)
        self.detROITxt.setText(roiStr)
        logger.debug(METHOD_EXIT_STR)

