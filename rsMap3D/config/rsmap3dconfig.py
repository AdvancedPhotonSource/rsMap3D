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

NAMESPACE = '{https://subversion.xray.aps.anl.gov/RSM/rsMap3DConfig}'
MAX_IMAGE_MEMORY = NAMESPACE + "maxImageMemory"


class RSMap3DConfig():
    """
    Class to read and store configuration information for the rsMap3D 
    application
    """
    def __init__(self, fileName=""):
        if fileName == "":
            userDir = expanduser("~")
            self.configFile = join(userDir,".rsMap3D")
        else:
            self.configFile = fileName
        try:
            if not exists(self.configFile):
                self.createConfigFile()
            tree = ET.parse(self.configFile)
        except IOError as ex:
            raise (RSMap3DException("Bad config file for rsMap3D " + 
                                    str(self.configFile)))
        self.root = tree.getroot()
        
    def createConfigFile(self):
        configElement = ET.Element('rsMap3DConfig', xmlns = NAMESPACE[1:-1])
        maxIMem = ET.SubElement(configElement, 'maxImageMemory')
        maxIMem.text ="100000000"
        #ET.dump(configElement)
        tree = ET.ElementTree(configElement)
        tree.write(self.configFile,  encoding = "utf-8", xml_declaration=True, method ="xml")
        redo = minidom.parseString(ET.tostring(configElement, 'utf8'))
        print redo.toprettyxml(indent="    ")
        fileHandle = open(self.configFile, "wb")
        redo.writexml(fileHandle, indent='   ', newl='\r\n')
        fileHandle.close()
        
    def getMaxImageMemory(self):
        maxIMem = self.root.find(MAX_IMAGE_MEMORY)
        if maxIMem == None:
            raise RSMap3DException("Config file " + self.configFile + \
                                   " does not define maxImageMemory")
        try:
            return int(maxIMem.text)
        except (TypeError, ValueError):
            raise RSMap3DException("Config file " + self.configFile + \
                               " maxImageMemory does not set a number correctly")

def main():
    config = RSMap3DConfig()
    config.createConfigFile()

if __name__ == "__main__":
    main()