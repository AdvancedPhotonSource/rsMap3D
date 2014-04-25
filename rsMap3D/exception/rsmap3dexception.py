'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
class RSMap3DException(Exception):
    '''
    General base class for all exceptions in rsMap3D package.
    '''
    def __init__(self, message):
        super(RSMap3DException, self).__init__(message)

class InstConfigException(RSMap3DException):
    '''
    Exception class to be raised if there is a problem with an instrument config
    file
    '''
    def __init__(self, message):
        super(InstConfigException, self).__init__(message)

class DetectorConfigException(RSMap3DException):
    '''
    Exception class to be raised if there is a problem with a detector config
    file
    '''
    def __init__(self, message):
        super(DetectorConfigException, self).__init__(message)

class Transform3DException(RSMap3DException):
    '''
    Exception class to be raised if there is a problem with a detector config
    file
    '''
    def __init__(self, message):
        super(Transform3DException, self).__init__(message)

