'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''

from PyQt4.QtCore import *
from PyQt4.QtGui import QDialog
from PyQt4.QtGui import QGridLayout
from PyQt4.QtGui import QLabel
from PyQt4.QtGui import QLineEdit
from PyQt4.QtGui import QPushButton

class FileForm(QDialog):
    def __init__(self,parent=None):
        '''
        '''
        super(FileForm, self).__init__(parent)
        layout = QGridLayout()

        label = QLabel("Project Directory:");
        self.projDirTxt = QLineEdit()
        layout.addWidget(label, 0, 0)
        layout.addWidget(self.projDirTxt, 0, 1)

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
        
        
        loadButton = QPushButton("Load")        
        layout.addWidget(loadButton,4 , 1)
        
        self.connect(loadButton, SIGNAL("clicked()"), self.loadFile)
        self.connect(self.instConfigFileButton, SIGNAL("clicked()"), 
                     self.browseForInstFile)
        self.connect(self.detConfigFileButton, SIGNAL("clicked()"), 
                     self.browseForDetFile)
        
        self.setLayout(layout);
        
    def loadFile(self):
        '''
        '''
        self.emit(SIGNAL("loadFile"))
        
    def browseForInstFile(self):
        '''
        '''
        print "Browsing for inst file"

    def browseForDetFile(self):
        '''
        '''
        print "Browsing for Det file"

    def getDetConfigName(self):
        '''
        '''
        return self.detConfigTxt.text()

    def getInstConfigName(self):
        '''
        '''
        return self.instConfigTxt.text()

    def getProjectDir(self):
        '''
        '''
        return self.projDirTxt.text()
        
    def getProjectName(self):
        '''
        '''
        return self.projNameTxt.text()
    
