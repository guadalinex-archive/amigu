# -*- coding: UTF-8 -*-
import os, re, shutil
from amigu.util.folder import *
from amigu.apps.base import application
from gtk import TreeStore
from glob import glob
import time
import sqlite3
from amigu import _

class webbrowser(application):
    """Clase para le manejo de navegadores Web"""

    def initialize(self):
        """Personaliza las opciones de la aplicación"""
        self.name = _("Navegador Web")
        self.description = _("Preferencias de navegación web")
        self.tree_links = self.get_tree_links()
        self.size = len(self.tree_links)

    def get_configuration(self):
        """Método abstracto para obtener la configuración asociada a la aplicación"""
        pass

    def get_tree_links(self):
        """Método abstracto para obtener el arbol de marcadores/favoritos
        de la aplicación
        
        """
        return TreeStore(str, str)

    def do(self):
        """Método que realiza el proceso de migración"""
        self.pulse_start()
        self.migrate2firefox()
        #self.update_progress(55.0)
        #self.migrate2konqueror()
        self.pulse_stop()
        return 1

    def migrate2firefox(self):
        """Metodo abstracto que importa la configuracion a Firefox"""
        pass

    def migrate2konqueror(self):
        """Metodo abstracto que importa la configuracion a Konqueror"""
        pass

class firefox3:
    """Clase para el manejo de la Mozilla Firefox 3 en Linux"""

    def __init__(self):
        """Constructor de la clase"""
        try:
            prof = open(os.path.join(os.path.expanduser('~'), '.mozilla', 'firefox', 'profiles.ini'), 'rb')
            for l in prof.readlines():
                if l.startswith('Path'):
                    perfil = l.split('=')[1].replace('\n','').replace('\r','')
            prof.close()
            self.bookmarks_file = glob(os.path.join(os.path.expanduser('~'), '.mozilla', 'firefox', perfil, 'places.sqlite'))[0]
        except:
            # create profile and bookmarks file
            ff_dir = folder(os.path.join(os.path.expanduser('~'), '.mozilla', 'firefox','m1gra73d.default'))
            prof = open(os.path.join(os.path.expanduser('~'), '.mozilla', 'firefox','profiles.ini'), 'w')
            prof.write("[General]\n")
            prof.write("StartWithLastProfile=1\n\n")
            prof.write("[Profile0]\n")
            prof.write("Name=migrated\n")
            prof.write("IsRelative=1\n")
            prof.write("Path=m1gra73d.default\n")
            prof.close()
            self.bookmarks_file = None
        if not self.bookmarks_file:
            self.bookmarks_file = os.path.join(ff_dir.path,'places.sqlite')
            try:
                conn = sqlite3.connect(self.bookmarks_file)
                c = conn.cursor()
                c.executescript("""CREATE TABLE moz_anno_attributes (id INTEGER PRIMARY KEY,name VARCHAR(32) UNIQUE NOT NULL);
CREATE TABLE moz_annos (id INTEGER PRIMARY KEY,place_id INTEGER NOT NULL,anno_attribute_id INTEGER,mime_type VARCHAR(32) DEFAULT NULL,content LONGVARCHAR, flags INTEGER DEFAULT 0,expiration INTEGER DEFAULT 0,type INTEGER DEFAULT 0,dateAdded INTEGER DEFAULT 0,lastModified INTEGER DEFAULT 0);
CREATE TABLE moz_bookmarks (id INTEGER PRIMARY KEY,type INTEGER, fk INTEGER DEFAULT NULL, parent INTEGER, position INTEGER, title LONGVARCHAR, keyword_id INTEGER, folder_type TEXT, dateAdded INTEGER, lastModified INTEGER);
CREATE TABLE moz_bookmarks_roots (root_name VARCHAR(16) UNIQUE, folder_id INTEGER);
CREATE TABLE moz_favicons (id INTEGER PRIMARY KEY, url LONGVARCHAR UNIQUE, data BLOB, mime_type VARCHAR(32), expiration LONG);
CREATE TABLE moz_historyvisits (id INTEGER PRIMARY KEY, from_visit INTEGER, place_id INTEGER, visit_date INTEGER, visit_type INTEGER, session INTEGER);
CREATE TABLE moz_inputhistory (place_id INTEGER NOT NULL, input LONGVARCHAR NOT NULL, use_count INTEGER, PRIMARY KEY (place_id, input));
CREATE TABLE moz_items_annos (id INTEGER PRIMARY KEY,item_id INTEGER NOT NULL,anno_attribute_id INTEGER,mime_type VARCHAR(32) DEFAULT NULL,content LONGVARCHAR, flags INTEGER DEFAULT 0,expiration INTEGER DEFAULT 0,type INTEGER DEFAULT 0,dateAdded INTEGER DEFAULT 0,lastModified INTEGER DEFAULT 0);
CREATE TABLE moz_keywords (id INTEGER PRIMARY KEY AUTOINCREMENT, keyword TEXT UNIQUE);
CREATE TABLE moz_places (id INTEGER PRIMARY KEY, url LONGVARCHAR, title LONGVARCHAR, rev_host LONGVARCHAR, visit_count INTEGER DEFAULT 0, hidden INTEGER DEFAULT 0 NOT NULL, typed INTEGER DEFAULT 0 NOT NULL, favicon_id INTEGER, frecency INTEGER DEFAULT -1 NOT NULL);
CREATE UNIQUE INDEX moz_annos_placeattributeindex ON moz_annos (place_id, anno_attribute_id);
CREATE INDEX moz_bookmarks_itemindex ON moz_bookmarks (fk,type);
CREATE INDEX moz_bookmarks_itemlastmodifiedindex ON moz_bookmarks (fk, lastModified);
CREATE INDEX moz_bookmarks_parentindex ON moz_bookmarks (parent,position);
CREATE INDEX moz_historyvisits_dateindex ON moz_historyvisits (visit_date);
CREATE INDEX moz_historyvisits_fromindex ON moz_historyvisits (from_visit);
CREATE INDEX moz_historyvisits_placedateindex ON moz_historyvisits (place_id, visit_date);
CREATE UNIQUE INDEX moz_items_annos_itemattributeindex ON moz_items_annos (item_id, anno_attribute_id);
CREATE INDEX moz_places_faviconindex ON moz_places (favicon_id);
CREATE INDEX moz_places_frecencyindex ON moz_places (frecency);
CREATE INDEX moz_places_hostindex ON moz_places (rev_host);
CREATE UNIQUE INDEX moz_places_url_uniqueindex ON moz_places (url);
CREATE INDEX moz_places_visitcount ON moz_places (visit_count);
CREATE TRIGGER moz_bookmarks_beforedelete_v1_trigger BEFORE DELETE ON moz_bookmarks FOR EACH ROW WHEN OLD.keyword_id NOT NULL BEGIN DELETE FROM moz_keywords WHERE id = OLD.keyword_id AND  NOT EXISTS (SELECT id FROM moz_bookmarks WHERE keyword_id = OLD.keyword_id AND id <> OLD.id LIMIT 1); END;
CREATE TRIGGER moz_historyvisits_afterdelete_v1_trigger AFTER DELETE ON moz_historyvisits FOR EACH ROW WHEN OLD.visit_type NOT IN (0,4,7) BEGIN UPDATE moz_places SET visit_count = visit_count - 1 WHERE moz_places.id = OLD.place_id AND visit_count > 0; END;
CREATE TRIGGER moz_historyvisits_afterinsert_v1_trigger AFTER INSERT ON moz_historyvisits FOR EACH ROW WHEN NEW.visit_type NOT IN (0,4,7) BEGIN UPDATE moz_places SET visit_count = visit_count + 1 WHERE moz_places.id = NEW.place_id; END;INSERT INTO moz_bookmarks  (type, parent, position, title, keyword_id, folder_type) VALUES (2, 0, 0, '', NULL, NULL);INSERT INTO moz_bookmarks  (type, parent, position, title, keyword_id, folder_type) VALUES (2, 1, 0, '', NULL, NULL);INSERT INTO moz_bookmarks  (type, parent, position, title, keyword_id, folder_type) VALUES (2, 1, 1, '', NULL, NULL);INSERT INTO moz_bookmarks  (type, parent, position, title, keyword_id, folder_type) VALUES (2, 1, 2, '', NULL, NULL);INSERT INTO moz_bookmarks  (type, parent, position, title, keyword_id, folder_type) VALUES (2, 1, 3, '', NULL, NULL);INSERT INTO moz_bookmarks_roots (root_name, folder_id) VALUES('places',1);INSERT INTO moz_bookmarks_roots (root_name, folder_id) VALUES('menu',2);INSERT INTO moz_bookmarks_roots (root_name, folder_id) VALUES('toolbar',3);INSERT INTO moz_bookmarks_roots (root_name, folder_id) VALUES('tags',4);INSERT INTO moz_bookmarks_roots (root_name, folder_id) VALUES('unfiled',5);""")
                conn.commit()
            except sqlite3.Error, e:
                print "An error occurred:", e.args[0]
            conn.close()
            #FIX ME!!!!!!!!!!!!!!!!!!
            try:
                shutil.copy2('/usr/share/amigu/places.sqlite', self.bookmarks_file)
            except:
                pass

    def get_connection(self):
        """Devuelve una conexión con el archivo que hace de base de datos de los marcadores"""
        try:
            return sqlite3.connect(self.bookmarks_file)
        except sqlite3.Error, e:
            print "An error occurred:", e.args[0]


    def add_bookmarks(self, tree, iter = None, cursor = None, id_parent = None):
        """Añade los marcadores de forma recursiva
        
        Argumentos de entrada:
        tree -> Objeto de tipo gtk.TreeStore que contiene las estructura de marcadores
        iter -> Objeto de tipo gtk.TreeIter que controla la iteraccion (default None)
        cursor -> cursor de acceso a la base de datos (default None)
        id_parent -> identificador del padre (default None)
        """
        if not cursor:
            conn = self.get_connection()
            if conn:
                cursor = conn.cursor()
                iter = tree.get_iter_root()
                q = "SELECT id FROM moz_bookmarks WHERE title='Bookmarks Menu'"
                try:
                    cursor.execute(q)
                    r = cursor.fetchone()
                    if r:
                        id = int(r[0])
                    else:
                        id = 2
                except:
                    pass
                else:
                    self.add_bookmarks(tree, iter, cursor, id)
                    conn.commit()
                conn.close()
        else:
            while iter:
                title = tree.get_value(iter, 0)
                url = tree.get_value(iter, 1)
                if url and id_parent:
                    #enlace
                    title = tree.get_value(iter, 0)
                    host = '.'+url.split('/')[2]
                    host = host[::-1]
                    id = 0
                    q = "SELECT moz_places.id, moz_bookmarks.parent FROM moz_places LEFT JOIN moz_bookmarks ON moz_places.id = moz_bookmarks.fk WHERE moz_places.url='%s'" % url
                    cursor.execute(q)
                    r = cursor.fetchone()
                    parent = None
                    if r:
                        id = int(r[0])
                        parent = r[1] and int(r[1])
                    else:
                        q = "INSERT INTO moz_places (url, title, rev_host, favicon_id) VALUES ('%s', '%s', '%s', NULL)" % (url, title, host)
                        cursor.execute(q)
                        id = cursor.lastrowid
                    if id and parent != id_parent:
                        q = "INSERT INTO moz_bookmarks  (fk, type, parent, position, title, keyword_id, folder_type, dateAdded, lastModified) VALUES (%d, 1, %d, 101, '%s', NULL, NULL, %d, %d)" % (id, id_parent, title, int(time.time()),  int(time.time()))
                        cursor.execute(q)
                else:
                    #carpeta
                    q ="SELECT id FROM moz_bookmarks WHERE title='%s'" % title
                    cursor.execute(q)
                    r = cursor.fetchone()
                    if r:
                        id = int(r[0])
                    else:
                        q = "INSERT INTO moz_bookmarks  (type, parent, position, title, keyword_id, folder_type, dateAdded, lastModified) VALUES (2, %d, 100, '%s', NULL, NULL, %d, %d)" % (id_parent, title, int(time.time()),  int(time.time()))
                        cursor.execute(q)
                        id = cursor.lastrowid
                    iter_children = tree.iter_children(iter)
                    self.add_bookmarks(tree, iter_children, cursor, id)
                iter = tree.iter_next(iter)

########################################################################


class konqueror():
    """Clase para el navegador Konqueror de KDE (NO TERMINADA)"""

    def __init__(self,folders):
        """Contructor de la clase.
        Recibe un diccionario con las rutas obtenidas del registro"""

        konqueror = folder(os.path.join(os.path.expanduser('~'),'.kde','share','apps','konqueror'))
        self.bookmarks_file = os.path.join(konqueror.path,'bookmarks.xml')
        #create bookmark.xml if not exists
        if not os.path.exists(self.bookmarks_file):
            try:
                b = open(self.bookmarks_file, 'w')
                b.write ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<!DOCTYPE xbel>\n<xbel>\n</xbel>")
                b.close()
            except:
                self.error("Unable to create bookmarks.xml for Konqueror")

    def import_favorites_IE(self):
        """Importa los favoritos de Internet Explorer"""
        if backup(self.bookmarks_file):
            try:
                b = open(self.bookmarks_file, 'w')
                o = open(self.bookmarks_file + '.bak',"r")
            except:
                b.close()
                o.close()
                self.report['iexplorer'] = 'Failed to modify bookmarks.xml'
                restore_backup(self.bookmarks_file + '.bak')
            else:
                # copiar los marcadores
                for linea in o.readlines():
                    if re.search('</xbel>', linea):
                        b.write(' <folder>\n')
                        b.write('  <title>Favoritos de IExplorer</title>\n')
                        self.add_favorites(self.favoritesIE.path, "   ", b)
                        b.write(' </folder>\n')
                    b.write(linea)
                self.report['iexplorer'] = 'Imported Favorites from IExplorer successfully'
                b.close()
                o.close()

    def add_favorites(self, orig, tab, fd):
        """Recorrido recursivo sobre las carpetas de favoritos.
        Recibe el elemento actual, el nivel de tabulación y el descriptor del fichero de escritura"""
        for e in os.listdir(orig):
            ruta = os.path.join(orig, e)
            if os.path.exists(ruta) and os.path.isdir(ruta):
                # recursive case
                fd.write(tab + '<folder>\n')
                fd.write(tab + '<title>' + e + '</title>\n')
                self.add_favorites(ruta, tab + " ", fd)
                fd.write(tab + '</folder>\n')
            elif os.path.exists(ruta) and os.path.isfile(ruta):
                # base case
                (name, ext) = os.path.splitext(e)
                if ext == '.url':
                    try:
                        f = open(ruta, "r")
                        for l in f.read().split("\n"):
                            if re.search('URL=', l):
                                href = l.replace('URL=','HREF=\"').replace('\r\n','\"')
                                fd.write('<bookmark href="%s">\n' % l)
                                fd.write('<title>%s</title>\n' % name)
                                fd.write('</bookmark>\n')
                    finally:
                        f.close()

    def import_bookmarks_firefox(self):
        """Importa los marcadores de Mozilla-Firefox"""
        win_bookmarks = self.get_firefox_bookmarks('windows')
        if backup(self.bookmarks_file):
            try:
                b = open(self.bookmarks_file, "w")
                orig = open(self.bookmarks_file + '.bak',"r")
                wb = open(win_bookmarks, "r")
            except:
                b.close()
                orig.close()
                wb.close()
                self.report['firefox'] = "Failed to modify bookmarks.xml"
                restore_backup(self.bookmarks_file + '.bak')
            else:
                folder = re.compile('.*<DT><H3.*>(?P<name>.+)</H3>')
                bmark = re.compile('.*<DT><A HREF=(?P<url>.+) .*>(?P<name>.+)</A>')
                tab = ' '
                for l in orig.readlines():
                    if re.search('</xbel>', l):
                        b.write('<folder>\n')
                        b.write(tab + '<title>Marcadores importados de Mozilla Firefox</title>\n')
                        for e in wb.readlines():
                            res1 = folder.match(e)
                            res2 = bmark.match(e)
                            if res1:
                                b.write(tab + '<folder>\n')
                                tab = tab + ' '
                                b.write(tab + '<title>%s</title>\n' % res1.group('name'))
                            elif res2:
                                b.write(tab + '<bookmark href=%s>\n' % res2.group('url'))
                                b.write(tab + ' <title>%s</title>\n' % res2.group('name'))
                                b.write(tab + '</bookmark>\n')
                    b.write(l)
                self.report['firefox'] = 'Imported Bookmarks from Mozilla-Firefox successfully'
                b.close()
                wb.close()
                orig.close()

    def import_bookmarks_opera(self):
        """Importa los marcadores de Opera"""
        opera_bookmarks = self.get_opera_bookmarks()
        if backup(self.bookmarks_file) and opera_bookmarks:
            try:
                b = open(self.bookmarks_file, 'w')
                o = open(self.bookmarks_file + '.bak',"r")
            except:
                b.close()
                o.close()
                self.report['opera'] = 'Failed to modify bookmarks.xml'
                # si falla se restaura la copia de seguridad
                restore_backup(self.bookmarks_file + '.bak')
            else:
                for l in o.readlines():
                    if re.search('</xbel>', l):
                        b.write('<folder>\n')
                        b.write('<title>Marcadores importados de Opera</title>\n')
                        tab = ' '
                        for m in opera_bookmarks:
                            for folder, list_links in m.iteritems():
                                b.write(tab + '<folder>\n')
                                tab = tab + ' '
                                b.write(tab + '<title>%s</title>\n' % folder)
                                for e in list_links:
                                    for name, url in e.iteritems():
                                        b.write(tab + '<bookmark href="%s">\n' % url)
                                        b.write(tab + ' <title>%s</title>\n' % name)
                                        b.write(tab +'</bookmark>\n')
                                tab = tab[:-1]
                                b.write(tab + '</folder>\n')
                    b.write(l)
                self.report['opera'] = 'Imported bookmarks from Opera successfully'
                b.close()
                o.close()

# end class konqueror

############################################################################


if __name__ == "__main__":
    from amigu.computer.info import pc
    from amigu.computer.users.mswin import winuser
    com = pc()
    com.check_all_partitions()
    print "Analizando usuarios de Windows"
    for user_path, ops in com.get_win_users().iteritems():
        u = winuser(user_path, com, ops)
        firefox3()
        u.clean()
