# -*- coding: utf-8 -*-

import os
from os.path import expanduser, join, split, exists, dirname, getsize
from amigu.util.folder import *
from amigu.apps.base import application
from amigu import _

class emule(application):
    
    def initialize(self):
        self.name = _("eMule")
        self.description = _("Configuración de eMule")
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
                if exists(join(path,'config','preferences.ini')):
                    return folder(join(path,'config'))
        elif self.user.os.find('Vista') > 0:
            d = join(self.user.folders["Local AppData"].path, 'eMule', 'config')
            if exists(d):
                return folder(d)
        
        
    def config_aMule(self):
        """Configura el programa de P2P aMule con la configuración del programa eMule en Windows"""
        amule = folder(join(expanduser('~'), '.aMule'))
        if amule:
            # copy edonkey config files
            self.cfg_dir.copy(amule, extension = ['.ini','.dat','.met'])
            # copy edonkey temporary files
            conf = join(amule.path, 'amule.conf')
            bak = backup(conf)
            try:
                emupref = open(join(amule.path,'preferences.ini'),'r')
                amuconf = open(conf, 'w')
                for l in emupref.readlines():
                    if l.find("IncomingDir") != -1:
                        l = "IncomingDir=%s\n" % join(amule.path,'Incoming')
                    if l.find("TempDir") != -1:
                        l = "TempDir=%s\n" % join(amule.path,'Temp')
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
            self.inc_dir.copy(join(expanduser('~'), '.aMule'), function=self.update_progress, delta=25.0/(self.inc_dir.count_files()+1))
        if self.tmp_dir and not self.tmp_dir.path.startswith(f):
            self.tmp_dir.copy(join(expanduser('~'), '.aMule'), extension = ['.part','.met',',part.met'], function=self.update_progress, delta=25.0/(self.tmp_dir.count_files()+1))
        else:
            #os.symlink(join(expanduser('~'), '.aMule', 'Temp'))
            pass
        return 1


    def get_paths(self):
        """Devuelve la ruta del directorio de descargas"""
        a = None
        try:
            a = open(join(self.cfg_dir.path,'preferences.ini'), 'r')
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
