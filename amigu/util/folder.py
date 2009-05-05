# -*- coding: utf-8 -*-
# Este módulo agrupa rutinas para el tratamiento de archivos y carpetas.
# Ofrece la funcionalidad de realizar backup's de archivos y restaurarlos posteriormente.
# Permite le uso de objetos de tipo 'folder' para simplificar y agilizar
# el manejo de las carpetas

import os, re, shutil
from os.path import isdir, isfile, exists, split, basename, dirname, splitext, join
from amigu.apps.base import application
from amigu import _

def backup(file):
    """Crea una copia de respaldo del archivo que se le indica"""
    if exists(file):
        try:
            progress('Doing backup of ' + file)
            shutil.copy2(file, file + '.bak')
            return file + '.bak'
        except (IOError, os.error), why:
            error("Can't backup %s: %s" % (file, str(why)))


def restore_backup(backup):
    """Restaura la copia de respaldo del archivo que se le indica"""
    if exists(backup):
        try:
            progress('Restoring backup of ' + backup[:-4])
            shutil.copy2(backup, backup[:-4])
            return 1
        except (IOError, os.error), why:
            error("Can't restore backup %s: %s" % (backup, str(why)))

def odf_converter(file, format = 'pdf'):
    try:
        os.system("unoconv -f %s %s" % (format, file.replace(' ', '\ ')))
    except:
        pass

def error(e):
    """Error handler"""
    print e

def warning(w):
    """Show warnings"""
    print w

def progress(p):
    """Show the progress"""
    pass

class folder:
    """Clase para el manejo de carpetas y archivos"""
    #
    # rutas por defecto
    #
    __DIR_BACKUP__="/tmp/migration-assistant"
    __DIR_MUSIC__='~/Music'
    __DIR_PICTURES__='~/Pictures'
    __DIR_VIDEO__='~/Video'
    #
    # extensiones
    #
    prefolders =   {"Desktop": _("Desktop"), 
                    "Documents": _("Documents"),
                    "Videos": _("Videos"),
                    "Music": _("Music"),
                    "Pictures": _("Pictures"),
                    "Downloads": _("Downloads")
                }
    
    document_files = ['.sxv', '.doc', '.xml', '.rtf', '.sdw']
    presentation_files = ['.pot', '.ppt']
    spread_files = ['.xls', '.xlt', '.sxc']
    texto = ['.sxv', '.stw', '.doc', '.rtf', '.sdw', '.var', '.txt', '.html', '.htm', '.pdf']
    calculo = ['.sxc', '.stc', '.dif', '.dbf', '.xls', '.xlw', '.xlt', '.sdc', '.vor', '.slk', '.csv', '.txt', '.html', '.htm']
    presentacion = ['.sxi', '.sti', '.ppt', '.pps', '.pot', '.sxd', '.sda', '.sdd', '.vor', '.pdf']
    pictures = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.pdf', '.ico', '.tif', '.tiff']
    audio = ['.wma', '.asf', '.wav', '.mp2', '.mp3', '.aac', '.m4a', '.ogg', '.mp4', '.mid', '.midi', '.dts', '.ac3']
    video = ['.avi', '.mpg', '.mpeg', '.divx', '.mov', '.mp4', '.vob', '.ifo', '.bup', '.wmv', '.3gp', '.ogm', '.mkv', '.rm']
    compresion = ['.zip', '.rar', '.r*' , '.7z', '.cab', '.tar', '.gz' , '.bz', '.bz2', '.ace', '.arj', '.z', '.cpio', '.rpm', '.deb', '.lzma', '.rz', '.arc', '.alz', '.arj', '.zz', '.tar.gz', '.tgz', '.tar.Z', '.tar.bz2', '.tbz2']
    ejecutable = ['.exe']
    edonkey = ['.dat', '.part', '.part.met', '.met']

    def __init__(self, path, create = True):
        """Constructor de la clase.
        Recibe una ruta y si no existe la crea"""
        self.errors = []
        self.path = None
        if exists(path) and isdir(path):
            self.path = path
        elif not exists(path) and create:
            self.path = self.create_folder(path)
        self.files = None
        self.dirs = None
        if self.errors:
            print self.errors
            #self.path = path

    def get_name(self):
        name = basename(self.path)
        if name in self.prefolders:
            name = self.prefolders[name]
        return name

    def error(self, e):
        """Almacena los errores en tiempo de ejecución"""
        self.errors.append(e)

    def get_path(self):
        """Devuelve la ruta del objeto"""
        return self.path

    def is_writable(self):
        """Devuelve si tiene permisos de escritura sobre la carpeta"""
        return os.access(self.path, os.W_OK)

    def is_readable(self):
        """Devuelve si tiene permisos de lectura sobre la carpeta"""
        return os.access(self.path, os.R_OK)

    def get_info(self):
        """Devuelve información con el número de archivos y carpetas y el tamaño del objeto"""
        size = self.get_size()
        if size > 1024*1024:
            size = str(size/(1024*1024)) + 'GB'
        elif size > 1024:
            size = str(size/1024) + 'MB'
        else:
            size = str(size) + 'KB'
        return '%d archivos en %d carpetas ocupando %s en disco' % (self.count_files(), self.count_dirs(), size)

    def get_size(self):
        """Devuelve el tamaño de la carpeta"""
        if self.path:
            try:
                tam = os.popen('du -s ' + self.path.replace(' ','\ ').replace('(','\(').replace(')','\)'))
                return int(tam.read().split('\t')[0])
            except:
                self.error('Size for %s not available' % self.path)
                return 0
        else:
            return 0

    def count_files(self):
        if self.files is None:
            self.files = self.count(self.path, 0, 0)[1]
        return self.files

    def count_dirs(self):
        if self.dirs is None:
            self.dirs = self.count(self.path, 0, 0)[0]
        return self.dirs

    def count(self, path, dirs, files):
        """Devuelve el número de archivos y carpetas de forma recursiva"""
        try:
            for e in os.listdir(path):
                if isdir(join(path, e)):
                    dirs, files = self.count(join(path, e), dirs, files)
                    dirs = dirs + 1
                elif isfile(join(path, e)):
                    files = files + 1
        except: pass
        return dirs, files

    def get_free_space(self):
        """Devuelve el espacio libre en la carpeta"""
        try:
            df = os.popen('df ' + self.path.replace(' ','\ '))
        except:
            self.error ("Free space not available")
        else:
            df.readline()
            file_sys,disc_size,disc_used,disc_avail,disc_cap_pct,mount=df.readline().split()
            df.close()
            return int(disc_avail)

    def copy(self, destino, extension = None, convert = True, exclude = ['.lnk',], function = None, delta = 0):
        """Copia solo los archivos de la ruta origen que tienen la misma extension que la especificada en la lista de 'extensiones'"""
        if not isinstance(destino, folder):
            destino = folder(join(destino, self.get_name()))
        for e in os.listdir(self.path):
            ruta = join(self.path, e)
            try:
                if isdir(ruta):
                    # caso recursivo
                    suborigen = folder(ruta)
                    subdestino = folder(join(destino.path, e))
                    if suborigen.path and subdestino.path:
                        suborigen.copy(subdestino, extension, convert, exclude, function, delta)
                elif isfile(ruta):
                    # caso base
                    ext = splitext(e)[-1]
                    if (not exclude or (not ext in exclude)) and (not extension or (ext in extension)): # think about some file to exclude, like .ini o .lnk
                        try:
                            progress(">>> Copying %s..." % ruta)
                            shutil.copy2(ruta, destino.path)
                            os.chmod(join(destino.path, e), 0644)
                            if convert and ext in self.document_files:
                                odf_converter(join(destino.path, e), 'odt')
                            elif convert and ext in self.presentation_files:
                                odf_converter(join(destino.path, e), 'odp')
                            elif convert and ext in self.spread_files:
                                odf_converter(join(destino.path, e), 'ods')
                            if function and delta:
                                #for progress bar update
                                function(delta=delta)
                        except:
                            self.error('Imposible copiar ' + e)
                else:
                    # Tipo desconocido, se omite
                    self.error('Skipping %s' % ruta)
            except error:
                self.error('Failed Stat over ' + e)

    def get_subfolders(self):
        for e in os.listdir(self.path):
            ruta = join(self.path, e)
            try:
                if isdir(ruta):
                    yield folder(ruta)
            except:
                pass

    def search_by_ext(self, extension):
        """Devuelve una lista de archivos que cumplen con la extension dada"""
        found = []
        for e in os.listdir(self.path):
            ruta = join(self.path, e)
            try:
                if isdir(ruta):
                    # caso recursivo
                    suborigen = folder(ruta)
                    if suborigen:
                        found += suborigen.search_by_ext(extension)
                elif isfile(ruta):
                    # caso base
                    ext = splitext(e)[1]
                    if (ext == extension ) :
                        #print ruta
                        found.append(ruta)
                else:
                    # Tipo desconocido, se omite
                    self.error('Skipping %s' % ruta)
            except:
                self.error('Failed Stat over ' + e)
        return found

    def create_folder(self, path):
        """Crea la carpeta"""
        try:
            os.makedirs(path)
            return path
        except OSError, e:
            if re.search('Errno 17',str(e)): # if already exists
                return path
            elif re.search('Errno 30',str(e)): # only read path
                self.error('No se puede escribir en ' + path)
            elif re.search('Errno 13',str(e)): # permission denied
                self.error ('Permiso denegado para escribir en ' + path)
            else: # invalid path
                self.error ('Ruta no valida: ' + join(path, folder))

    def create_subfolder(self, subfolder):
        """Crea una subcarpeta en la ruta del objeto"""
        try:
            os.makedirs(join(self.path, subfolder.replace(' ','\ ')))
            return join(self.path, subfolder)
        except OSError, e:
            if re.search('Errno 17',str(e)): # if already exists
                return join(self.path, subfolder)
            elif re.search('Errno 30',str(e)): # only read path
                self.error('No se puede escribir en ' + self.path)
            elif re.search('Errno 13',str(e)): # permission denied
                self.error ('Permiso denegado para escribir en ' + self.path)
            else: # invalid path
                self.error ('Ruta no valida: ' + join(self.path, subfolder))



class copier(application):
    
    def initialize(self):

        self.name = _(self.option.get_name())
        self.size = self.option.get_size()
        self.files = self.option.count_files()
        self.copied = 0
        self.type = "data"
        self.destination = None
        self.path = self.option
        self.description = _("Carpeta") + " '%s': %d " % (self.name, self.files) + _("archivos")

    def set_destination(self, dest):
        if type(dest) == folder:
            self.destination = dest.path
        elif exists(dest) and isdir(dest):
            self.destination = dest

    def do(self):
        self.option.errors = []
        inc = 0
        if self.model:
            inc = 100.0/(self.files+1)
        self.option.copy(destino=self.destination, function=self.update_progress, delta=inc)
        if not self.option.errors:
            return 1
        else:
            print self.option.errors


if __name__ == "__main__":
    f = folder('/home/fernando/Audio')
    print f.get_name()
    print f.get_info()
    print 'freespace: %dKB' % f.get_free_space()
    for s in f.get_subfolders():
        print s.get_name()
    print f.search_by_ext('.txt')
    f.copy('/tmp')
    print f.errors

