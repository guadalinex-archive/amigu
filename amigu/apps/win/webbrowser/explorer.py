# -*- coding: UTF-8 -*-
import os, re
from gtk import TreeStore
from amigu import _
from amigu.apps.win.webbrowser.base import *

class iexplorer(webbrowser):

    def initialize(self):
        """Personaliza las opciones de la aplicación"""
        webbrowser.initialize(self)
        self.name = "Internet Explorer"
        self.description = _("Favoritos de Internet Explorer")

    def get_configuration(self):
        """Devuelve la configuración de la apliación"""
        return self.user.folders['Favorites'].path

    def get_favorites(self, tree, iter, path):
        """Inicializa el árbol de marcadores
        
        Argumentos de entrada:
        tree -> objeto de tipo TreeStore
        iter -> objeto de tipo TreeIter
        path -> carpeta de favoritos de IE
        
        """
        for e in os.listdir(path):
            ruta = os.path.join(path, e)
            if os.path.exists(ruta) and os.path.isdir(ruta):
                folder = tree.append(iter, [str(e), None])
                #print str(e)
                self.get_favorites(tree, folder, ruta)
            elif os.path.exists(ruta) and os.path.isfile(ruta):
                # caso base
                (nombre, ext) = os.path.splitext(e)
                if ext == '.url': #filtrar por extension
                    try:
                        f = open(ruta, "r")
                        for linea in f.readlines():
                            if re.search('URL=', linea):
                                link = linea.replace('URL=','').replace('\r\n','')
                                file = tree.append(iter, [str(nombre), str(link)])
                                #print '\t',str(nombre), str(link)
                    finally:
                        f.close()

    def get_tree_links(self):
        """Devuelve el arbol de marcadores/favoritos de la aplicación
        contenido en un objeto de tipo TreeStore
        
        """
        tree = TreeStore(str, str)
        folder = tree.append(None, [_("Favoritos de Internet Explorer"), None])
        #print _("Marcadores de Internet Explorer")
        #print "#########################################################"
        self.get_favorites(tree, folder, self.get_configuration())
        #print "#########################################################"
        return tree

    def migrate2firefox(self):
        """Importa la configuración en Firefox"""
        ff = firefox3()
        ff.add_bookmarks(self.tree_links)
