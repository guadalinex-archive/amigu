# -*- coding: utf-8 -*-
# La clase regedit permite acceder a la información contenida en el registro de Windows.
# La compatibilidad con los registros de Windows viene dada por el programa 'dumphive'
# que convierte el contenido del registro en un fichero de texto plano.
# Se añade la función genérica de buscar cualquier entrada del registro.
import os
import codecs
import tempfile
from folder import *

class regedit:
    """Clase para el registro de Windows"""
    
    __dumphive="/usr/bin/dumphive"
    #__dumphive="./bin/dumphive"

    def __init__(self, dir):
        """Constructor de la clase.
        
        Argumentos de entrada:
        dir -> ruta de un directorio que contenga un archivo del registro de Windows
        
        """
        self.tempreg = tempfile.mktemp()
        self.errors = []
        ntuser1 = os.path.join(dir, 'NTUSER.DAT')
        ntuser2 = os.path.join(dir, 'ntuser.dat') # for case sensistives filesystems
        system = os.path.join(dir, 'WINDOWS','system32','config','system')
        if os.path.exists(self.__dumphive):
            if os.path.exists(ntuser1):
                try:
                    os.system("%s %s %s" % (self.__dumphive, ntuser1.replace(" ","\ "), self.tempreg))
                except:
                    self.errors.append('Failed to read user registry')
            elif os.path.exists(ntuser2):
                try:
                    os.system("%s %s %s" % (self.__dumphive, ntuser2.replace(" ","\ "), self.tempreg))
                except:
                    self.errors.append('Failed to read user registry')
            elif os.path.exists(system):
                try:
                    os.system("%s %s %s" % (self.__dumphive, system.replace(" ","\ "), self.tempreg))
                except:
                    self.errors.append('Failed to read system registry')
            else:
                raise Exception(path, "Registry not found")
        else:
            raise Exception(self.__dumphive, "Parser not found")

    def error (self, e):
        """Alamacena los errores en tiempo de ejecución"""
        self.errors.append(e)

    def search_key(self, key):
        """Devuelve un diccionario con el valor asociado a la clave del registro
        
        Argumentos de entrada:
        key -> clave del registro de Windows
        
        """
        try:
            reg = codecs.open(self.tempreg, 'r', 'iso-8859-1')
        except:
            self.error('No fue posible acceder al archivo')
        else:
            entrada = "a"
            res = {}
            while not res and entrada != "":
                entrada = reg.readline()
                if entrada.find(key) != -1:
                    while entrada != "\r\n":
                        entrada = reg.readline()
                        if entrada != "\r\n":
                            #entrada = entrada.encode('utf-8')
                            entrada = entrada.replace('\\\\','/')
                            entrada = entrada.replace('\"','')
                            try:
                                separator = entrada.find('=')
                                clave = entrada[:separator]
                                if entrada[-3] == '\\':
                                    valor = entrada[(separator+1):-3]
                                    while entrada[-3] == '\\': 
                                        entrada = reg.readline()
                                        if entrada[-3] == '\\':
                                            valor += entrada[2:-3]
                                        else:
                                            valor += entrada[2:-2]
                                else:
                                    valor = entrada[(separator+1):-2]
                                res[clave]=valor
                            except:
                                self.error("error de lectura en el registro")
            reg.close()
            return res


    def clean (self):
        """Borra el archivo temporal del registro"""
        try:
            os.system('rm %s' % self.tempreg)
            #os.system('rm %s' % self.user_reg)
            #os.system('rm %s' % self.system_reg)
        except:
            self.error("Can't erase tempfiles")

# end class winregistry
