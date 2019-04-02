'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
from os.path import expanduser 
from os.path import join
from os.path import exists
import xml.etree.ElementTree as ET
from rsMap3D.exception.rsmap3dexception import RSMap3DException
from xml.dom import minidom
import logging
logger = logging.getLogger(__name__)

NAMESPACE = '{https://subversion.xray.aps.anl.gov/RSM/rsMap3DConfig}'
MAX_IMAGE_MEMORY = NAMESPACE + "maxImageMemory"
CONFIG_FILENAME_DEFAULT = ".rsMap3D"
MAX_IMAGE_MEMORY_BYTES = "100000000"

class RSMap3DConfig():
    """
    Class to read and store configuration information for the rsMap3D 
    application
    """
    def __init__(self, fileName="", exeptionOnNoFile=False):
        if fileName == "":
            userDir = expanduser("~")
            self.configFile = join(userDir, CONFIG_FILENAME_DEFAULT)
            logger.debug("No filename given so using default name " + \
                         str(self.configFile))
        else:
            self.configFile = fileName
            logger.debug("Filename passed as argument using that " + \
                         str(self.configFile))
        try:
            if not exists(self.configFile):
                #normally this just creates a new config file.  Add allowing
                #exception when a new config bases on ConfigParser was adopted
                #This allows using an reading old config file, if it exists,
                #to set the maxMemory specified by the user.
                if not exeptionOnNoFile:
                    self.createConfigFile()
                else:
                    raise RSMap3DConfigNotFound("File " + self.configFile +
                                                " was not found")
            tree = ET.parse(self.configFile)
        except IOError as ex:
            raise (RSMap3DException("Bad config file for rsMap3D " + 
                                    str(self.configFile) + "\n" +
                                    str(ex)))
        self.root = tree.getroot()
        
    def createConfigFile(self):
        configElement = ET.Element('rsMap3DConfig', xmlns = NAMESPACE[1:-1])
        maxIMem = ET.SubElement(configElement, 'maxImageMemory')
        maxIMem.text = MAX_IMAGE_MEMORY_BYTES
        #ET.dump(configElement)
        tree = ET.ElementTree(configElement)
        tree.write(self.configFile,  encoding = "utf-8", xml_declaration=True, method ="xml")
        redo = minidom.parseString(ET.tostring(configElement, 'utf8'))
        print (redo.toprettyxml(indent="    "))
        fileHandle = open(self.configFile, "wb")
        redo.writexml(fileHandle, indent='   ', newl='\r\n')
        fileHandle.close()
        
    def getMaxImageMemory(self):
        maxIMem = self.root.find(MAX_IMAGE_MEMORY)
        if maxIMem is None:
            raise RSMap3DException("Config file " + self.configFile + \
                                   " does not define maxImageMemory")
        try:
            return int(maxIMem.text)
        except (TypeError, ValueError):
            raise RSMap3DException("Config file " + self.configFile + \
                               " maxImageMemory does not set a number correctly")

class RSMap3DConfigNotFound(RSMap3DException):
    '''
    Exception specific to not finding default RSMap3DConfig file
    '''
    def __init__(self, message):
        super(RSMap3DConfigNotFound, self).__init__(message)
        
    
def main():
    config = RSMap3DConfig()
    config.createConfigFile()

if __name__ == "__main__":
    main()