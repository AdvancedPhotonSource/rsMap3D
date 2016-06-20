'''
 Copyright (c) 2014, UChicago Argonne, LLC
 See LICENSE file.
'''
from setuptools import setup


setup(name='rsMap3D',
      version='1.0.10',
      description='Python Program to map xray diffraction data into ' + \
                    'reciprocal space map',
      author = 'John Hammonds, Christian Schleputz',
      author_email = 'JPHammonds@anl.gov',
      url = 'https://confluence.aps.anl.gov/display/RSM/SSG_000116+Reciprocal+Space+Mapping',
      packages = ['rsMap3D',
                  'rsMap3D.config',
                   'rsMap3D.datasource',
                   'rsMap3D.datasource.DetectorGeometry',
                   'rsMap3D.exception',
                   'rsMap3D.gui',
                   'rsMap3D.gui.input',
                   'rsMap3D.transforms',
                   'rsMap3D.utils',
                   'rsMap3D.mappers'] ,
      install_requires = ['spec2nexus',
                 'pillow',
                 ],
      license = 'See LICENSE File',
      platforms = 'any',
      scripts = ['Scripts/rsMap3D',
                 'Scripts/rsMap3D.bat'],
      )