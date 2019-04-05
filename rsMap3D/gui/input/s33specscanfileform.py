'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import os

import logging
from rsMap3D.config.rsmap3dlogging import METHOD_ENTER_STR, METHOD_EXIT_STR
from rsMap3D.gui.output.processpowderscanform import ProcessPowderScanForm
logger = logging.getLogger(__name__)
import PyQt5.QtGui as qtGui
import PyQt5.QtCore as qtCore
import PyQt5.QtWidgets as qtWidgets

from rsMap3D.gui.rsm3dcommonstrings import WARNING_STR, BROWSE_STR,\
    COMMA_STR, QLINEEDIT_COLOR_STYLE, BLACK, RED, EMPTY_STR,\
    BAD_PIXEL_FILE_FILTER, SELECT_BAD_PIXEL_TITLE, SELECT_FLAT_FIELD_TITLE,\
    TIFF_FILE_FILTER
from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.transforms.polemaptransform3d import PoleMapTransform3D
from rsMap3D.gui.input.specxmldrivenfileform import SpecXMLDrivenFileForm
from rsMap3D.gui.output.processvtioutputform import ProcessVTIOutputForm
from rsMap3D.gui.output.processimagestackform import ProcessImageStackForm
from PyQt5.QtWidgets import QAbstractButton

class S33SpecScanFileForm(SpecXMLDrivenFileForm):
    '''
    This class presents information for selecting input files
    '''

    FORM_TITLE = "Sector 33 Spec/XML Setup"

    #UPDATE_PROGRESS_SIGNAL = "updateProgress"
    # Regular expressions for string validation
    PIX_AVG_REGEXP_1 =  "^(\d*,*)+$"
    PIX_AVG_REGEXP_2 =  "^((\d)+,*){2}$"
    #Strings for Text Widgets
    
    NONE_RADIO_NAME = "None"
    BAD_PIXEL_RADIO_NAME = "Bad Pixel File"
    FLAT_FIELD_RADIO_NAME = "Flat Field Correction"
    
    @staticmethod
    def createInstance(parent=None, appConfig=None):
        return S33SpecScanFileForm(parent = parent, appConfig=appConfig)
        
    def __init__(self, **kwargs):
        '''
        Constructor - Layout Widgets on the page and link actions
        '''
        logger.debug(METHOD_ENTER_STR)
        super(S33SpecScanFileForm, self).__init__(**kwargs)

        #Initialize parameters
        self.projectionDirection = [0,0,1]
        
        #Initialize a couple of widgets to do setup.
        self.noFieldRadio.setChecked(True)
        self._fieldCorrectionTypeChanged(*(self.noFieldRadio,))
        logger.debug(METHOD_EXIT_STR)
        
    @qtCore.pyqtSlot()
    def _badPixelFileChanged(self):
        '''
        Do some verification when the bad pixel file changes
        '''
        logger.debug(METHOD_ENTER_STR)
        if os.path.isfile(self.badPixelFileTxt.text()) or \
           self.badPixelFileTxt.text() == EMPTY_STR:
            self.checkOkToLoad()
        else:
            message = qtWidgets.QMessageBox()
            message.warning(self, \
                            WARNING_STR, \
                             "The filename entered for the bad pixel " + \
                             "file is invalid")
        logger.debug(METHOD_EXIT_STR)
            
                
    @qtCore.pyqtSlot()
    def _browseBadPixelFileName(self):
        '''
        Launch file browser for bad pixel file
        '''
        logger.debug(METHOD_ENTER_STR)
        if self.badPixelFileTxt.text() == EMPTY_STR:
            fileName = qtWidgets.QFileDialog.getOpenFileName(None, \
                                               SELECT_BAD_PIXEL_TITLE, \
                                               filter=BAD_PIXEL_FILE_FILTER)[0]
        else:
            fileDirectory = os.path.dirname(str(self.badPixelFileTxt.text()))
            fileName = qtWidgets.QFileDialog.getOpenFileName(None, \
                                               SELECT_BAD_PIXEL_TITLE, \
                                               filter=BAD_PIXEL_FILE_FILTER, \
                                               directory = fileDirectory)[0]
        if fileName != EMPTY_STR:
            self.badPixelFileTxt.setText(fileName)
            self.badPixelFileTxt.editingFinished.emit()
        logger.debug(METHOD_EXIT_STR)

    @qtCore.pyqtSlot()
    def _browseFlatFieldFileName(self):
        '''
        Launch file browser for Flat field file
        '''
        logger.debug(METHOD_ENTER_STR)
        if self.flatFieldFileTxt.text() == EMPTY_STR:
            fileName = qtWidgets.QFileDialog.getOpenFileName(None, \
                                               SELECT_FLAT_FIELD_TITLE, \
                                               filter=TIFF_FILE_FILTER)[0]
        else:
            fileDirectory = os.path.dirname(str(self.flatFieldFileTxt.text()))
            fileName = qtWidgets.QFileDialog.getOpenFileName(None, 
                                               SELECT_FLAT_FIELD_TITLE, 
                                               filter=TIFF_FILE_FILTER, \
                                               directory = fileDirectory)[0]
        if fileName != EMPTY_STR:
            self.flatFieldFileTxt.setText(fileName)
            self.flatFieldFileTxt.editingFinished.emit()
        logger.debug(METHOD_EXIT_STR)
    
    def checkOkToLoad(self):
        '''
        Make sure we have valid file names for project, instrument config, 
        and the detector config.  If we do enable load button.  If not disable
        the load button
        '''
        logger.debug(METHOD_ENTER_STR)
        retVal = False
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
        self.okToLoad.emit(retVal)
        logger.debug(METHOD_EXIT_STR)
        return retVal
    
    def _createControlBox(self):
        '''
        Create Layout holding controls widgets
        '''
        logger.debug(METHOD_ENTER_STR)
        controlBox = super(S33SpecScanFileForm, self)._createControlBox()
        logger.debug(METHOD_EXIT_STR)
        return controlBox
    
    def _createDataBox(self):
        '''
        Create widgets for collecting data
        '''
        logger.debug(METHOD_ENTER_STR)
        dataBox = super(S33SpecScanFileForm, self)._createDataBox()
        dataLayout = dataBox.layout()
        row = dataLayout.rowCount()
        self._createInstConfig(dataLayout, row)
        
        row = dataLayout.rowCount() + 1
        self._createDetConfig(dataLayout, row)

        row = dataLayout.rowCount() + 1
        self.fieldCorrectionGroup = qtWidgets.QButtonGroup(self)
        self.noFieldRadio = qtWidgets.QRadioButton(self.NONE_RADIO_NAME)
        self.badPixelRadio = qtWidgets.QRadioButton(self.BAD_PIXEL_RADIO_NAME)
        self.flatFieldRadio = qtWidgets.QRadioButton(self.FLAT_FIELD_RADIO_NAME)
        self.fieldCorrectionGroup.addButton(self.noFieldRadio, 1)
        self.fieldCorrectionGroup.addButton(self.badPixelRadio, 2)
        self.fieldCorrectionGroup.addButton(self.flatFieldRadio, 3)
        self.badPixelFileTxt = qtWidgets.QLineEdit()
        self.flatFieldFileTxt = qtWidgets.QLineEdit()
        self.badPixelFileBrowseButton = qtWidgets.QPushButton(BROWSE_STR)
        self.flatFieldFileBrowseButton = qtWidgets.QPushButton(BROWSE_STR)

        
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
        label = qtWidgets.QLabel("Number of Pixels To Average:");
        self.pixAvgTxt = qtWidgets.QLineEdit("1,1")
        rxAvg = qtCore.QRegExp(self.PIX_AVG_REGEXP_1)
        self.pixAvgTxt.setValidator(qtGui.QRegExpValidator(rxAvg,self.pixAvgTxt))
        dataLayout.addWidget(label, row, 0)
        dataLayout.addWidget(self.pixAvgTxt, row, 1)

        row = dataLayout.rowCount() + 1
        self._createDetectorROIInput(dataLayout, row)

        row = dataLayout.rowCount() + 1
        self._createScanNumberInput(dataLayout, row)
        
        row = dataLayout.rowCount() + 1
        self._createOutputType(dataLayout, row)

        row = dataLayout.rowCount() + 1
        self._createHKLOutput(dataLayout, row)

        # Add Signals between widgets
        self.fieldCorrectionGroup.buttonClicked\
            .connect(self._fieldCorrectionTypeChanged)

        self.badPixelFileTxt.editingFinished.connect(self._badPixelFileChanged)
        self.badPixelFileBrowseButton.clicked\
            .connect(self._browseBadPixelFileName)

        self.flatFieldFileTxt.editingFinished\
            .connect(self._flatFieldFileChanged)
        self.flatFieldFileBrowseButton.clicked.\
            connect(self._browseFlatFieldFileName)
        
        self.pixAvgTxt.textChanged.connect(self._pixAvgTxtChanged)
        
        dataBox.setLayout(dataLayout)
        logger.debug(METHOD_EXIT_STR)
        return dataBox
    
    @qtCore.pyqtSlot(QAbstractButton)
    def _fieldCorrectionTypeChanged(self, *fieldCorrType):
        '''
        React when the field type radio buttons change.  Disable/Enable other 
        widgets as appropriate
        '''
        logger.debug(METHOD_ENTER_STR)
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
        logger.debug(METHOD_EXIT_STR)
            
    @qtCore.pyqtSlot()           
    def _flatFieldFileChanged(self):
        '''
        Do some verification when the flat field file changes
        '''
        logger.debug(METHOD_ENTER_STR)
        if os.path.isfile(self.flatFieldFileTxt.text()) or \
           self.flatFieldFileTxt.text() == "":
            self.checkOkToLoad()
        else:
            message = qtWidgets.QMessageBox()
            message.warning(self, \
                            WARNING_STR, \
                             "The filename entered for the flat field " + \
                             "file is invalid")
        logger.debug(METHOD_EXIT_STR)
                
    def getBadPixelFileName(self):
        '''
        Return the badPixel file name.  If empty or if the bad pixel radio 
        button is not checked return None
        '''
        logger.debug(METHOD_ENTER_STR)
        retVal = None
        if (str(self.badPixelFileTxt.text()) == EMPTY_STR) or \
           (not self.badPixelRadio.isChecked()):
            retVal = None
        else:
            retVal = str(self.badPixelFileTxt.text())
        logger.debug("Exit " + str(retVal))
        return retVal
        
    def getDataSource(self):
        logger.debug(METHOD_ENTER_STR)
        if self.getOutputType() == self.SIMPLE_GRID_MAP_STR:
            self.transform = UnityTransform3D()
        elif self.getOutputType() == self.POLE_MAP_STR:
            self.transform = \
                PoleMapTransform3D(projectionDirection=\
                                   self.getProjectionDirection())
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
                                      self.getFlatFieldFileName(), \
                                   appConfig = self.appConfig
                                  )
        self.dataSource.setProgressUpdater(self.updateProgress)
        self.dataSource.setCurrentDetector(self.currentDetector)
        self.dataSource.loadSource(mapHKL = self.getMapAsHKL())
        logger.debug(METHOD_EXIT_STR)
        return self.dataSource
        
    def getFlatFieldFileName(self):
        '''
        Return the flat field file name.  If empty or if the bad pixel radio 
        button is not checked return None
        '''
        logger.debug(METHOD_ENTER_STR)
        retVal = None
        if (str(self.flatFieldFileTxt.text()) == EMPTY_STR) or \
           (not self.flatFieldRadio.isChecked()):
            retVal = None
        else:
            retVal = str(self.flatFieldFileTxt.text())
        logger.debug(METHOD_EXIT_STR)
        return retVal
        
    def getOutputForms(self):
        logger.debug(METHOD_ENTER_STR)
        outputForms = []
        outputForms.append(ProcessVTIOutputForm)
        outputForms.append(ProcessImageStackForm)
        outputForms.append(ProcessPowderScanForm)
        logger.debug(METHOD_EXIT_STR)
        return outputForms
    
    def getPixelsToAverage(self):
        '''
        :return: the pixels to average as a list
        '''
        logger.debug(METHOD_ENTER_STR)
        pixelStrings = str(self.pixAvgTxt.text()).split(COMMA_STR)
        pixels = []
        for value in pixelStrings:
            pixels.append(int(value))
        logger.debug(METHOD_EXIT_STR)
        return pixels
    
    def getProjectionDirection(self):
        '''
        Return projection direction for stereographic projections
        '''
        logger.debug(METHOD_ENTER_STR)
        logger.debug(METHOD_EXIT_STR)
        return self.projectionDirection
          
            
    def _pixAvgTxtChanged(self, text):
        '''
        Check to make sure the text for pix to average is valid and indicate 
        by a color change 
        :param text: new values as a text list 
        '''
        logger.debug(METHOD_ENTER_STR)
        if self.pixAvgValid(text):
            self.pixAvgTxt.setStyleSheet(QLINEEDIT_COLOR_STYLE % BLACK)
        else: 
            self.pixAvgTxt.setStyleSheet(QLINEEDIT_COLOR_STYLE % RED)
        self.checkOkToLoad()
        logger.debug(METHOD_EXIT_STR)
            
    def pixAvgValid(self, text):
        '''
        Check to make sure that the pixAvgText is valid
        :param text: new values as a text list 
        '''
        logger.debug(METHOD_ENTER_STR)
        retVal = False
        rxPixAvg = qtCore.QRegExp(self.PIX_AVG_REGEXP_2)
        validator = qtGui.QRegExpValidator(rxPixAvg, None)
        pos = 0
        if validator.validate(text, pos)[0] == qtGui.QValidator.Acceptable:
            retVal = True
        else:
            retVal = False
        logger.debug("Exit " + str(retVal))
        return retVal
