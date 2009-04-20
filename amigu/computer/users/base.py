# -*- coding: utf-8 -*-

import os
import re
#from amigu.apps.lnx import *
from amigu.util.folder import *
import gettext

_ = gettext.gettext
gettext.textdomain("amigu")
gettext.bindtextdomain("amigu", "./translations")

class generic_usr:
    """Clase para los usuarios del PC"""

    def __init__(self, dir, pc, ops):
        """Constructor de la clase.
        Recibe la ruta a la carpeta del usuario"""
        self.os = ops
        self.path = dir
        self.name = os.path.split(dir)[1]
        self.folders = self.get_user_folders(pc)
        if not self.folders:
            self.error("Couldn't get user folders.")
        else:
            self.init_apps()
            self.info = None
            self.tree_options = None
            self.errors = []
        if self.errors: print self.errors

    def init_apps(self):
        pass

    def get_path(self):
        """Devuelve la carpeta del usuario"""
        return self.path

    def get_personal_folder(self):
        """Devuelve las carpetas personales y de configuración del usuario"""
        return self.folders['Personal']

    def get_avatar(self):
            return "/usr/share/pixmaps/nobody.png"

    def get_name(self):
        """Devuelve el nombre del usuario de Windows"""
        return self.name

    def get_details(self):
        size = "0Mb"
        size = "%.2fMb" % (self.folders['Personal'].get_size()/1024.0)
        return "Sistema Operativo"+": "+self.os +", "+ size +" de datos"

    def get_info(self):
        """Devuelve la información de archivos y programas del usuario"""
        pass

    def all_errors(self):
        """Recopila los errores producidos en tiempo de ejecuccion"""
        return self.errors

    def get_tree_options(self, update=False):
        """Genera el árbol de opciones para el usario seleccionado"""

        if self.tree_options:
            if update:
                self.tree_options.clear()
            else:
                return self.tree_options
        else:
            from gtk import TreeStore
            self.tree_options = TreeStore( str, 'gboolean', str, str, str)

        name_usr = self.tree_options.append(None, [self.get_name(), None, None, _('Usuario seleccionado'), None])

        # Files
        parent = self.tree_options.append(name_usr , [_("Archivos"), None, None, _('Migrar archivos'), None] )
        personal = self.tree_options.append( parent, [_("Carpeta Personal"), None, str(self.folders['Personal'].get_size()), _('Archivos personales: ')+ self.folders['Personal'].get_info(), 'documentos'] )
        #self.tree_options.append(personal, [_("Escritorio"), None, str(self.folders['Desktop'].get_size()), _('Archivos del escritorio: ')+self.folders['Desktop'].get_info(), 'escritorio'] )
        #self.tree_options.append(personal, [_("Documentos"), None, str(self.folders['Desktop'].get_size()), _('Archivos del escritorio: ')+self.folders['My Documents'].get_info(), 'docs'] )
        #self.tree_options.append(personal, [_("Música"), None, str(self.folders['Desktop'].get_size()), _('Archivos del escritorio: ')+self.folders['My Music'].get_info(), 'audio'] )
        #self.tree_options.append(personal, [_("Videos"), None, str(self.folders['Desktop'].get_size()), _('Archivos del escritorio: ')+self.folders['My Video'].get_info(), 'video'] )
        #self.tree_options.append(personal, [_("Imágenes"), None, str(self.folders['Desktop'].get_size()), _('Archivos del escritorio: ')+self.folders['My Pictures'].get_info(), 'imagenes'] )
        return self.tree_options

    def get_user_folders(self, pc):
        """Devuelve las carpetas de archivos, configuraciones y programas del usuario"""
        folders = {}
        folders["Personal"] = folder(self.path)
        return folders

    def clean(self):
        pass

#end class user


############################################################################

def test():
    from amigu.computer.info import pc
    com = pc()
    com.check_all_partitions()
    print "Analizando usuarios...."
    for user_path, ops in com.get_mac_users().iteritems():
        u = generic_usr(user_path, ops, com)
        print u.get_details()
        print u.get_avatar()
        u.clean()

if __name__ == "__main__":
    test()
