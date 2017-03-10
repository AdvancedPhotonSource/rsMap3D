'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.exception.rsmap3dexception import RSMap3DException
from rsMap3D.gui.rsm3dcommonstrings import COMMA_STR, SPACE_STR

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
        reader = open(self.badPixelFile) 
        self.badPixels = []
        line_num = 0
        for line in reader:
            try:
                line_num += 1
                line = line.replace(COMMA_STR, SPACE_STR)
                values = line.split()
                self.badPixels.append(BadPixel(int(values[0]), \
                                       int(values[1]), \
                                       int(values[2]), \
                                       int(values[3])))
            except (IndexError, ValueError) as ex:
                raise RSMap3DException( "Error in bad Pixel file at " + \
                                        str(line) + \
                                        "  Format is at Line " + \
                                        str(line_num) + \
                                        " badX1,badY1 replacementX1,replacementY1\n" + \
                                        str(ex))

        
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