# -*- coding: utf-8 -*-

import os
from os.path import expanduser, join, split, exists, dirname, getsize
from amigu.util.folder import *
from amigu.apps.base import application
from amigu import _


class wallpaper(application):
    """Copia y configura la imagen que se le pasa como fondo de escritorio.
    Válido para GNOME y KDE"""

    def initialize(self):
        self.name = _('Fondo de escritorio')
        self.description = _('Imagen de fondo de escritorio')
        w = self.user.search_key("Control Panel\\Desktop")
        if 'WallPaper' in w.keys():
            self.image = self.user.check_path(w['WallPaper'])
        elif 'Wallpaper' in w.keys():
            self.image = self.user.check_path(w['Wallpaper'])
        else:
            raise Exception
        
        if not exists(self.image):
            #bug in Windows XP
            self.image = self.image.replace('/w','/W')
        self.size = getsize(self.image)/1024

    def do(self):
        dest = expanduser('~') #for GNOME should be /usr/share/bankgrounds and for KDE /usr/share/themes but it requires toot privileges
        filename = basename(self.image)
        wp = join(dest, filename)
        self.update_progress(10.0)
        i = 1
        file, ext = splitext(wp)
        while exists(wp):
            wp = "%s_%d%s" % (file, i , ext)
            i += 1
        self.update_progress(25.0)
        try:
            shutil.copy2(self.image, wp)
        except:
            return 0
        self.update_progress(50.0)
        if exists('/usr/bin/gconftool'): # for GNOME
            os.system("gconftool --type string --set /desktop/gnome/background/picture_filename %s" % wp.replace(' ','\ '))
            self.update_progress(delta=15.0)
        if exists('/usr/bin/dcop'): # for KDE
            os.system('dcop kdesktop KBackgroundIface setWallpaper  %s 4' % wp.replace(' ','\ '))
            self.update_progress(delta=15.0)
        return 1

class avatar(application):
    """Establece la imagen del usuario del sistema"""

    def initialize(self):
        self.name = _('Imagen de usuario')
        self.description = _('Imagen de usuario')
        if self.user.get_avatar().find('nobody') > 0:
            raise Exception
        self.size = getsize(self.user.get_avatar())/1024

    def do(self):
        self.update_progress(delta=50.0)
        shutil.copy2(self.user.get_avatar(), join(expanduser('~'), '.face'))
        return 1


class fonts_installer(application):
    """Copia las fuentes ttf del directorio que se le pasa"""

    def initialize(self):
        self.name = _('Fuentes tipográficas')
        self.description = _('Fuentes tipográficas')
        if not "Fonts" in self.user.folders.keys() and not self.user.folders["Fonts"]:
            raise Exception
        self.size = self.user.folders["Fonts"].get_size()

    def do(self):
        dest = folder(join(expanduser('~'),'.fonts','ttf-windows'))
        inc = 0
        if self.model:
            inc = 99.9/self.user.folders["Fonts"].count_files()
        try:
            self.user.folders["Fonts"].copy(destino=dest.path, extension='.ttf', function=self.update_progress, delta=inc)
        except:
            pass
        else:
            return 1
