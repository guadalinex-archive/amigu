# -*- coding: UTF-8 -*-
import os
from gtk import TreeStore
from amigu import _
from amigu.apps.win.webbrowser.base import *

class opera(webbrowser):

    def initialize(self):
        """Personaliza las opciones de la aplicación"""
        webbrowser.initialize(self)
        self.name = "Opera"
        self.description = _("Marcadores de Opera")

    def get_configuration(self):
        """Devuelve la configuración de la apliación"""
        file = os.path.join(self.user.folders['AppData'].path, 'Opera', 'Opera', 'bookmarks.adr')
        links = []
        marks = open(file,'r')
        hotlist = marks.read().split('\r\n\r\n')
        marks.close()
        for h in hotlist:
            valid = True
            e = h.split('\r\n')
            if e[0]=="#FOLDER":
                if valid:
                    links.append([e[0],e[2].replace('\t','')[5:], None])
            elif e[0]=="#URL":
                name=e[2].replace('\t','')[5:]
                url=e[3].replace('\t','')[4:]
                links.append([e[0],name, url])
            elif e[0]=='-':
                links.append([e[0], None, None])
        return links

    def get_tree_links(self):
        """Devuelve el arbol de marcadores/favoritos de la aplicación
        contenido en un objeto de tipo TreeStore
        
        """
        tree = TreeStore(str, str)
        folder = tree.append(None, [_("Marcadores de Opera"), None])
        #print "#########################################################"
        self.get_bookmarks(tree, folder, self.get_configuration())
        #print "#########################################################"
        return tree

    def get_bookmarks(self, tree, iter, opera_links):
        """Inicializa el árbol de marcadores
        
        Argumentos de entrada:
        tree -> objeto de tipo TreeStore
        iter -> objeto de tipo TreeIter
        mark_list -> lista de marcadores
        
        """
        while opera_links:
            e = opera_links.pop(0)
            if e[0]=="#FOLDER":
                folder = tree.append(iter, [e[1],None])
                #print e[1]
                self.get_bookmarks(tree, folder, opera_links)
            elif e[0]=="#URL":
                folder = tree.append(iter, [e[1],e[2]])
                #print '\t', e[1],e[2]
            elif e[0]=='-':
                break
        return tree

    def migrate2firefox(self):
        """Importa la configuración en Firefox"""
        ff = firefox3()
        ff.add_bookmarks(self.tree_links)
