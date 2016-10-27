''' Script to analyze powder diffraction data '''

import os

#==============================================================================
# User parameters
# ---------------
#
# Modify this section according to your needs.
#
#==============================================================================

# Data files and scan selection
#projectdir = os.path.join("X:/", "data/schlepuetz/20150203/Proslier_Nb3Sn/")
projectdir = os.path.join("C:/", "Users/hammonds/RSM/s33/powderscan/")
#projectdir = os.path.join("/home/33id/", "data/lee/20160629/lcvd/")
specfile = "YSZ_FG_Pt_1.spec"

# List of scans or scan-ranges that should be processed. Each list item is
# processed as a new powder diffraction data set, but lists or string-ranges
# within list elements are combined in a single data file. List items can be
# integers, strings, string ranges, or lists.
#
# Example:
#     scan_list = ['1','2-5',20, [23,25,31]]
# This will result in four different data files containing information from 
# the following scans:
#     ..._S001.xye: Scans # 1
#     ..._S002.xye: Scans # 2,3,4,5
#     ..._S020.xye: Scans # 20
#     ..._S023.xye: Scans # 23, 25, 31
#
scan_list = ['5']

# Instrument and detector configuration files
instrument_config = os.path.join(projectdir, "33IDD_psic.xml")
detector_config = os.path.join(projectdir, "33IDD_Pilatus_psic.xml")
badpixelfile = os.path.join(projectdir, "badpixels1.txt")

# Detector settings
# Reduce data: number of pixels to bin (average) in each detector direction
bin = [1,1] 
# Region of interest on the detector
roi = [10,480,5,190] 

# Set the x-axis properties
# data_coordinate can be 'tth' or 'q'
data_coordinate = 'tth'
# Use x_min = None or x_max = None to automatically find data set bounds
x_min = 20.0
x_max = 98

# Histogram step size in units of the x-axis (q or tth)
x_step = 0.01

# Control plotting options
do_plot = True
# y-axis scaling, can be 'lin' or 'log'
plot_y = 'log'

# Control file export options
# In the output_filename_fmt, the specfilename (without extension) and the
# first scannumber from scans are inserted to create the output filename.
write_file = True
output_filename_fmt = os.path.join(projectdir, \
        "analysis_runtime/%s_S%03d.xye")

# Verbosity level
verbose = True

# Maximum memory to be allocated for image processing [Mb] (approximate!)
max_image_memory = 1500

#==============================================================================
# End of user parameters
# Do not modify the code below, unless you know what you are doing...
#==============================================================================

import sys
import numpy as np
import time

#from pyspec import spec
import xrayutilities as xu
import matplotlib.pyplot as plt

try:
    import rsMap3D
except:
    rsMap3D_path = 'Z:/python/rsMap3D'
    if not rsMap3D_path in sys.path:
        try:
            sys.path.insert(0,rsMap3D_path)
            import rsMap3D
        except Exception, e:
            print e.message
            raise
            sys.exit()
            
from rsMap3D.datasource.Sector33SpecDataSource import Sector33SpecDataSource
from rsMap3D.mappers.gridmapper import QGridMapper
from rsMap3D.utils.srange import srange

if verbose:
    xu.config.VERBOSITY = 1
else:
    xu.config.VERBOSITY = 0

specfilename = os.path.splitext(specfile)[0]
specfileext = os.path.splitext(specfile)[1]

# convert max_image_memory to bytes
# Factor 1/15 is an empirical fudge factor...
max_image_memory = max_image_memory*1024*1024/15

for scans in scan_list:
    _start_time = time.time()
    scan_range = srange(scans)
    scans = scan_range.list()

    # Initialize the data source from the spec file, detector and instrument
    # configuration, read the data, and set the ranges such that all images
    # will be used.
    ds = Sector33SpecDataSource(projectdir, specfilename, specfileext, \
            instrument_config, detector_config, roi=roi, pixelsToAverage=bin, \
            scanList = scans, badPixelFile = badpixelfile)
    ds.setCurrentDetector('Pilatus')
    ds.loadSource()
    ds.setRangeBounds(ds.getOverallRanges())
    imageToBeUsed = ds.getImageToBeUsed()
    wavelen = 12398.4190 / ds.getIncidentEnergy()[scans[0]]
    imageSize = np.prod(ds.getDetectorDimensions())

    # Determine data ranges
    qx_min, qx_max, qy_min, qy_max, qz_min, qz_max = ds.getOverallRanges()
    abs_qx_max = np.max(np.fabs([qx_min, qx_max]))
    if (np.sign(qx_max) != np.sign(qx_min)):
        abs_qx_min = 0.0
    else:
        abs_qx_min = np.min(np.fabs([qx_min, qx_max]))
    abs_qy_max = np.max(np.fabs([qy_min, qy_max]))
    if (np.sign(qy_max) != np.sign(qy_min)):
        abs_qy_min = 0.0
    else:
        abs_qy_min = np.min(np.fabs([qy_min, qy_max]))        
    abs_qz_max = np.max(np.fabs([qz_min, qz_max]))
    if (np.sign(qz_max) != np.sign(qz_min)):
        abs_qz_min = 0.0
    else:
        abs_qz_min = np.min(np.fabs([qz_min, qz_max]))        
    Q_min = np.sqrt(abs_qx_min**2 + abs_qy_min**2 + abs_qz_min**2)
    Q_max = np.sqrt(abs_qx_max**2 + abs_qy_max**2 + abs_qz_max**2)
    if data_coordinate is 'tth':
        coords_x_min = np.rad2deg(np.arcsin((Q_min*wavelen) / 
                            (4.0*np.pi))*2.0)
        coords_x_max = np.rad2deg(np.arcsin((Q_max*wavelen) / 
                            (4.0*np.pi))*2.0)
    else:
        coords_x_min = Q_min
        coords_x_max = Q_max
    
    # Use full range if no bounds are given
    if x_min is None:
        x_min = (np.round(coords_x_min / x_step)) * x_step
    if x_max is None:
        x_max = (np.round(coords_x_max / x_step)) * x_step  
    
    # Adjust the bounds and calculate the number of bins
    x_min = x_min - (x_step/2.0)
    x_max = x_max + (x_step/2.0)
    nbins = np.round((x_max - x_min) / x_step)
    
    if verbose:
        print 'Input data set:'
        print '  qx : ', qx_min, ' .... ', qx_max
        print '  qy : ', qy_min, ' .... ', qy_max
        print '  qz : ', qz_min, ' .... ', qz_max
        if data_coordinate is 'tth':
            print '  tth: ', coords_x_min, ' .... ', coords_x_max
        else:
            print '  Q  : ', coords_x_min, ' .... ', coords_x_max
        print 'Resulting data set:'
        print '  x_min:  ', x_min
        print '  x_max:  ', x_max
        print '  x_step: ', x_step
        print '  nbins:  ', nbins
        print ''
        print 'Starting the gridding process'
        
    # Create a gridder object and initialize
    gridder = xu.Gridder1D(int(nbins))
    gridder.KeepData(True)
    gridder.dataRange(x_min, x_max)
    
    # Create the QGridMapper object
    gm = QGridMapper(ds, 'dummy.vti')

    # Run through all scans of the scan-set to perform the gridding
    for scan in ds.getAvailableScans():
        if verbose:
            print "Scan number: ", scan
        numImages = len(imageToBeUsed[scan])
        if imageSize*4*numImages <= max_image_memory:
            if verbose:
                print "  Only 1 pass required."
            qx, qy, qz, intensity = ds.rawmap((scan,), mask=imageToBeUsed[scan])
            Q = np.sqrt(qx**2 + qy**2 + qz**2)
            if data_coordinate is 'tth':
                coords_x = np.rad2deg(np.arcsin((Q*wavelen)/(4.0*np.pi))*2.0)
            else:
                coords_x = Q
            gridder(np.ravel(coords_x), np.ravel(intensity))
                
        else:
            nPasses = np.int(np.floor(imageSize*4*numImages/max_image_memory) + 1)
            for thisPass in range(nPasses):
                if verbose:
                    print "  Pass number %d of %d " % (thisPass+1, nPasses)
                imageToBeUsedInPass = np.array(imageToBeUsed[scan])
                imageToBeUsedInPass[:thisPass*numImages/nPasses] = False
                imageToBeUsedInPass[(thisPass+1)*numImages/nPasses:] = False        
                qx, qy, qz, intensity = gm.rawmap((scan,), mask=imageToBeUsedInPass)
                Q = np.sqrt(qx**2 + qy**2 + qz**2)
                if data_coordinate is 'tth':
                    coords_x = np.rad2deg(np.arcsin((Q*wavelen) / 
                            (4.0*np.pi))*2.0)
                else:
                    coords_x = Q
                gridder(np.ravel(coords_x), np.ravel(intensity))

    if verbose:
        print 'Elapsed time for Q-conversion: %.3f seconds' % (time.time() - _start_time)

    
    data_x = gridder.xaxis
    int_y = gridder.data
    # Retrieve the normalization array from the gridder to calculate the error bars
    # for the normalized (averaged) intensities in int_y.
    # NOTE: At this stage we are assuming that gridder._gdata is an integrated
    # photon count, hence the uncertainty is given by the square root of this
    # number. This assumption is NOT VALID if additional correction factors, such
    # as monitor corrections, filter transmission corrections, or similar, have
    # been applied to the data before the gridding process, or if the data is not
    # from a photon-counting detector.
    # Error propagation needs to be addressed at a much more fundamental level in
    # our gridding routines, but presently this functionality is missing.
    err = np.where(gridder._gnorm > 0.0,
            np.sqrt(gridder._gdata)/gridder._gnorm, 0.0)

    if write_file:
        data = np.transpose(np.array([data_x, int_y, err]))
        output_filename = output_filename_fmt % (os.path.splitext(specfile)[0], scans[0])
        with open(output_filename, 'w') as outfile:
            outfile.write('# SPECfile=%s\n' % specfile)
            outfile.write('# Project=%s\n' % projectdir)
            outfile.write('# Scan_numbers=%s\n' % scan_range)
            outfile.write('# Instrument_configuration=%s\n' % instrument_config)
            outfile.write('# Detector_configuration=%s\n' % detector_config)
            outfile.write('# Bad_pixel_file=%s\n' % badpixelfile)
            outfile.write('#\n')
            outfile.write('# x_min=%.4f\n' % data_x.min())
            outfile.write('# x_max=%.4f\n' % data_x.max())
            outfile.write('# x_step=%.4f\n' % x_step)
            outfile.write('# x_npts=%d\n' % np.size(data_x))
            outfile.write('# Wavelength=%.6f\n' % wavelen)
            outfile.write('# Temperature=n/a\n')
            outfile.write('#\n')
            outfile.write('# TwoTheta Intensity Error\n')
            np.savetxt(outfile, data, fmt='%10.6e %10.6e %10.6e')
            if verbose:
                print "Data written to " + output_filename + "."
            
       
    if do_plot:
        fig = plt.figure()
        plt.plot(data_x, int_y, marker = '.')
        h_a = plt.gca()
        if plot_y is 'lin':
            h_a.set_yscale('linear')
        elif plot_y is 'log':
            h_a.set_yscale('log')
        else:
            print "Invalid y-axis scaling, must be 'lin' or 'log'."
            sys.exit()
        if data_coordinate is 'tth':
            plt.xlabel(r'$2 \theta$ [deg]')
        else:
            plt.xlabel(r'$\left|Q\right|$ [$\AA^{-1}$]')
        plt.ylabel('Intensity [arb. units]')
        plt.title('%s - Scan %s' % (specfilename, scan_range))
        plt.show()
    
