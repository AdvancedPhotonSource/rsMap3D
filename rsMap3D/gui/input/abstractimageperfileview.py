'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import PyQt4.QtGui as qtGui
import PyQt4.QtCore as qtCore
from rsMap3D.gui.input.abstractfileview import AbstractFileView

class AbstractImagePerFileView(AbstractFileView):
    '''
    classdocs
    '''


    def __init__(self, parent=None):
        '''
        Constructor
        '''
        super(AbstractImagePerFileView, self).__init__(parent)