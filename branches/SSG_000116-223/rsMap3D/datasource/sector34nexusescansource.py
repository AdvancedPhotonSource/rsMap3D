'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
from rsMap3D.exception.rsmap3dexception import DetectorConfigException,\
    RSMap3DException
from rsMap3D.datasource.Sector33SpecDataSource import LoadCanceledException
from rsMap3D.gui.rsm3dcommonstrings import CANCEL_STR
import h5py
from rsMap3D.datasource.abstractDataSource import AbstractDataSource
from rsMap3D.datasource.DetectorGeometry.detectorgeometryforescan \
    import DetectorGeometryForEScan
import math
import numpy as np
import glob
import os
import string

H5_INCIDENT_ENERGY = '/entry1/sample/incident_energy'
H5_ROI_START_X = '/entry1/detector/startx'
H5_ROI_START_Y = '/entry1/detector/starty'
H5_ROI_END_X = '/entry1/detector/endx'
H5_ROI_END_Y = '/entry1/detector/endy'
H5_IMAGE = '/entry1/data/data'

class Sector34NexusEscanSource(AbstractDataSource):
    '''
    '''
    
    def __init__(self, \
                 projectDir, \
                 projectName, \
                 projectExtension,
                 detConfigFile,
                 detectorId="PE1621 723-3335",
                 **kwargs):
        '''
        '''
        super(Sector34NexusEscanSource, self).__init__()
        self.projectDir = str(projectDir)
        self.projectName = str(projectName)
        self.projectExtension = str(projectExtension)
        self.detConfigFile = str(detConfigFile)
        self.detectorId = detectorId
        self.files = None
        self.availableFiles = []
        self.detectorROI = []
        self.incidentEnergy = {}
        self.progressUpdater = None
        self.progress = 0
        self.progressMax = 1
        self.cancelLoad = False
        
        

    def findImageQs(self):
        (qx,qy, qz) = self.qsForDetector()
        idx = range(len(qx))
        xmin = [np.min(qx[i]) for i in idx]
        xmax = [np.max(qx[i]) for i in idx]
        ymin = [np.min(qy[i]) for i in idx]
        ymax = [np.max(qy[i]) for i in idx]
        zmin = [np.min(qz[i]) for i in idx]
        zmax = [np.max(qz[i]) for i in idx]
        return (xmin, xmax, ymin, ymax, zmin, zmax)
                     
    def findScanQs(self, xmin, xmax, ymin, ymax, zmin, zmax):
        '''
        find the overall boundaries for a scan given the min/max boundaries
        of each image in the scan
        '''
        scanXmin = np.min( xmin)
        scanXmax = np.max( xmax)
        scanYmin = np.min( ymin)
        scanYmax = np.max(  ymax)
        scanZmin = np.min(  zmin)
        scanZmax = np.max(  zmax)
        return scanXmin, scanXmax, scanYmin, scanYmax, scanZmin, scanZmax

    def getImageToBeUsed(self):
        '''
        Return a dictionary containing list of images to be used in each scan.
        '''
        return self.imageToBeUsed
     
    def getReferenceNames(self):
        names = []
        names.append("Energy (keV)")
        return names
    
    def getReferenceValues(self, scan):
        
        values = []
        for energy in self.incidentEnergy.values():
            values.append([energy,]) 
        return values

    def loadSource(self):
        try:
            self.detConfig = DetectorGeometryForEScan(self.detConfigFile)
            self.detector = self.detConfig.getDetectorById(self.detectorId)
            self.detectorDimensions = \
                self.detConfig.getNpixels(self.detector)
            self.detectorSize = self.detConfig.getSize(self.detector)
            self.detectorPixelWidth = \
                [self.detectorSize[0]/self.detectorDimensions[0],\
                 self.detectorSize[1]/self.detectorDimensions[1]]
            self.detectorRotation = self.detConfig.getRotation(self.detector)   
            self.detectorTranslation = \
                self.detConfig.getTranslation(self.detector)  
            Rx = self.detectorRotation[0]
            Ry = self.detectorRotation[1]
            Rz = self.detectorRotation[2]    
            theta = math.sqrt(Rx*Rx+Ry*Ry+Rz*Rz) 
            
            if theta == 0:
                self.rho = np.array[[1,0,0],[0,1,0],[001]]
            else:
                c = math.cos(theta)
                s = math.sin(theta)
                c1 = 1 - c
                Rx /= theta      # normalize to unit vector
                Ry /= theta
                Rz /= theta 
                
                self.rho = \
                    np.array([[c + Rx*Rx*c1, Rx*Ry*c1 - Rz*s, Ry*s + Rx*Rz*c1],\
                              [Rz*s + Rx*Ry*c1, c + Ry*Ry*c1, -Rx*s + Ry*Rz*c1],\
                              [-Ry*s + Rx*Rz*c1,Rx*s + Ry*Rz*c1, c + Rz*Rz*c1]])
                self.rho2 = \
                    np.array([[c + Rx*Rx*c1, Rz*s + Rx*Ry*c1, Ry*s + Rx*Rz*c1],\
                              [Rx*Ry*c1 - Rz*s, c + Ry*Ry*c1,  Rx*s + Ry*Rz*c1],\
                              [Ry*s + Rx*Rz*c1,-Rx*s + Ry*Rz*c1, c + Rz*Rz*c1]])
                
        except DetectorConfigException as ex:
            print ("--Error Reading detectorConfig")
            raise ex
        except Exception as ex:
            print ("---Unhandled Exception in loading detector config")
            raise ex

        
        if self.files == None:
            fileFilter = str(os.path.join(self.projectDir, string.rsplit(self.projectName, '_',1)[0])) + \
                         "_[0-9]*" + \
                         self.projectExtension
                         
            fileList = glob.glob(fileFilter)
        if fileList == []:
                raise RSMap3DException("No files Found matching " + fileFilter)
        self.files = range(1,len(fileList)+1)

        if self.progressUpdater <> None:
            self.progressUpdater(self.progress, self.progressMax)
        for afile in self.files:
            if (self.cancelLoad):
                self.cancelLoad = False
                raise LoadCanceledException(CANCEL_STR)
            else:
                filename = os.path.join(self.projectDir, \
                               string.rsplit(self.projectName, '_', 1)[0]) + \
                               '_' + \
                               str(afile) + \
                               self.projectExtension
                #print filename
                if os.path.exists(filename):
                    #curScan = self.sd[afile]
                    self.availableFiles.append(afile)
                    try:
                        hdfFile = h5py.File(filename, "r")
                        self.incidentEnergy[afile] = \
                            hdfFile[H5_INCIDENT_ENERGY].value[0]
                        self.detectorROI = \
                            [hdfFile[H5_ROI_START_X].value[0], \
                             hdfFile[H5_ROI_END_X].value[0], \
                             hdfFile[H5_ROI_START_Y].value[0], \
                             hdfFile[H5_ROI_END_Y].value[0]]
                        hdfFile.close()
                    except Exception:
                        print "Trouble Opening File" + filename
        #print self.incidentEnergy
        self.imageBounds[1] = self.findImageQs()
        #print "ImageBounds: " + str(self.imageBounds)
        self.availableScans.append(1)
            
    def pixel2XYZ(self, pixelX, pixelY):
        
        xp = (pixelX - 0.5*(self.detectorDimensions[0])-1) * \
            self.detectorPixelWidth[0]
        yp = (pixelY - 0.5*(self.detectorDimensions[1])-1) * \
            self.detectorPixelWidth[1]
            
        xp += self.detectorTranslation[0]
        yp += self.detectorTranslation[1]
        zp = self.detectorTranslation[2]
        xyz = [(self.rho[0][0]*xp + self.rho[0][1]*yp + self.rho[0][2]*zp), \
               (self.rho[1][0]*xp + self.rho[1][1]*yp + self.rho[1][2]*zp), \
               (self.rho[2][0]*xp + self.rho[2][1]*yp + self.rho[2][2]*zp)]
        return xyz
    
    def pixel2q(self, pixelX, pixelY, qhat, depth=0):
        ki = [0, 0, 1]
        
        kout = self.pixel2XYZ(pixelX, pixelY)
        
        if depth != 0:
            kout -= depth*ki
        koutnorm = np.linalg.norm(kout)
        if koutnorm != 0:
            kout /= koutnorm 
        
        qhat = kout-ki
#         qhatnorm = np.linalg.norm(qhat)
#         if qhatnorm != 0:
#             qhat /= qhatnorm
        #print "qhat " + str(qhat)
        return qhat
    
    def qsForDetector(self):            
        #print self.detectorROI
        xIndexArray =  range(self.detectorROI[0], self.detectorROI[1]+1)
        yIndexArray =  range(self.detectorROI[2], self.detectorROI[3]+1)
        qx = np.zeros([len(self.availableFiles), \
                       len(xIndexArray), \
                       len(yIndexArray)])
        qy = np.zeros([len(self.availableFiles), \
                       len(xIndexArray), \
                       len(yIndexArray)])
        qz = np.zeros([len(self.availableFiles), \
                       len(xIndexArray), \
                       len(yIndexArray)])
        qpx = np.zeros([len(yIndexArray), \
                       len(xIndexArray)])
        qpy = np.zeros([len(yIndexArray), \
                       len(xIndexArray)])
        qpz = np.zeros([len(yIndexArray), \
                       len(xIndexArray)])
        #print xIndexArray, yIndexArray
        for row in yIndexArray:
            for column in xIndexArray:
                startx = self.detectorROI[0]
                starty = self.detectorROI[2]
                qForPixel = self.pixel2q(column, row,None)
                qpx[row-starty][column-startx] = qForPixel[0]
                qpy[row-starty][column-startx] = qForPixel[1]
                qpz[row-starty][column-startx] = qForPixel[2]
        for afile in self.availableFiles:
            twoPiOverLamda = 2*np.pi * self.incidentEnergy[afile] / 1.23985
            qx[afile-1,:,:] = qpx * twoPiOverLamda 
            qy[afile-1,:,:] = qpy * twoPiOverLamda 
            qz[afile-1,:,:] = qpz * twoPiOverLamda 
#        print(qx)
#        print(qy)
#        print(qz)
        return qx, qy, qz

    def rawmap(self,scans, angdelta=[0,0,0,0,0],
            adframes=None, mask = None):
        qx, qy, qz = self.qsForDetector()
        intensity = np.array([])
        arrayInitializedForScan = False
        offset=0
        foundIndex = 0
        self.availableFiles.sort()
        #print "availableFiles:" + str(self.availableFiles)
        for afile in self.availableFiles:
            filename = os.path.join(self.projectDir, \
                           string.rsplit(self.projectName, '_', 1)[0]) + \
                           '_' + \
                           str(afile) + \
                           self.projectExtension
            hdfFile = h5py.File(filename, "r")
            img = \
                hdfFile[H5_IMAGE].value
            #print ("Image: " + str(img))
            if not arrayInitializedForScan:
                if not intensity.shape[0]:
                    intensity = np.zeros((len(self.availableFiles),) + img.shape)
                    arrayInitializedForScan = True
                else: 
                    offset = intensity.shape[0]
                    intensity = np.concatenate(
                        (intensity,
                        (np.zeros((np.count_nonzero(len(self.availableFiles)),) + img.shape))),
                        axis=0)
                    arrayInitializedForScan = True
            intensity[foundIndex+offset,:,:] = img
            foundIndex += 1
            
            hdfFile.close()
        
        return qx, qy, qz, intensity
