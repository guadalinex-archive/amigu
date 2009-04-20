# -*- coding: utf-8 -*-
# Funciones asociadas a configuraciones del usuario.
# Permite configurar el fondo de escritorio e instalar nuevas fuentes true-type.

import os, re, shutil
from amigu.util.folder import *
from amigu.apps.base import application
from amigu import _

class emule(application):
    
    def initialize(self):
        self.name = _("eMule")
        self.description = _("Configuración de eMule")+"\n"+_("Seleccione también la opción Archivos")
        self.cfg_dir = self.get_configuration()
        self.inc_dir, self.tmp_dir = None, None
        if not self.cfg_dir:
            raise Exception
        self.size = self.cfg_dir.get_size()
        self.get_paths()
        if self.user.os.find('Vista') > 1:
            f = self.user.folders['Downloads'].path
        elif self.user.os.find('XP') > 1:
            f = self.user.get_personal_folder().path
        if self.inc_dir and not self.inc_dir.path.startswith(f):
            self.size += self.inc_dir.get_size()
            self.description = _("Configuración y archivos de eMule")
        if self.tmp_dir and not self.tmp_dir.path.startswith(f):
            self.size += self.tmp_dir.get_size()
            self.description = _("Configuración y archivos de eMule")


        
    def get_configuration(self):
        if self.user.os.find('XP') > 0:
            e = self.user.search_key("Software\eMule")
            if e and 'Install Path' in e.keys():
                path = e["Install Path"].replace(e["Install Path"][:2], self.user.mount_points[e["Install Path"][:2]])
                if os.path.exists(os.path.join(path,'config','preferences.ini')):
                    return folder(os.path.join(path,'config'))
        elif self.user.os.find('Vista') > 0:
            d = os.path.join(self.user.folders["Local AppData"].path, 'eMule', 'config')
            if os.path.exists(d):
                return folder(d)
        
        
    def config_aMule(self):
        """Configura el programa de P2P aMule con la configuración del programa eMule en Windows"""
        amule = folder(os.path.join(os.path.expanduser('~'), '.aMule'))
        if amule:
            # copy edonkey config files
            self.cfg_dir.copy(amule, extension = ['.ini','.dat','.met'])
            # copy edonkey temporary files
            conf = os.path.join(amule.path, 'amule.conf')
            bak = backup(conf)
            try:
                emupref = open(os.path.join(amule.path,'preferences.ini'),'r')
                amuconf = open(conf, 'w')
                for l in emupref.readlines():
                    if l.find("IncomingDir") != -1:
                        l = "IncomingDir=%s\n" % os.path.join(amule.path,'Incoming')
                    if l.find("TempDir") != -1:
                        l = "TempDir=%s\n" % os.path.join(amule.path,'Temp')
                    amuconf.write(l)
                amuconf.close()
                emupref.close()
            except:
                amuconf.close()
                emupref.close()
                if bak:
                    restore_backup(bak)
            else:
                return 1
                
                
    def import_files(self):
        if self.user.os.find('Vista') > 1:
            f = self.user.folders['Downloads'].path
        elif self.user.os.find('XP') > 1:
            f = self.user.get_personal_folder().path
        if self.inc_dir and not self.inc_dir.path.startswith(f):
            self.inc_dir.copy(os.path.join(os.path.expanduser('~'), '.aMule'), function=self.update_progress, delta=25.0/(self.inc_dir.count_files()+1))
        if self.tmp_dir and not self.tmp_dir.path.startswith(f):
            self.tmp_dir.copy(os.path.join(os.path.expanduser('~'), '.aMule'), extension = ['.part','.met',',part.met'], function=self.update_progress, delta=25.0/(self.tmp_dir.count_files()+1))
        return 1


    def get_paths(self):
        """Devuelve la ruta del directorio de descargas"""
        a = None
        try:
            a = open(os.path.join(self.cfg_dir.path,'preferences.ini'), 'r')
            for l in a.readlines():
                l = l.replace('\r\n','')
                if l.find("IncomingDir") != -1:
                    inc = l.split('=')[1]
                    inc = inc.replace('\\','/')
                    inc = self.user.mount_points[inc[:2]] + inc[2:]
                    self.inc_dir = folder(inc)
                elif l.find("TempDir") != -1:
                    tmp = l.split('=')[1]
                    tmp = tmp.replace('\\','/')
                    tmp = self.user.mount_points[tmp[:2]] + tmp[2:]
                    self.tmp_dir = folder(tmp)
        except:
            pass
        else:
            a.close()

    def do(self):
        self.update_progress(10.0)
        a = self.config_aMule()
        self.update_progress(30.0)
        b = self.import_files()
        self.update_progress(90.0)
        return (a and b)
        

class wallpaper(application):
    """Copia y configura la imagen que se le pasa como fondo de escritorio.
    Válido para GNOME y KDE"""

    def initialize(self):
        self.name = _('Fondo de escritorio')
        self.description = _('Imagen de fondo de escritorio')
        w = self.user.search_key("Control Panel\\Desktop")
        self.image = self.user.check_path(w['WallPaper'])
        print self.image
        if not os.path.exists(self.image):
            #bug in Windows XP
            self.image = self.image.replace('/w','/W')
        self.size = os.path.getsize(self.image)/1024

    def do(self):
        dest = os.path.expanduser('~') #for GNOME should be /usr/share/bankgrounds and for KDE /usr/share/themes but it requires toot privileges
        filename = os.path.basename(self.image)
        wp = os.path.join(dest, filename)
        self.update_progress(50.0)
        if not os.path.exists(wp):
            try:
                shutil.copy2(self.image, dest)
            except:
                return 0
        if os.path.exists('/usr/bin/gconftool'): # for GNOME
            os.system("gconftool --type string --set /desktop/gnome/background/picture_filename %s" % wp.replace(' ','\ '))
            self.update_progress(delta=20.0)
        if os.path.exists('/usr/bin/dcop'): # for KDE
            os.system('dcop kdesktop KBackgroundIface setWallpaper  %s 4' % wp.replace(' ','\ '))
            self.update_progress(delta=20.0)
        return 1

class avatar(application):
    """Establece la imagen del usuario del sistema"""

    def initialize(self):
        self.name = _('Imagen de usuario')
        self.description = _('Imagen de usuario')
        if self.user.get_avatar().find('nobody') > 0:
            raise Exception
        self.size = os.path.getsize(self.user.get_avatar())/1024

    def do(self):
        self.update_progress(delta=50.0)
        shutil.copy2(self.user.get_avatar(), os.path.join(os.path.expanduser('~'), '.face'))
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
        dest = folder(os.path.join(os.path.expanduser('~'),'.fonts','ttf-windows'))
        inc = 0
        if self.model:
            inc = 99.9/self.user.folders["Fonts"].count_files()
        try:
            self.user.folders["Fonts"].copy(destino=dest.path, extension='.ttf', function=self.update_progress, delta=inc)
        except:
            pass
        else:
            return 1


