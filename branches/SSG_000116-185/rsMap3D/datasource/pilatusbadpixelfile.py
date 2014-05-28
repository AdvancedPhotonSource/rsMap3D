'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
import csv
from rsMap3D.exception.rsmap3dexception import RSMap3DException

class BadPixel(object):
    '''
    Class to define a bad pixel and a pixel whose value should replace the 
    value in the bad pixel.  Note that this assumes that the replacement pixel
    has a value similar to what the bad pixel should have.
    '''
    def __init__(self, badX, badY, replacementX, replacementY):
        self.badX = badX
        self.badY = badY
        self.replacementX = replacementX
        self.replacementY = replacementY
        
    def getBadLocation(self):
        '''
        Return the location of the Bad pixel
        '''
        return (self.badX, self.badY)
    
    def getReplacementLocation(self):
        '''
        Return the value of the replacement pixel
        '''
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
        '''
        Return the number of bad pixels defined in the file
        '''
        return len(self.badPixels)
    
    def getBadPixels(self):
        '''
        Return a list of BadPixel objects.
        '''
        return self.badPixels