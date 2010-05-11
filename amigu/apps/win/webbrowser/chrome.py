# -*- coding: UTF-8 -*-
import os
from gtk import TreeStore
from amigu import _
from amigu.apps.win.webbrowser.base import *

class chrome(webbrowser):

    def initialize(self):
        """Personaliza las opciones de la aplicación"""
        webbrowser.initialize(self)
        self.name = "Google Chrome"
        self.description = _("Marcadores de Google Chrome")

    def get_configuration(self):
        """Devuelve la configuración de la apliación"""
        self.bookmarks_file = os.path.join(self.user.folders["Local AppData"].path, 'Google', 'Chrome', 'User Data', 'Default', 'Bookmarks')
        f = open(self.bookmarks_file, 'r')
        dict = f.read()
        f.close()
        bookmarks = eval(dict.replace('\r\n',''))
        return bookmarks

    def get_tree_links(self):
        """Devuelve el arbol de marcadores/favoritos de la aplicación
        contenido en un objeto de tipo TreeStore
        
        """
        tree = TreeStore(str, str)
        folder = tree.append(None, [_("Marcadores de Google Chrome"), None])
        #print _("Marcadores de Google Chrome")
        #print "#########################################################"
        self.get_bookmarks(tree, folder, self.get_configuration())
        #print "#########################################################"
        return tree

    def get_bookmarks(self, tree, iter, marks):
        """Inicializa el árbol de marcadores
        
        Argumentos de entrada:
        tree -> objeto de tipo TreeStore
        iter -> objeto de tipo TreeIter
        marks -> lista de marcadores
        
        """
        if isinstance(marks, list):
            for e in marks:
                self.get_bookmarks(tree, iter, e)
        elif isinstance(marks, dict):
            if "type" in marks.keys():
                if marks["type"] == "folder":
                    #caso recursivo
                    folder = tree.append(iter, [eval("u'%s'" % marks["name"]),None])
                    #print marks["name"].decode('iso-8859-1').encode('utf-8')
                    self.get_bookmarks(tree, folder, marks["children"])
                elif marks["type"] == "url":
                    # caso base
                    #print '\t', marks["name"].decode('iso-8859-1').encode('utf-8'), marks["url"].decode('iso-8859-1').encode('utf-8')
                    mark = tree.append(iter, [eval("u'%s'" % marks["name"]), marks["url"].decode('iso-8859-1').encode('utf-8')])
            else:
                for e in marks.values():
                    self.get_bookmarks(tree, iter, e)


    def migrate2firefox(self):
        """Importa la configuración en Firefox"""
        ff = firefox3()
        ff.add_bookmarks(self.tree_links)
