#! /usr/bin/env python
# -*- coding: utf-8 -*-

import commands
import re
import os
#import tempfile

class partition:
    """Clase para el manejo de particiones del sistema"""

    def __init__(self, dev, ops=None, fs=None):
        """Constructor de la clase
        
        Argumentos de entrada:
        dev -- dispositivo de bloques
        os -- sistema de operativo instalado (default None)
        """
        if os.path.exists(dev):
            self.dev = dev
        else:
            raise Exception(dev, "Invalid device")
        self.filesystem = fs
        self.mountpoint = None
        self.installed_os = ops
        self.users_path = []
        

    def check(self):
        """Monta la partición y comprueba su contenido"""
        self.is_mounted(True)
        if self.mountpoint is None:
            return  0
        self.detect_os()
        self.search_users()

    def __unicode__(self):
        return "Dispositivo: %s  \
                \nPunto de montaje: %s  \
                \nSistema Operativo: %s \
                \nSistema de ficheros: %s  \
                \nDirectorio de usuarios: %s \n" % (
                 self.dev, self.mountpoint, self.installed_os, self.filesystem, self.users_path)

    def is_mounted(self, automount=False):
        """Comprueba si la partición está montada y devuelve el punto de
        montaje actual en caso afirmativo
        
        """
        mounted = False
        error = False
        try:
            f = open("/etc/mtab",'r')
        except:
            print 'No se puede determinar las unidades montadas'
        else:
            l = re.compile('\s*(?P<dev>[/\-\w]+)\s+(?P<mountpoint>[/\-\w]+)\s+(?P<filesystem>\w+)\s+\.*')
            for entrada in f.readlines():
                disk = l.match(entrada)
                try:
                    if disk.group('dev') == self.dev:
                        mounted = disk.group('mountpoint')
                        self.mountpoint = mounted
                        self.filesystem = self.filesystem is None and disk.group('filesystem') or self.filesystem
                        error = False
                        break
                except:
                    pass
            f.close()
            if not mounted and automount and not error:
                os.system('gvfs-mount -d %s' % (self.dev))
                #os.system('gksudo \"mount -o ro %s %s\"' % (self.dev, tempfile.mkdtemp()))
                #gksu2.sudo('mount -o ro %s %s' % (self.dev, tempfile.mkdtemp()))
                mounted = self.is_mounted(False)
            return mounted
            
    def umount(self):
        if self.mountpoint:
            #gksu2.sudo('umount %s' % self.dev)
            os.system('gvfs-mount -u %s' % self.mountpoint)
            
           

    def detect_os(self):
        """Detecta el tipo de sistema operativo que contiene la partición.
        La deteccion está basada en el sistema de ficheros y las carpetas
        existentes en él
        
        """
        if self.installed_os:
            return 1
        if self.filesystem == 'vfat':
            if os.path.exists(os.path.join(self.mountpoint, 'Documents and Settings')):
                self.installed_os = "MS Windows 2000/XP"
            else:
                self.installed_os = "MS Windows"
        elif self.filesystem == 'ntfs' or self.filesystem == 'fuseblk':
            if os.path.exists(os.path.join(self.mountpoint, 'Users')):
                self.installed_os = "MS Windows Vista/Se7en"
            elif os.path.exists(os.path.join(self.mountpoint, 'Documents and Settings')):
                self.installed_os = "MS Windows 2000/XP"
            elif self.filesystem == 'fuseblk':
                self.installed_os = "Unknown"
        elif self.filesystem in ('ext2', 'ext3', 'reiserfs', 'jfs', 'xfs', 'ext4'):
            if os.path.exists(os.path.join(self.mountpoint, 'bin')) or os.path.exists(os.path.join(self.mountpoint, 'lost+found')):
                self.installed_os = "Unix/Linux"
        elif self.filesystem in ('hfs', 'hfsplus'):
            self.installed_os = "Apple Mac OS X"

    def search_users(self):
        """Busca posibles usuarios en la particiones detectadas"""
        #directorios que no se deben tener en cuenta
        excluir = ('All Users', 'Default User', 'Default', 'LocalService',
        'NetworkService', 'Public','etc','boot','lib','tmp','var','proc',
        'dev','lost+found', 'opt', 'sbin', 'sys', 'lib32', 'lib64', 'bin',
         'media', 'srv', 'mnt', 'usr', 'Shared', 'root')
        if self.installed_os is None and self.mountpoint:
            return 0
        if self.installed_os.find('XP') >= 0:
            # Usuarios de Windows XP
            f = os.path.join(self.mountpoint, "Documents and Settings")
            documents = os.path.exists(f) and os.listdir(f) or []
            for d in documents:
                ruta = os.path.join(self.mountpoint, 'Documents and Settings', d)
                if (not d in excluir) and (os.path.exists(os.path.join(ruta, 'NTUSER.DAT')) or os.path.exists(os.path.join(ruta, 'ntuser.dat'))):
                    self.users_path.append(ruta)
        elif self.installed_os.find('Vista') >= 0 or self.installed_os.find('7') >= 0:
            # Usuarios de Windows Vista
            f = os.path.join(self.mountpoint, "Users")
            documents = os.path.exists(f) and os.listdir(f) or []
            for d in documents:
                ruta = os.path.join(self.mountpoint, 'Users', d)
                if (not d in excluir) and (os.path.exists(os.path.join(ruta, 'NTUSER.DAT')) or os.path.exists(os.path.join(ruta, 'ntuser.dat'))):
                    self.users_path.append(ruta)
        elif self.installed_os.find('Apple Mac') >= 0:
            # Usuarios de Mac
            f = os.path.join(self.mountpoint, "Users")
            documents = os.path.exists(f) and os.listdir(f) or []
            for d in documents:
                ruta = os.path.join(self.mountpoint, 'Users', d)
                if (not d in excluir) and not d.startswith('.'):
                    self.users_path.append(ruta)
        elif self.installed_os.find('Unix/Linux') >= 0:
            # Usuarios de Unix/Linux
            documents = os.listdir(self.mountpoint)
            for d in documents:
                ruta = os.path.join(self.mountpoint, d)
                if (not d in excluir) and not d.startswith('.') and (os.path.exists(os.path.join(ruta, '.profile')) and os.path.exists(os.path.join(ruta, '.bashrc'))):
                    self.users_path.append(ruta)


class pc:
    """Clase para el manejo de información del PC"""

    def __init__(self):
        """Constructor de la clase"""
        self.errors = []
        self.partitions = []
        for dev, os in self.get_devices().iteritems():
            try:
                self.partitions.append(partition(dev, os))
            except:
                pass
        self.win_users = {}
        self.mac_users = {}
        self.lin_users = {}
        self.win_parts = []


    def get_devices(self):
        """Busca las particiones del equipo que contengan sistemas
        operativos instalados
        """
        listos = commands.getoutput('gksudo os-prober')
        r = {}
        try:
            udi_list = commands.getoutput('lshal | grep  ^udi.*volume')
            for u in udi_list.splitlines():
                if u.find('=') == -1 or u.find('uuid') <  0:
                    #print u
                    continue
                udi = u.split('=')[1]
                dev = commands.getoutput('hal-get-property --udi %s --key block.device' % udi)
                r[dev]=None
        except:
            pass
        for ops in listos.splitlines():
            try:
                r[ops.split(':')[0]]=ops.split(':')[1].replace(" (loader)","")
            except:
                pass
        return r

    def check_all_partitions(self):
        """Comprueba todas las particiones previamente detectadas"""
        print "Comprobando particiones..."
        for p in self.partitions:
            p.check()
            print unicode(p)
            
    def umount_all_partitions(self):
        """Desmonta todas las particiones previamente usadas"""
        print "Liberando particiones..."
        for p in self.partitions:
            p.umount()

    def error(self, e):
        """Almacena los errores en tiempo de ejecución  OBSOLETO """
        self.errors.append(e)

    def get_win_users(self):
        """Devuelve una lista con la ruta a las carpetas de los usuarios de Windows"""
        for p in self.partitions:
            if p.installed_os and p.installed_os.find('Windows') >= 0:
                for path in p.users_path:
                    self.win_users[path] = p.installed_os
        return self.win_users

    def get_lnx_users(self):
        """Devuelve una lista con la ruta a las carpetas de los usuarios de Linux"""
        for p in self.partitions:
            if p.installed_os and p.installed_os.find('Linux') >= 0:
                for path in p.users_path:
                    self.lin_users[path] = p.installed_os
        return self.lin_users

    def get_mac_users(self):
        """Devuelve una lista con la ruta a las carpetas de los usuarios de Mac OS"""
        for p in self.partitions:
            if p.installed_os and p.installed_os.find('Mac') >= 0:
                for path in p.users_path:
                    self.mac_users[path] = p.installed_os
        return self.mac_users

    def get_windows(self):
        """Devuelve las particiones que contienen un Sistema Operativo Windows instalado"""
        r = []
        for p in self.partitions:
            if p.installed_os and p.installed_os.find('Windows') >= 0 or p.filesystem == "fuseblk":
                r.append(p)
        self.win_parts = r
        return r

    def map_win_units(self, dpaths):
        """Devuelve un diccionario que asocia los puntos de montaje de 
        Linux con la asignación de unidades de Windows.
        
        Argumentos de entrada:
        dpaths -- diccionario con las rutas de carpetas de Windows
        
        """
        units = {}
        wp = self.get_windows()

        # CONSIDERAR UNIDADES DE RED #

        for k, v in dpaths.iteritems():
            c = v.split('/',1)
            if c[0] and not (c[0] in units.keys()):
                for part in wp:
                    if  len(c)>1 and part.mountpoint and os.path.exists(os.path.join(part.mountpoint, c[1])):
                        units[c[0]]= part.mountpoint
        return units
#end class pc

if __name__ == "__main__":
    com = pc()
    #for p in computer.partitions:
    #    p.check()
    #    print unicode(p)
    com.check_all_partitions()
    print "Windows: ", str(com.get_win_users().keys())
    print "Linux: ", str(com.get_lnx_users().keys())
    print "Mac: ", str(com.get_mac_users().keys())
    com.umount_all_partitions()




