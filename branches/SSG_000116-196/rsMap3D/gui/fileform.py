'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import os

import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore

from rsMap3D.utils.srange import srange
from rsMap3D.datasource.DetectorGeometryForXrayutilitiesReader\
     import DetectorGeometryForXrayutilitiesReader
from rsMap3D.exception.rsmap3dexception import DetectorConfigException,\
    InstConfigException, RSMap3DException
from rsMap3D.gui.rsm3dcommonstrings import WARNING_STR, BROWSE_STR,\
    COMMA_STR, QLINEEDIT_COLOR_STYLE, BLACK, RED, EMPTY_STR,\
    BAD_PIXEL_FILE_FILTER, SELECT_BAD_PIXEL_TITLE, SELECT_FLAT_FIELD_TITLE,\
    TIFF_FILE_FILTER, SELECT_DETECTOR_CONFIG_TITLE, DETECTOR_CONFIG_FILE_FILTER,\
    INSTRUMENT_CONFIG_FILE_FILTER, SELECT_INSTRUMENT_CONFIG_TITLE,\
    SPEC_FILE_FILTER, SELECT_SPEC_FILE_TITLE
from rsMap3D.gui.input.abstractimageperfileview import AbstractImagePerFileView
from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource,\
    LoadCanceledException
from rsMap3D.gui.rsmap3dsignals import BLOCK_TABS_FOR_LOAD_SIGNAL
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.transforms.polemaptransform3d import PoleMapTransform3D
from rsMap3D.datasource.InstForXrayutilitiesReader \
    import InstForXrayutilitiesReader
from rsMap3D.gui.qtsignalstrings import BUTTON_CLICKED_SIGNAL, CLICKED_SIGNAL, \
    CURRENT_INDEX_CHANGED_SIGNAL, EDIT_FINISHED_SIGNAL, \
    TEXT_CHANGED_SIGNAL


class FileForm(AbstractImagePerFileView):
    '''
    This class presents information for selecting input files
    '''
    #UPDATE_PROGRESS_SIGNAL = "updateProgress"
    # Regular expressions for string validation
    PIX_AVG_REGEXP_1 =  "^(\d*,*)+$"
    PIX_AVG_REGEXP_2 =  "^((\d)+,*){2}$"
    DET_ROI_REGEXP_1 =  "^(\d*,*)+$"
    DET_ROI_REGEXP_2 =  "^(\d)+,(\d)+,(\d)+,(\d)+$"
    SCAN_LIST_REGEXP = "((\d)+(-(\d)+)?\,( )?)+"
    #Strings for Text Widgets
    
    NONE_RADIO_NAME = "None"
    BAD_PIXEL_RADIO_NAME = "Bad Pixel File"
    FLAT_FIELD_RADIO_NAME = "Flat Field Correction"
    
    def __init__(self,parent=None):
        '''
        Constructor - Layout Widgets on the page and link actions
        '''
        super(FileForm, self).__init__(parent)

        #Initialize parameters
        self.roixmin = 1
        self.roixmax = 680
        self.roiymin = 1
        self.roiymax = 480
        self.projectionDirection = [0,0,1]
        self.fileDialogTitle = SELECT_SPEC_FILE_TITLE
        self.fileDialogFilter = SPEC_FILE_FILTER
        
        self.dataBox = self._createDataBox()
        controlBox = self._createControlBox()
        
        self.layout.addWidget(self.dataBox)
        self.layout.addWidget(controlBox)
        self.setLayout(self.layout);

        #Initialize a couple of widgets to do setup.
        self.noFieldRadio.setChecked(True)
        self._fieldCorrectionTypeChanged(*(self.noFieldRadio,))
        
    def _badPixelFileChanged(self):
        '''
        Do some verification when the bad pixel file changes
        '''
        if os.path.isfile(self.badPixelFileTxt.text()) or \
           self.badPixelFileTxt.text() == EMPTY_STR:
            self.checkOkToLoad()
        else:
            message = qtGui.QMessageBox()
            message.warning(self, \
                            WARNING_STR, \
                             "The filename entered for the bad pixel " + \
                             "file is invalid")
            
                
    def _browseBadPixelFileName(self):
        '''
        Launch file browser for bad pixel file
        '''
        if self.badPixelFileTxt.text() == EMPTY_STR:
            fileName = qtGui.QFileDialog.getOpenFileName(None, \
                                               SELECT_BAD_PIXEL_TITLE, \
                                               filter=BAD_PIXEL_FILE_FILTER)
        else:
            fileDirectory = os.path.dirname(str(self.badPixelFileTxt.text()))
            fileName = qtGui.QFileDialog.getOpenFileName(None, \
                                               SELECT_BAD_PIXEL_TITLE, \
                                               filter=BAD_PIXEL_FILE_FILTER, \
                                               directory = fileDirectory)
        if fileName != EMPTY_STR:
            self.badPixelFileTxt.setText(fileName)
            self.badPixelFileTxt.emit(qtCore.SIGNAL(EDIT_FINISHED_SIGNAL))

    
    def _browseFlatFieldFileName(self):
        '''
        Launch file browser for Flat field file
        '''
        if self.flatFieldFileTxt.text() == EMPTY_STR:
            fileName = qtGui.QFileDialog.getOpenFileName(None, \
                                               SELECT_FLAT_FIELD_TITLE, \
                                               filter=TIFF_FILE_FILTER)
        else:
            fileDirectory = os.path.dirname(str(self.flatFieldFileTxt.text()))
            fileName = qtGui.QFileDialog.getOpenFileName(None, 
                                               SELECT_FLAT_FIELD_TITLE, 
                                               filter=TIFF_FILE_FILTER, \
                                               directory = fileDirectory)
        if fileName != EMPTY_STR:
            self.flatFieldFileTxt.setText(fileName)
            self.flatFieldFileTxt.emit(qtCore.SIGNAL(EDIT_FINISHED_SIGNAL))
    
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

#     def _browseForProjectDir(self):
#         '''
#         Launch file selection dialog for instrument file.
#         '''
#         if self.projNameTxt.text() == EMPTY_STR:
#             fileName = qtGui.QFileDialog.getOpenFileName(None, \
#                                                    SELECT_SPEC_FILE_TITLE, \
#                                                    filter=SPEC_FILE_FILTER)
#         else:
#             fileDirectory = os.path.dirname(str(self.projNameTxt.text()))
#             fileName = qtGui.QFileDialog.getOpenFileName(None,\
#                                                    SELECT_SPEC_FILE_TITLE, \
#                                                    directory = fileDirectory,
#                                                    filter=SPEC_FILE_FILTER)
#             
#         if fileName != EMPTY_STR:
#             self.projNameTxt.setText(fileName)
#             self.projNameTxt.emit(qtCore.SIGNAL(EDIT_FINISHED_SIGNAL))
# 
# 
    def checkOkToLoad(self):
        '''
        Make sure we have valid file names for project, instrument config, 
        and the detector config.  If we do enable load button.  If not disable
        the load button
        '''
        if os.path.isfile(self.projNameTxt.text()) and \
            os.path.isfile(self.instConfigTxt.text()) and \
            os.path.isfile(self.detConfigTxt.text()) and \
            (self.noFieldRadio.isChecked() or \
             (self.badPixelRadio.isChecked() and \
              not (str(self.badPixelFileTxt.text()) == "")) or \
             (self.flatFieldRadio.isChecked() and \
              not (str(self.flatFieldFileTxt.text()) == ""))) and \
             self.pixAvgValid(self.pixAvgTxt.text()) and \
             self.detROIValid(self.detROITxt.text()):
            retVal = True
            self.loadButton.setEnabled(retVal)
        else:
            retVal = False
            self.loadButton.setDisabled(not retVal)
        return retVal
    
    def _createControlBox(self):
        '''
        Create Layout holding controls widgets
        '''
        controlBox = super(FileForm, self)._createControlBox()
#         controlBox = qtGui.QGroupBox()
#         controlLayout = qtGui.QGridLayout()       
#         row =0
#         self.progressBar = qtGui.QProgressBar()
#         controlLayout.addWidget(self.progressBar, row, 1)
#         
#         row += 1
#         self.loadButton = qtGui.QPushButton(LOAD_STR)        
#         self.loadButton.setDisabled(True)
#         controlLayout.addWidget(self.loadButton, row, 1)
#         self.cancelButton = qtGui.QPushButton(CANCEL_STR)        
#         self.cancelButton.setDisabled(True)
#         controlLayout.addWidget(self.cancelButton, row, 2)
# 
#         self.connect(self.loadButton, \
#                      qtCore.SIGNAL(CLICKED_SIGNAL), \
#                      self._loadFile)
#         self.connect(self.cancelButton, \
#                      qtCore.SIGNAL(CLICKED_SIGNAL), \
#                      self._cancelLoadFile)
#         self.connect(self, \
#                      qtCore.SIGNAL(self.UPDATE_PROGRESS_SIGNAL), \
#                      self.setProgress)
# 
#         controlBox.setLayout(controlLayout)
        return controlBox
    
    def _createDataBox(self):
        '''
        Create widgets for collecting data
        '''
        dataBox = super(FileForm, self)._createDataBox()
        dataLayout = dataBox.layout()
        row = dataLayout.rowCount()
        label = qtGui.QLabel("Instrument Config File:");
        self.instConfigTxt = qtGui.QLineEdit()
        self.instConfigFileButton = qtGui.QPushButton(BROWSE_STR)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.instConfigTxt, row, 1)
        dataLayout.addWidget(self.instConfigFileButton, row, 2)

        row += 1
        label = qtGui.QLabel("Detector Config File:");
        self.detConfigTxt = qtGui.QLineEdit()
        self.detConfigFileButton = qtGui.QPushButton(BROWSE_STR)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.detConfigTxt, row, 1)
        dataLayout.addWidget(self.detConfigFileButton, row, 2)
        
        row += 1
        self.fieldCorrectionGroup = qtGui.QButtonGroup(self)
        self.noFieldRadio = qtGui.QRadioButton(self.NONE_RADIO_NAME)
        self.badPixelRadio = qtGui.QRadioButton(self.BAD_PIXEL_RADIO_NAME)
        self.flatFieldRadio = qtGui.QRadioButton(self.FLAT_FIELD_RADIO_NAME)
        self.fieldCorrectionGroup.addButton(self.noFieldRadio, 1)
        self.fieldCorrectionGroup.addButton(self.badPixelRadio, 2)
        self.fieldCorrectionGroup.addButton(self.flatFieldRadio, 3)
        self.badPixelFileTxt = qtGui.QLineEdit()
        self.flatFieldFileTxt = qtGui.QLineEdit()
        self.badPixelFileBrowseButton = qtGui.QPushButton(BROWSE_STR)
        self.flatFieldFileBrowseButton = qtGui.QPushButton(BROWSE_STR)

        
        dataLayout.addWidget(self.noFieldRadio, row, 0)
        row += 1
        dataLayout.addWidget(self.badPixelRadio, row, 0)
        dataLayout.addWidget(self.badPixelFileTxt, row, 1)
        dataLayout.addWidget(self.badPixelFileBrowseButton, row, 2)
        row += 1
        dataLayout.addWidget(self.flatFieldRadio, row, 0)
        dataLayout.addWidget(self.flatFieldFileTxt, row, 1)
        dataLayout.addWidget(self.flatFieldFileBrowseButton, row, 2)
        
        row += 1
        label = qtGui.QLabel("Number of Pixels To Average:");
        self.pixAvgTxt = qtGui.QLineEdit("1,1")
        rxAvg = qtCore.QRegExp(self.PIX_AVG_REGEXP_1)
        self.pixAvgTxt.setValidator(qtGui.QRegExpValidator(rxAvg,self.pixAvgTxt))
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.pixAvgTxt, row, 1)

        row += 1
        label = qtGui.QLabel("Detector ROI:");
        self.detROITxt = qtGui.QLineEdit()
        self.updateROITxt()
        rxROI = qtCore.QRegExp(self.DET_ROI_REGEXP_1)
        self.detROITxt.setValidator(qtGui.QRegExpValidator(rxROI,self.detROITxt))
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.detROITxt, row, 1)
        
        row += 1
        label = qtGui.QLabel("Scan Numbers")
        self.scanNumsTxt = qtGui.QLineEdit()
        rx = qtCore.QRegExp(self.SCAN_LIST_REGEXP)
        self.scanNumsTxt.setValidator(qtGui.QRegExpValidator(rx,self.scanNumsTxt))
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.scanNumsTxt, row, 1)

        row += 1
        label = qtGui.QLabel("Output Type")
        self.outTypeChooser = qtGui.QComboBox()
        self.outTypeChooser.addItem(self.SIMPLE_GRID_MAP_STR)
        self.outTypeChooser.addItem(self.POLE_MAP_STR)
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.outTypeChooser, row, 1)

        row += 1
        label = qtGui.QLabel("HKL output")
        dataLayout.addWidget(label, row, 0)
        self.hklCheckbox = qtGui.QCheckBox()
        dataLayout.addWidget(self.hklCheckbox, row, 1)

        # Add Signals between widgets
        self.connect(self.instConfigFileButton, \
                     qtCore.SIGNAL(CLICKED_SIGNAL), \
                     self._browseForInstFile)
        self.connect(self.detConfigFileButton, \
                     qtCore.SIGNAL(CLICKED_SIGNAL), \
                     self._browseForDetFile)
        self.connect(self.instConfigTxt, \
                     qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), \
                     self._instConfigChanged)
        self.connect(self.detConfigTxt, \
                     qtCore.SIGNAL(EDIT_FINISHED_SIGNAL), \
                     self._detConfigChanged)
        self.connect(self.outTypeChooser, \
                     qtCore.SIGNAL(CURRENT_INDEX_CHANGED_SIGNAL), \
                     self._outputTypeChanged)
        self.connect(self.fieldCorrectionGroup,\
                     qtCore.SIGNAL(BUTTON_CLICKED_SIGNAL), \
                     self._fieldCorrectionTypeChanged)
        self.connect(self.badPixelFileTxt,
                     qtCore.SIGNAL(EDIT_FINISHED_SIGNAL),
                     self._badPixelFileChanged)
        self.connect(self.flatFieldFileTxt,
                     qtCore.SIGNAL(EDIT_FINISHED_SIGNAL),
                     self._flatFieldFileChanged)
        self.connect(self.badPixelFileBrowseButton, \
                     qtCore.SIGNAL(CLICKED_SIGNAL), \
                     self._browseBadPixelFileName)
        self.connect(self.flatFieldFileBrowseButton, \
                     qtCore.SIGNAL(CLICKED_SIGNAL), \
                     self._browseFlatFieldFileName)
        self.connect(self.pixAvgTxt,
                     qtCore.SIGNAL(TEXT_CHANGED_SIGNAL),
                     self._pixAvgTxtChanged)
        self.connect(self.detROITxt,
                     qtCore.SIGNAL(TEXT_CHANGED_SIGNAL),
                     self._detROITxtChanged)
        
        dataBox.setLayout(dataLayout)
        return dataBox
    
    def _detConfigChanged(self):
        '''
        '''
        if os.path.isfile(self.detConfigTxt.text()) or \
           self.detConfigTxt.text() == "":
            self.checkOkToLoad()
            try:
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
        
    def _fieldCorrectionTypeChanged(self, *fieldCorrType):
        '''
        React when the field type radio buttons change.  Disable/Enable other 
        widgets as appropriate
        '''
        if fieldCorrType[0].text() == self.NONE_RADIO_NAME:
            self.badPixelFileTxt.setDisabled(True)
            self.badPixelFileBrowseButton.setDisabled(True)
            self.flatFieldFileTxt.setDisabled(True)
            self.flatFieldFileBrowseButton.setDisabled(True)
        elif fieldCorrType[0].text() == self.BAD_PIXEL_RADIO_NAME:
            self.badPixelFileTxt.setDisabled(False)
            self.badPixelFileBrowseButton.setDisabled(False)
            self.flatFieldFileTxt.setDisabled(True)
            self.flatFieldFileBrowseButton.setDisabled(True)
        elif fieldCorrType[0].text() == self.FLAT_FIELD_RADIO_NAME:
            self.badPixelFileTxt.setDisabled(True)
            self.badPixelFileBrowseButton.setDisabled(True)
            self.flatFieldFileTxt.setDisabled(False)
            self.flatFieldFileBrowseButton.setDisabled(False)
        self.checkOkToLoad()
            
            
    def _flatFieldFileChanged(self):
        '''
        Do some verification when the flat field file changes
        '''
        if os.path.isfile(self.flatFieldFileTxt.text()) or \
           self.flatFieldFileTxt.text() == "":
            self.checkOkToLoad()
        else:
            message = qtGui.QMessageBox()
            message.warning(self, \
                            WARNING_STR, \
                             "The filename entered for the flat field " + \
                             "file is invalid")
                
    def getBadPixelFileName(self):
        '''
        Return the badPixel file name.  If empty or if the bad pixel radio 
        button is not checked return None
        '''
        if (str(self.badPixelFileTxt.text()) == EMPTY_STR) or \
           (not self.badPixelRadio.isChecked()):
            return None
        else:
            return str(self.badPixelFileTxt.text())
        
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
            Sector33SpecDataSource(str(self.getProjectDir()), \
                                   str(self.getProjectName()), \
                                   str(self.getProjectExtension()), \
                                   str(self.getInstConfigName()), \
                                   str(self.getDetConfigName()), \
                                   transform = self.transform, \
                                   scanList = self.getScanList(), \
                                   roi = self.getDetectorROI(), \
                                   pixelsToAverage = \
                                      self.getPixelsToAverage(), \
                                   badPixelFile = \
                                      self.getBadPixelFileName(), \
                                   flatFieldFile = \
                                      self.getFlatFieldFileName() \
                                  )
        self.dataSource.setProgressUpdater(self.updateProgress)
        self.dataSource.loadSource(mapHKL = self.getMapAsHKL())
        return self.dataSource
        
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
    
    def getFlatFieldFileName(self):
        '''
        Return the flat field file name.  If empty or if the bad pixel radio 
        button is not checked return None
        '''
        if (str(self.flatFieldFileTxt.text()) == EMPTY_STR) or \
           (not self.flatFieldRadio.isChecked()):
            return None
        else:
            return str(self.flatFieldFileTxt.text())
        
    def getInstConfigName(self):
        '''
        Return the Instrument config file name
        '''
        return self.instConfigTxt.text()

    def getMapAsHKL(self):
        '''
        '''
        return self.hklCheckbox.isChecked()
        
    def getOutputType(self):
        '''
        Get the output type to be used.
        '''
        return self.outTypeChooser.currentText()
    
    def getPixelsToAverage(self):
        '''
        :return: the pixels to average as a list
        '''
        pixelStrings = str(self.pixAvgTxt.text()).split(COMMA_STR)
        pixels = []
        for value in pixelStrings:
            pixels.append(int(value))
        return pixels
    
    def getProjectionDirection(self):
        '''
        Return projection direction for stereographic projections
        '''
        return self.projectionDirection
          
            
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
            except InstConfigException:
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
            
    def _pixAvgTxtChanged(self, text):
        '''
        Check to make sure the text for pix to average is valid and indicate 
        by a color change 
        :param text: new values as a text list 
        '''
        if self.pixAvgValid(text):
            self.pixAvgTxt.setStyleSheet(QLINEEDIT_COLOR_STYLE % BLACK)
        else: 
            self.pixAvgTxt.setStyleSheet(QLINEEDIT_COLOR_STYLE % RED)
        self.checkOkToLoad()
            
    def pixAvgValid(self, text):
        '''
        Check to make sure that the pixAvgText is valid
        :param text: new values as a text list 
        '''
        rxPixAvg = qtCore.QRegExp(self.PIX_AVG_REGEXP_2)
        validator = qtGui.QRegExpValidator(rxPixAvg, None)
        pos = 0
        if validator.validate(text, pos)[0] == qtGui.QValidator.Acceptable:
            return True
        else:
            return False
        
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
        detector = detConfig.getDetectorById("Pilatus")
        detSize = detConfig.getNpixels(detector)
        xmax = detSize[0]
        ymax = detSize[1]
        if xmax < self.roixmax:
            self.roixmax = xmax
        if ymax < self.roiymax:
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
