'''
 Copyright (c) 2017, UChicago Argonne, LLC
 See LICENSE file.
'''
LOGGER_NAME = "rsMap3D"
LOGGER_FORMAT = '%(asctime)-15s - %(name)s - %(funcName)s- %(levelname)s - %(message)s'
LOGGER_DEFAULT = {
    'version' : 1,
    'handlers' : {'consoleHandler' : {'class' : 'logging.StreamHandler',
                               'level' : 'INFO',
                               'formatter' : 'consoleFormat',
                               'stream' : 'ext://sys.stdout'}
                  },
    'formatters' : {'consoleFormat' : {'format' : '%(asctime)-15s - %(name)s - %(funcName)s- %(levelname)s - %(message)s'}
                    },
    'loggers' : {'root' :{'level' : 'INFO',
                        'handlers' : ['consoleHandler',],
                      },
               'rsMap3D' : {'level' : 'INFO',
                            'handlers' : ['consoleHandler',],
                            'qualname' : 'rsMap3D'
                            }
               },
   }

METHOD_ENTER_STR = "Enter %s\n-------------------"
METHOD_EXIT_STR = "Exit %s\n---------------------"
