# -*- coding: utf-8 -*-

import os
import re
from amigu.util.folder import *
from amigu import _


class generic_usr:
    """Clase abstracta para los usuarios del PC"""

    def __init__(self, dir, pc, ops):
        """Constructor de la clase.
        
        Argumentos de entrada:
        dir  -- directorio raíz del usuario
        pc -- objeto de la clase PC
        ops -- sistema operativo al que pertence el usuario
        
        """
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
        """Método a definir por las clases hijas para ejecutarse al 
        crear el objeto
        """
        pass

    def get_path(self):
        """Devuelve la carpeta raíz del usuario"""
        return self.path

    def get_personal_folder(self):
        """Devuelve las carpetas personales y de configuración del usuario"""
        return self.folders['Personal']

    def get_avatar(self):
        """Devuelve la imagen de usuario"""
        return "/usr/share/pixmaps/nobody.png"

    def get_name(self):
        """Devuelve el nombre del usuario en el sistema"""
        return self.name

    def get_details(self):
        """Devuelve información sobre el usuario        OBSOLETO
        
        """
        size = "0Mb"
        size = "%.2fMb" % (self.folders['Personal'].get_size()/1024.0)
        return "Sistema Operativo"+": "+self.os +", "+ size +" de datos"

    def get_info(self):
        """Método a definir por las clases hijas.
        Devuelve la información de archivos y programas del usuario
        
        """
        pass

    def all_errors(self):
        """Devuelve los errores producidos en tiempo de ejecuccion"""
        return self.errors

    def get_tree_options(self, update=False):
        """Devuele el árbol de opciones generado para el usario seleccionado.
        El objeto devuelto es de tipo gtk.TreeStore.
        Este método debe ampliarse en las clases hijas.
        
        Argumentos de entrada:
        update -- indica si se debe actualizar el contenido del árbol (default False)
        
        """
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
        return self.tree_options

    def get_user_folders(self, pc):
        """Devuelve un diccionario que contiene las carpetas de archivos, 
        configuraciones y programas del usuario.
        
        Esta clase debe ampliarse en las clases hijas
        
        Argumentos de entrada:
        pc -- objeto de tipo PC
        
        """
        folders = {}
        folders["Personal"] = folder(self.path)
        return folders

    def clean(self):
        """Método abstracto que elimina los archivos temporales usados"""
        pass
#end class user


############################################################################

def test():
    from amigu.computer.info import pc
    com = pc()
    com.check_all_partitions()
    print "Analizando usuarios...."
    for user_path, ops in com.get_win_users().iteritems():
        u = generic_usr(user_path, ops, com)
        print u.get_details()
        print u.get_avatar()
        u.clean()

if __name__ == "__main__":
    test()
