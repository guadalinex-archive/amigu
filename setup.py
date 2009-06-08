#!/usr/bin/env python
# -*- coding: utf-8 -*-
from distutils.core import setup
from distutils.extension import Extension
import amigu
import os

needed_dirs = ('/usr/share/pixmaps/amigu', '/usr/share/amigu')
for d in needed_dirs:
    try:
        os.makedirs(needed_dir)
    except:
        pass

setup(  name             = "AMIGU",
        version          = amigu.__version__,
        author           = "Fernando Ruiz Humanes",
        author_email     = "fruiz@forja.guadalinex.org",
        url              = "http://forja.guadalinex.org/repositorio/projects/amigu/",
        download_url     = "http://forja.guadalinex.org/repositorio/frs/?group_id=22",
        package_dir      = {'amigu': 'amigu'},
        packages         = ['amigu',
                            'amigu.computer',
                            'amigu.computer.users',
                            'amigu.util',
                            'amigu.gui',
                            'amigu.apps',
                            'amigu.apps.win',
                            'amigu.apps.lnx',
                            'amigu.apps.mac',],
        data_files=[('/usr/share/applications/', ['amigu.desktop']),
                    ('/usr/share/amigu/', ['share/places.sqlite']),
                    ('/usr/bin/', ['bin/amigu','bin/dumphive', 'bin/readdbx', 'bin/readoe', 'bin/readpst']),
                    ('/usr/share/pixmaps/amigu', ['imagenes/cab_amigu.png', 'imagenes/icon_paginacion.png']),
                    ('/usr/share/locale/es/LC_MESSAGES', ['translations/es/LC_MESSAGES/amigu.mo']),
                    ('/usr/share/locale/en/LC_MESSAGES', ['translations/en/LC_MESSAGES/amigu.mo'])
                    ],
     )


