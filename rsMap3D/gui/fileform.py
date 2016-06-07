'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import os

import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore

from rsMap3D.gui.rsm3dcommonstrings import WARNING_STR, BROWSE_STR,\
    COMMA_STR, QLINEEDIT_COLOR_STYLE, BLACK, RED, EMPTY_STR,\
    BAD_PIXEL_FILE_FILTER, SELECT_BAD_PIXEL_TITLE, SELECT_FLAT_FIELD_TITLE,\
    TIFF_FILE_FILTER
from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource
from rsMap3D.transforms.unitytransform3d import UnityTransform3D
from rsMap3D.transforms.polemaptransform3d import PoleMapTransform3D
from rsMap3D.gui.input.specxmldrivenfileform import SpecXMLDrivenFileForm
from rsMap3D.gui.qtsignalstrings import BUTTON_CLICKED_SIGNAL, CLICKED_SIGNAL, \
    EDIT_FINISHED_SIGNAL, TEXT_CHANGED_SIGNAL


class FileForm(SpecXMLDrivenFileForm):
    '''
    This class presents information for selecting input files
    '''
    #UPDATE_PROGRESS_SIGNAL = "updateProgress"
    # Regular expressions for string validation
    PIX_AVG_REGEXP_1 =  "^(\d*,*)+$"
    PIX_AVG_REGEXP_2 =  "^((\d)+,*){2}$"
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
        self.projectionDirection = [0,0,1]
        
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
        return controlBox
    
    def _createDataBox(self):
        '''
        Create widgets for collecting data
        '''
        dataBox = super(FileForm, self)._createDataBox()
        dataLayout = dataBox.layout()
        row = dataLayout.rowCount()
        self._createInstConfig(dataLayout, row)
        
        row = dataLayout.rowCount() + 1
        self._createDetConfig(dataLayout, row)

        row = dataLayout.rowCount() + 1
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

        row = dataLayout.rowCount() + 1
        self._createDetectorROIInput(dataLayout, row)

        row = dataLayout.rowCount() + 1
        self._createScanNumberInput(dataLayout, row)
        
        row = dataLayout.rowCount() + 1
        self._createOutputType(dataLayout, row)

        row = dataLayout.rowCount() + 1
        label = qtGui.QLabel("HKL output")
        dataLayout.addWidget(label, row, 0)
        self.hklCheckbox = qtGui.QCheckBox()
        dataLayout.addWidget(self.hklCheckbox, row, 1)

        # Add Signals between widgets
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
        
        dataBox.setLayout(dataLayout)
        return dataBox
    
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
        self.dataSource.setCurrentDetector(self.currentDetector)
        self.dataSource.loadSource(mapHKL = self.getMapAsHKL())
        return self.dataSource
        
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
        
