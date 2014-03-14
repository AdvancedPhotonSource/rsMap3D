'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
import os
from PyQt4.QtCore import *
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QMessageBox

class FileForm(QDialog):
    '''
    This class presents information for selecting input files
    '''
    def __init__(self,parent=None):
        '''
        Constructor - Layout Widgets on the page and link actions
        '''
        super(FileForm, self).__init__(parent)
        layout = QGridLayout()

        label = QLabel("Project Directory:");
        self.projDirTxt = QLineEdit()
        self.projectDirButton = QPushButton("Browse")
        layout.addWidget(label, 0, 0)
        layout.addWidget(self.projDirTxt, 0, 1)
        layout.addWidget(self.projectDirButton, 0, 2)

        label = QLabel("Project Name:");
        self.projNameTxt = QLineEdit()
        layout.addWidget(label, 1, 0)
        layout.addWidget(self.projNameTxt, 1, 1)

        label = QLabel("Instrument Config File:");
        self.instConfigTxt = QLineEdit()
        self.instConfigFileButton = QPushButton("Browse")
        layout.addWidget(label, 2, 0)
        layout.addWidget(self.instConfigTxt, 2, 1)
        layout.addWidget(self.instConfigFileButton, 2, 2)
        label = QLabel("Detector Config File:");
        self.detConfigTxt = QLineEdit()
        self.detConfigFileButton = QPushButton("Browse")
        layout.addWidget(label, 3, 0)
        layout.addWidget(self.detConfigTxt, 3, 1)
        layout.addWidget(self.detConfigFileButton, 3, 2)
        
        
        self.loadButton = QPushButton("Load")        
        self.loadButton.setDisabled(True)
        layout.addWidget(self.loadButton,4 , 1)
        
        self.connect(self.loadButton, SIGNAL("clicked()"), self.loadFile)
        self.connect(self.projectDirButton, SIGNAL("clicked()"), 
                     self.browseForProjectDir)
        self.connect(self.instConfigFileButton, SIGNAL("clicked()"), 
                     self.browseForInstFile)
        self.connect(self.detConfigFileButton, SIGNAL("clicked()"), 
                     self.browseForDetFile)
        self.connect(self.projDirTxt, 
                     SIGNAL("editingFinished()"), 
                     self.projectDirChanged)
        self.connect(self.projNameTxt, 
                     SIGNAL("editingFinished()"), 
                     self.projectNameChanged)
        self.connect(self.instConfigTxt, 
                     SIGNAL("editingFinished()"), 
                     self.instConfigChanged)
        self.connect(self.detConfigTxt, 
                     SIGNAL("editingFinished()"), 
                     self.detConfigChanged)
        
        self.setLayout(layout);
        
    def loadFile(self):
        '''
        Emit a signal to start loading data
        '''
        self.emit(SIGNAL("loadFile"))
        
    def browseForInstFile(self):
        '''
        Launch file selection dialog for instrument file.
        '''
        fileName = QFileDialog.getOpenFileName(None, 
                                               "Select Instrument Config File", 
                                               filter="*.xml")
        self.instConfigTxt.setText(fileName)
        self.instConfigTxt.emit(SIGNAL("editingFinished()"))

    def browseForDetFile(self):
        '''
        Launch file selection dialog for Detector file.
        '''
        fileName = QFileDialog.getOpenFileName(None, 
                                               "Select Detector Config File", 
                                               filter="*.xml")
        self.detConfigTxt.setText(fileName)
        self.detConfigTxt.emit(SIGNAL("editingFinished()"))

    def browseForProjectDir(self):
        '''
        Launch file selection dialog for instrument file.
        '''
        dirName = QFileDialog.getExistingDirectory(None,
                                                   QString())
        self.projDirTxt.setText(dirName)
        self.projDirTxt.emit(SIGNAL("editingFinished()"))


    def getDetConfigName(self):
        '''
        Return the selected Detector Configuration file
        '''
        return self.detConfigTxt.text()

    def getInstConfigName(self):
        '''
        Return the Instrument config file name
        '''
        return self.instConfigTxt.text()

    def getProjectDir(self):
        '''
        Return the project directory
        '''
        return self.projDirTxt.text()
        
    def getProjectName(self):
        '''
        Return the project name
        '''
        return self.projNameTxt.text()
    
    def projectDirChanged(self):
        if os.path.isdir(self.projDirTxt.text()):
            self.checkOkToLoad()
        else:
            message = QMessageBox()
            message.warning(self, \
                             "Warning", \
                             "The project directory entered is invalid")
        
    def projectNameChanged(self):
        print "2"
        self.checkOkToLoad()
        
    def instConfigChanged(self):
        if os.path.isfile(self.instConfigTxt.text()):
            self.checkOkToLoad()
        else:
            message = QMessageBox()
            message.warning(self, \
                            "Warning", \
                             "The filename entered for the instrument " + \
                             "configuration is invalid")
        
    def detConfigChanged(self):
        if os.path.isfile(self.detConfigTxt.text()):
            self.checkOkToLoad()
        else:
            message = QMessageBox()
            message.warning(self, \
                             "Warning"\
                             "The filename entered for the detector " + \
                             "configuration is invalid")
        
    def checkOkToLoad(self):
        if os.path.isdir(self.projDirTxt.text()) and \
            os.path.isfile(self.instConfigTxt.text()) and \
            os.path.isfile(self.detConfigTxt.text()) and \
            self.projNameTxt.text() != "":
            self.loadButton.setEnabled(True)
        else:
            self.loadButton.setDisabled(True)