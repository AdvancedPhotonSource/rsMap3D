'''
Created on May 28, 2014

@author: hammonds
'''
import csv
from rsMap3D.exception.rsmap3dexception import RSMap3DException

class BadPixel(object):
    def __init__(self, badX, badY, replacementX, replacementY):
        self.badX = badX
        self.badY = badY
        self.replacementX = replacementX
        self.replacementY = replacementY
        
    def getBadLocation(self):
        return (self.badX, self.badY)
    
    def getReplacementLocation(self):
        return (self.replacementX, self.replacementY)
    
class PilatusBadPixelFile(object):
    '''
    Bad Pixel file described at 
    http://cars.uchicago.edu/software/epics/pilatusDoc.html
    '''


    def __init__(self, fileName):
        '''
        Constructor
        '''
        self.badPixelFile = fileName
        reader = csv.reader(open(self.badPixelFile), \
                            delimiter=' ', \
                            skipinitialspace=True) 
        self.badPixels = []
        for line in reader:
            try:
                badP = line[0].split(',')
                replaceP = line[1].split(',')
                self.badPixels.append(BadPixel(int(badP[0]), \
                                       int(badP[1]), \
                                       int(replaceP[0]), \
                                       int(replaceP[1])))
            except (IndexError, ValueError):
                raise RSMap3DException( "Error in bad Pixel file at " + \
                                        str(line) + \
                                        "  Format is at Line " + \
                                        str(reader.line_num) + \
                                        " badX1,badY1 replacementX1,replacementY1")

        print self.badPixels
        
    def getNumPixels(self):
        return len(self.badPixels)
    
    def getBadPixels(self):
        return self.badPixels