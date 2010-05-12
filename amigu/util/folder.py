# -*- coding: utf-8 -*-
# Este módulo agrupa rutinas para el tratamiento de archivos y carpetas.
# Ofrece la funcionalidad de realizar backup's de archivos y restaurarlos posteriormente.
# Permite le uso de objetos de tipo 'folder' para simplificar y agilizar
# el manejo de las carpetas

import os
import re
import shutil
import commands
from os.path import isdir, isfile, exists, split, basename, dirname, splitext, join, getsize
from amigu.apps.base import application
from amigu import _
import subprocess
from threading import Timer

abort_copy = False

def backup(file):
    """Crea una copia de respaldo del archivo que se le indica.
    Devuelve el nombre del fichero creado.
    
    Argumentos de entrada:
    file -> ruta del archivo
    
    """
    if exists(file):
        try:
            progress('Doing backup of ' + file)
            shutil.copy2(file, file + '.bak')
            return file + '.bak'
        except (IOError, os.error), why:
            error("Can't backup %s: %s" % (file, str(why)))


def restore_backup(backup):
    """Restaura la copia de respaldo del archivo que se le indica
    
    Argumentos de entrada:
    backup -> ruta de la copia de respaldo
    
    """
    if exists(backup):
        try:
            progress('Restoring backup of ' + backup[:-4])
            shutil.copy2(backup, backup[:-4])
            return 1
        except (IOError, os.error), why:
            error("Can't restore backup %s: %s" % (backup, str(why)))


        
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
    
    document_files = ['.sxv', '.doc', '.rtf', '.sdw']
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
        
        Argumentos de entrada:
        path -> ruta de la carpeta
        create -> indica si se debe crear la carpeta (default True)
        
        """
        self.errors = []
        self.path = None
        if exists(path) and isdir(path):
            self.path = path
        elif not exists(path) and create:
            self.path = self.create_folder(path)
        self.files = None
        self.dirs = None
        self.subprocesos = []
        if self.errors:
            print self.errors
            #self.path = path

    def get_name(self):
        """Devuelve el nombre de la carpeta"""
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
                tam = commands.getoutput('du -s  "%s"' % self.path)
                return int(tam.split('\t')[0])
            except:
                self.error('Size for %s not available' % self.path)
                return 0
        else:
            return 0

    def count_files(self):
        """Devuelve el número de archivos que contiene la carpeta"""
        if self.files is None:
            self.files = self.count(self.path, 0, 0)[1]
        return self.files

    def count_dirs(self):
        """Devuelve el número de carpetas que contiene la carpeta"""
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
        """Copia solo los archivos de la ruta origen que tienen la misma 
        extension que la especificada en la lista de 'extensiones'
        
        Argumentos de entrada:
        destino -> destino de la copia
        extension -> lista con las extensiones de los ficheros a copiar (default None)
        convert -> indica se debe convertir ficheros a equivalentes libres (defualt True)
        exclude -> lista con las extensiones de los ficheros excluidos (default ['.lnk'])
        function -> función encargada del indicar el progreso de la copia (default None)
        delta -> incremento de progreso por cada archivo copiado (default 0)
        
        """
        i = 0
        global abort_copy
        if not isinstance(destino, folder):
            destino = folder(join(destino, self.get_name()))
        for e in os.listdir(self.path):
            ruta = join(self.path, e)
            try:
                if isdir(ruta):
                    # caso recursivo
                    suborigen = folder(ruta)
                    subdestino = folder(join(destino.path, e))
                    if suborigen.path and subdestino.path and not abort_copy:
                        abort_copy = False
                        suborigen.copy(subdestino, extension, convert, exclude, function, delta)
                elif isfile(ruta):
                    # caso base
                    if e == "desktop.ini":
                        continue
                    ext = splitext(e)[-1]
                    if (not exclude or (not ext in exclude)) and (not extension or (ext in extension)) and not abort_copy: # think about some file to exclude, like .ini o .lnk
                        try:
                            progress(">>> Copying %s..." % ruta)
                            shutil.copy2(ruta, destino.path)
                            os.chmod(join(destino.path, e), 0644)
                            if function and delta:
                                #for progress bar update
                                function(1, 1)
                                function(delta=delta)
                        except:
                            self.error('Imposible copiar ' + e)
                else:
                    # Tipo desconocido, se omite
                    self.error('Skipping %s' % ruta)
                    
            except error:
                self.error('Failed Stat over ' + e)


    def get_subfolders(self):
        """Devuelve una lista con las subcarpetas"""
        for e in os.listdir(self.path):
            ruta = join(self.path, e)
            try:
                if isdir(ruta):
                    yield folder(ruta)
            except:
                pass

    def search_by_ext(self, extensions):
        """Devuelve una lista de archivos que cumplen con la extension dada
        
        Argumentos de entrada:
        extension -> extensión para el filtrado de los ficheros
        
        """
        found = []
        for e in os.listdir(self.path):
            ruta = join(self.path, e)
            try:
                if isdir(ruta):
                    # caso recursivo
                    suborigen = folder(ruta)
                    if suborigen:
                        found += suborigen.search_by_ext(extensions)
                elif isfile(ruta):
                    # caso base
                    ext = splitext(e)[1]
                    if (ext in extensions ) :
                        #print ruta
                        found.append(ruta)
                else:
                    # Tipo desconocido, se omite
                    self.error('Skipping %s' % ruta)
            except:
                self.error('Failed Stat over ' + e)
        return found

    def create_folder(self, path):
        """Crea la carpeta
        
        Argumentos de entrada:
        path -> ruta de la carpeta a crear
        
        """
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
        """Crea una subcarpeta en la ruta del objeto
        
        Argumentos de entrada:
        subfolder -> nombre de la subcarpeta a crear
        
        """
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

class converter(application):
    """Clase para el manejo de conversión de archivos"""
    def initialize(self):
        """Inicializa los parametros específicos de la aplicación"""
        if not os.path.exists("/usr/bin/unoconv"):
            raise Exception
        self.name = _("Convertir archivos de ofimática")
        self.filelist = self.option.search_by_ext(self.option.document_files + self.option.presentation_files + self.option.spread_files)
        self.files = len(self.filelist)
        if not self.files:
            raise Exception
        self.size = self.get_total_size()
        self.copied = 0
        self.type = "data"
        self.destination = None
        self.timer = None
        self.path = self.option
        self.description = _("Conversión de") + " %d " % self.files + _("archivos ofimáticos")

    def get_total_size(self):
        accum = 0
        for f in self.filelist:
            tam = commands.getoutput('du -s "%s"' % f)
            try:
                accum += int(tam.split('\t')[0])
            except: 
                pass
        return accum

    def set_destination(self, dest):
        """Establece el destino de la copia.
        
        Argumentos de entrada:
        dest -> destino de la copia, puede ser una ruta o un objeto de tipo 'folder'
        
        """
        if type(dest) == folder:
            self.destination = dest.path
        elif exists(dest) and isdir(dest):
            self.destination = dest

    def do(self):
        """Realiza el proceso de importación"""
        self.option.errors = []
        inc = 0
        errors = 0
        if self.model:
            inc = 100.0/(self.files + 1)
        self.abort = False
        dest = folder(self.destination)
        self.destination = dest.create_subfolder(_("Convertidos"))
        for f in self.filelist:
            if self.abort:
                break
            s = None
            ext = splitext(f)[1]
            if ext in self.option.document_files:
                s = self.odf_converter(f, 'odt')
            elif ext in self.option.presentation_files:
                s = self.odf_converter(f, 'odp')
            elif ext in self.option.spread_files:
                s = self.odf_converter(f, 'ods')
            if not s:
                continue
            if s.wait() < 0:
                errors += 1
            else:
                errors -= 1
                self.update_progress(1, 1)
                self.update_progress(delta=inc)
            self.outpipe.close()
            self.timer.cancel()
            if errors >= 10:
                self.cancel()
                return 0
            elif errors < 0:
                errors = 0
        return 1
                
    def odf_converter(self, file, format = 'pdf'):
        """Convierte el fichero recibido a formato compatible con OpenOffice.org
        
        Argumentos de entrada:
        file -> ruta del fichero
        format -> tipo de formato de salida (default "pdf")
        
        """
        s = None
        if not exists(file):
            return s
        output = file.replace(self.user.path, self.destination)
        ext = splitext(file)[1]
        folder(dirname(output))
        self.outpipe = open(output.replace(ext, "."+format) , "w")
        try:
            #os.system("unoconv -f %s %s" % (format, file.replace(' ', '\ ')))
            s = subprocess.Popen(["unoconv", "--stdout" , "-f", format, file], stdout=self.outpipe)
            self.timer = Timer(30, s.kill)
            self.timer.start()
        except:
            s.wait()
        return s



class copier(application):
    """Clase para el manejo de importación de archivos"""
    
    def initialize(self):
        """Inicializa los parametros específicos de la aplicación"""

        self.name = self.option.get_name()
        self.size = self.option.get_size()
        self.files = self.option.count_files()
        self.copied = 0
        self.type = "data"
        self.destination = None
        self.path = self.option
        self.description = _("Carpeta") + " '%s': %d " % (self.name, self.files) + _("archivos")

    def set_destination(self, dest):
        """Establece el destino de la copia.
        
        Argumentos de entrada:
        dest -> destino de la copia, puede ser una ruta o un objeto de tipo 'folder'
        
        """
        if type(dest) == folder:
            self.destination = dest.path
        elif exists(dest) and isdir(dest):
            self.destination = dest

    def do(self):
        """Realiza el proceso de importación"""
        self.option.errors = []
        inc = 0
        if self.model:
            inc = 100.0/(self.files+1)
        self.abort = False
        global abort_copy
        abort_copy = False
        self.copied = 0
        self.option.copy(destino=self.destination, function=self.update_progress, delta=inc)
        if not self.option.errors:
            return 1
        else:
            print self.option.errors

    def cancel(self):
        """Método para detener la ejecución del a tarea        .
        
        """
        self.abort = True
        global abort_copy
        abort_copy = True

if __name__ == "__main__":
    f = folder('/home/fernando/Documentos')
    print f.get_name()
    print f.get_info()
    print 'freespace: %dKB' % f.get_free_space()
    for s in f.get_subfolders():
        print s.get_name()
    print f.search_by_ext([".odt"])
    #f.copy('/tmp')
    print f.errors

