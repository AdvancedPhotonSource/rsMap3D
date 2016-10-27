import sys
import os
import vtk
from vtk.util import numpy_support
import numpy as np
import Image


vti_input_file = sys.argv[1]



#vti_file = '/Users/cschlep/software/python/rsMap3D/trunk/rsMap3D/CB_130905_1_1_S221.vti'
#vti_file = '/Users/cschlep/software/python/rsMap3D/trunk/rsMap3D/CB_140303A_1_S111.vti'


def export_tiff_stack(qx, qy, qz, intensity, dim=2, filebase="slice"):
        if dim==0:
            for ind, val in enumerate(qx):
                im = Image.fromarray(np.squeeze(intensity[ind,:,:]))
                filename = "%s_x%.3f.tif" % (filebase, val)
                im.save(filename)
        if dim==1:
            for ind, val in enumerate(qx):
                im = Image.fromarray(np.squeeze(intensity[:,ind,:]))
                filename = "%s_y%.3f.tif" % (filebase, val)
                im.save(filename)
        if dim==2:
            for ind, val in enumerate(qz):
                im = Image.fromarray(np.squeeze(intensity[:,:,ind]))
                filename = "%s_z%.3f.tif" % (filebase, val)
                im.save(filename)

def main():

    vti_file = os.path.abspath(vti_input_file)

    vti_reader = vtk.vtkXMLImageDataReader()
    vti_reader.SetFileName(vti_file)
    vti_reader.Update()
    vti_data = vti_reader.GetOutput()
    vti_point_data = vti_data.GetPointData()
    vti_array_data = vti_point_data.GetScalars()
    array_data = numpy_support.vtk_to_numpy(vti_array_data)
    dim = vti_data.GetDimensions()
    steps = vti_data.GetSpacing()
    origin = vti_data.GetOrigin()

    qx = np.linspace(origin[0], origin[0]+dim[0]*steps[0], dim[0])
    qy = np.linspace(origin[1], origin[1]+dim[1]*steps[1], dim[1])
    qz = np.linspace(origin[2], origin[2]+dim[2]*steps[2], dim[2])
    
    print 'Qx: ', np.shape(qx), ', ', np.min(qx), ', ', np.max(qx)
    print 'Qy: ', np.shape(qy), ', ', np.min(qy), ', ', np.max(qy)
    print 'Qz: ', np.shape(qz), ', ', np.min(qz), ', ', np.max(qz)

    print 'Dimensions: ', dim
    print 'array shape: ', np.shape(array_data)

    array_data = np.reshape(array_data, dim[::-1])
    print 'array shape: ', np.shape(array_data)

    array_data = np.transpose(array_data)
    print 'array shape: ', np.shape(array_data)

    data_dir, filename = os.path.split(vti_file)
    filebase, ext = os.path.splitext(filename)
    
    if not os.path.isdir(os.path.join(data_dir, filebase)):
        print "Creating image directory."
        os.mkdir(os.path.join(data_dir, filebase))
    else:
        print "found directory!"

    export_tiff_stack(qx, qy, qz, array_data, dim=2, \
        filebase=os.path.join(data_dir, filebase, filebase))


if __name__ == '__main__':
    main()




