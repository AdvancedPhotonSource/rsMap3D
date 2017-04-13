'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
from ConfigParser import ConfigParser
from os.path import expanduser, join, exists
import inspect
#import rsMap3D.gui.input as input
#import rsMap3D.gui.output as rsmoutput
from rsMap3D.gui.input.abstractfileview import AbstractFileView
#from rsMap3D.gui.output.abstractoutputview import AbstractOutputView
from rsMap3D.config.rsmap3dconfig import RSMap3DConfig
import importlib
import logging
from rsMap3D.config.rsmap3dlogging import METHOD_ENTER_STR, METHOD_EXIT_STR
from rsMap3D.exception.rsmap3dexception import RSMap3DException
logger = logging.getLogger(__name__)

CONFIG_FILENAME_DEFAULT = "rsMap3D.ini"
MAX_IMAGE_MEMORY_BYTES = "100000000"
MEMORY_SECTION_NAME = "Memory"
MAX_IMAGE_MEMORY = "maxImageMemory"
INPUT_FORM_SECTION = "InputForms"
OUTPUT_FORM_SECTION = "OutputForms"

class RSMap3DConfigParser(ConfigParser):
    '''
    New class to replace the configuration done in rsmap3dconfig.  That class 
    was a homebrewed config file using XML.  This class will use Python's 
    ConfigParser class to create and maintain a more robust configuration
    '''
    
    def __init__(self, fileName="", **kwargs):
        ConfigParser.__init__(self, **kwargs)
        userDir = expanduser("~")
        if fileName == "":
            self.configFile = join(userDir, CONFIG_FILENAME_DEFAULT)
        else:
            self.configFile = fileName
        self.MaxMemory = MAX_IMAGE_MEMORY_BYTES

        try:
            if not exists(self.configFile):
                logger.debug("Could not find existing logfile " + \
                             str(self.configFile))
                self.buildDefaultConfig()
                try:
                    logger.debug("Try reading debug info from previous XML " + \
                                 "file " )

                    configFileOld = RSMap3DConfig()
                    self.MaxMemory = configFileOld.getMaxImageMemory()
                    self.set(MEMORY_SECTION_NAME, MAX_IMAGE_MEMORY, 
                             str(self.MaxMemory))
                except Exception as ex:
                    logger.debug("Trouble loading from XML file")
                with open(self.configFile, 'wb') as configFile:
                    self.write(configFile)
                with open(self.configFile, 'r') as configFile:
                    self.read(configFile)
            else:
                logger.debug("Found existing logfile " + \
                             str(self.configFile))
                self.read(self.configFile)
        except Exception as ex:
            raise RSMap3DException(str(ex))
                
    def buildDefaultConfig(self):

        logging.debug(METHOD_ENTER_STR)
        self.add_section(MEMORY_SECTION_NAME)
        self.set(MEMORY_SECTION_NAME, MAX_IMAGE_MEMORY, MAX_IMAGE_MEMORY_BYTES)
        self.add_section(INPUT_FORM_SECTION)
        module = importlib.import_module("rsMap3D.gui.input")
        inputForms = self.findFormClasses(module, AbstractFileView)
        formNum = 0
        for form in inputForms:
            logging.debug("adding form %s as Form %d" %(form, formNum))
            self.set(INPUT_FORM_SECTION, "InputForm%i" % formNum, form)
            formNum += 1
        logging.debug(METHOD_EXIT_STR)
        
    def findFormClasses(self, module, superclass):
        names = []
        for obj in inspect.getmembers(module, inspect.isclass):

            if inspect.isclass(obj[1]) and issubclass( obj[1], superclass):
                
                names.append(obj[1].__module__ + "." + obj[1].__name__)
        return names
    
    def getMaxImageMemory(self):
        logger.debug("Sections: " + str(self.sections()))
        logger.debug("Memory " + str(self.options(MEMORY_SECTION_NAME)))
        logger.debug("MaxMemory Value ", str(self.get(MEMORY_SECTION_NAME, MAX_IMAGE_MEMORY)))
        return self.getint(MEMORY_SECTION_NAME, MAX_IMAGE_MEMORY)
        