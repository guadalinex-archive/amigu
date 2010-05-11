# -*- coding: UTF-8 -*-

import os
from gtk import TreeStore
from glob import glob
import sqlite3
from amigu import _
from amigu.apps.win.webbrowser.base import *
from amigu.util.folder import folder

class firefox(webbrowser):

    def initialize(self):
        """Personaliza las opciones de la aplicación"""
        webbrowser.initialize(self)
        self.name = "Mozilla Firefox"
        self.description = _("Marcadores de Mozilla Firefox")

    def get_configuration(self):
        """Devuelve la configuración de la apliación"""
        self.bookmarks_file = glob(os.path.join(self.user.folders["AppData"].path, 'Mozilla', 'Firefox', 'Profiles','*.default', 'places.sqlite'))[0]
        if self.bookmarks_file:
            conn = sqlite3.connect(self.bookmarks_file)
            c = conn.cursor()
            q = "SELECT mb.type, mb.id, mb.parent, mb.title, mp.title, mp.url FROM moz_bookmarks mb LEFT JOIN moz_places AS mp ON mb.fk=mp.id WHERE mb.id>1 AND (mp.rev_host IS NOT NULL AND mp.frecency >0 OR mb.type==2) ORDER BY mb.type DESC"
            c.execute(q)
            res = c.fetchall()
            conn.close()
            return res

    def get_tree_links(self):
        """Devuelve el arbol de marcadores/favoritos de la aplicación
        contenido en un objeto de tipo TreeStore
        
        """
        tree = TreeStore(str, str)
        folder = tree.append(None, [_("Marcadores de Mozilla Firefox"), None])
        #print _("Marcadores de Mozilla Firefox")
        #print "#########################################################"
        self.get_bookmarks(tree, folder, self.get_configuration())
        #print "#########################################################"
        return tree

    def get_bookmarks(self, tree, iter, marks_list):
        """Inicializa el árbol de marcadores
        
        Argumentos de entrada:
        tree -> objeto de tipo TreeStore
        iter -> objeto de tipo TreeIter
        mark_list -> lista de marcadores
        
        """
        for e in marks_list:
            if e[0]==2:
                #caso recursivo
                folder = tree.append(iter, [e[3],None])
                #print e[3]
                self.get_bookmarks(tree, folder, [f for f in marks_list if f[2] == e[1]])
            elif e[0]==1:
                # caso base
                if e[4].count('/') < 3:
                    mark = tree.append(iter, [e[4], e[5]])
                #print '\t' + e[4], e[5]

    def migrate2firefox(self):
        """Importa la configuración en Firefox"""
        if not os.path.exists(os.path.join(os.path.expanduser('~'), '.mozilla', 'firefox')):
            self.direct_import()
        else:
            ff = firefox3()
            ff.add_bookmarks(self.tree_links)
            
    def direct_import(self):
        """Importa directamente la configuración en Firefox"""
        dest = folder(os.path.join(os.path.expanduser('~'), '.mozilla', 'firefox'))
        origen = folder(os.path.join(self.user.folders["AppData"].path, 'Mozilla', 'Firefox'))
        origen.copy(dest)
