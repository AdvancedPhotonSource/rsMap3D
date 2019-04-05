'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
from configparser import ConfigParser
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
MPI_SECTION_NAME = "MPI"
MPI_HOST_FILE = "hostfile"
MPI_WORKER_COUNT = "workercount"
MPI_DEFAULT_HOST = "worker_hosts"
MPI_DEFAULT_WORKER_COUNT = '1'

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
                with open(self.configFile, 'w') as configFile:
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
        self.add_section(MPI_SECTION_NAME)
        self.set(MPI_SECTION_NAME, MPI_HOST_FILE, MPI_DEFAULT_HOST)
        self.set(MPI_SECTION_NAME, MPI_WORKER_COUNT, MPI_DEFAULT_WORKER_COUNT)
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
        maxMemory = self.getint(MEMORY_SECTION_NAME, MAX_IMAGE_MEMORY)
        logger.debug("MaxMemory Value %d" % maxMemory)
        return maxMemory
    
    def getMPIWorkerHostFile(self, default="worker_hosts"):
        hostFile = None
        sections = self.sections()
        logger.debug("Sections %s" % str((sections,)))
        try:
            if MPI_SECTION_NAME in sections:
                hostFile = self.get(MPI_SECTION_NAME, MPI_HOST_FILE)
                logger.debug("MPI HostFile %s" % str(hostFile))
            else:
                logger.warning("MPI Section not found in app config file\n" +
                               "default section looks like\n" +
                               "[MPI]\n"
                               "HostFile = worker_hosts\n"
                               "WorkerCount = 1\n"
                               )
                hostFile = MPI_DEFAULT_HOST 
        except Exception as ex:
            logger.error("No MPI_HOST_FILE found using defaut; %s" % \
                str(MPI_DEFAULT_HOST))
            logger.exception(ex.message)
            hostFile = MPI_DEFAULT_HOST
        return hostFile
            
    def getMPIWorkerCount(self, default=1):
        workerCount = 1
        try:
            mpiSections = self.sections()
            if MPI_SECTION_NAME in mpiSections:
                #mpiSection = self.sections()[MPI_SECTION_NAME]
                workerCount = self.getint(MPI_SECTION_NAME, \
                                                MPI_WORKER_COUNT)
                logger.debug("MPI Worker count %d" % workerCount)
            else:
                logger.warning("MPI Section not found in app config file\n" +
                               "default section looks like\n" +
                               "[MPI]\n"
                               "HostFile = worker_hosts\n"
                               "WorkerCount = 1\n"
                               )
                workerCount = MPI_DEFAULT_WORKER_COUNT
        except Exception as ex:
            workerCount = 1
            logger.exception(ex.message)
        return workerCount    
        