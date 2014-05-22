'''
 Copyright (c) 2012, UChicago Argonne, LLC
 See LICENSE file.
'''
class RSMap3DException(Exception):
    '''
    General base class for all exceptions in rsMap3D package.
    '''
    def __init__(self, message):
        '''
        Constructor
        :param message: Message string to pass along when the exception is 
        raised.
        '''
        super(RSMap3DException, self).__init__(message)

class DetectorConfigException(RSMap3DException):
    '''
    Exception class to be raised if there is a problem with a detector config
    file
    '''
    def __init__(self, message):
        super(DetectorConfigException, self).__init__(message)

class InstConfigException(RSMap3DException):
    '''
    Exception class to be raised if there is a problem with an instrument config
    file
    '''
    def __init__(self, message):
        '''
        Constructor
        :param message: Message string to pass along when the exception is 
        raised.
        '''
        super(InstConfigException, self).__init__(message)

class Transform3DException(RSMap3DException):
    '''
    Exception class to be raised if there is a problem with a detector config
    file
    '''
    def __init__(self, message):
        '''
        Constructor
        :param message: Message string to pass along when the exception is 
        raised.
        '''
        super(Transform3DException, self).__init__(message)

class ScanDataMissingException(RSMap3DException):
    '''
    Exception class to be raised if the process of loading scan information
    shows that the data is missing
    '''
    def __init__(self, message):
        '''
        Constructor
        :param message: Message string to pass along when the exception is 
        raised.
        '''
        super(ScanDataMissingException, self).__init__(message)

