# -*- coding: utf-8 -*-

import uuid
import sys
import traceback
import gtk
import sys
from amigu import _
from threading import Timer

class application:
    """Clase abstracta el manejo de aplicaciones y opciones de migración"""
    
    def __init__(self, user, option = None):
        """Constructor de la clase.
        
        Argumentos de entrada:
        user -- objeto de tipo Generic_usr
        option -- opción especifica de la aplicación que implemente la clase (default None)
        
        """
        self.user = user
        self.id = str(uuid.uuid4())
        self.os = user.os
        self.name = ""
        self.description = ""
        self.type = "conf"
        self.size = None
        self.status = 0
        self.progress = 0
        self.option = option
        self.abort = False
        self.timer = None
        try:
            self.initialize()
        except:
            cla, exc, trbk = sys.exc_info()
            print "Error: %s (%s)\nArgs: %s\nTrace: %s" % (cla.__name__, self.name, exc, traceback.format_tb(trbk, 10))
            raise Exception
        self.error = ''

    def initialize(self):
        """Método abstracto para que las clases hijas personalicen la 
        aplicación
        
        """
        pass

    def run(self, model=None, iter=None):
        """Ejecuta la tarea y controla su resultado.
        
        Argumentos de entrada:
        model -- objeto de tipo gtk.TreeModel obtenido del arbol de opciones
        iter -- objeto de tipo gtk.TreeIter obtenido del arbol de opciones
        
        """
        self.model = model
        self.iter = iter
        self.status = -1
        try:
            if self.do():
                self.status = 1
            if self.abort:
                self.status = 0
        except:
            cla, exc, trbk = sys.exc_info()
            self.error = "Error: %s\nArgs: %s\nTrace: %s" % (cla.__name__, exc, traceback.format_tb(trbk, 10))
        finally:
            self.pulse_stop()


    def do(self):
        """Método abstracto para que las clases hijas implementen 
        el proceso de migración/importación.
        
        """
        pass
        
    def cancel(self):
        """Método para detener la ejecución del a tarea        .
        
        """
        self.abort = True
        
    def update_progress(self, value = 0, delta=0):
        """Actualiza la barra de progreso asociada a la tarea en con un 
        valor concreto o con un incremento relativo. Sólo válido para 
        la interfaz gráfica de Amigu
        
        Argumentos de entrada:
        value -- nuevo valor de la barra de progreso (default 0)
        delta -- nuevo incremento de la barra de progreso (default 0)
        """
        try:
            gtk.gdk.threads_enter()
            if value and delta:
                try:
                    self.copied += value
                    status = _("Migrando...") + " (%d/%d)" % (self.copied, self.files)
                    self.model.set_value(self.iter, 3, status)
                except:
                    pass
            elif value: self.model.set_value(self.iter, 2, value)
            elif delta: self.model.set_value(self.iter, 2, delta + float(self.model.get_value(self.iter, 2)))
        except: 
            pass
        finally:
            gtk.gdk.threads_leave()
            
    def pulse_start(self):
        """Inicia  el indicador de actividad en la barra de progreso. Sólo válido para 
        la interfaz gráfica de Amigu
        
        
        """
        try:
            gtk.gdk.threads_enter()
            self.model.set_value(self.iter, 4, 1)
            self.timer = Timer(0.05, self.update_pulse)
            self.timer.start()
        except: 
            pass
        finally:
            gtk.gdk.threads_leave()
            
    
    def update_pulse(self):
        """Actualiza  el indicador de actividad en la barra de progreso. Sólo válido para 
        la interfaz gráfica de Amigu
        
        
        """
        try:
            gtk.gdk.threads_enter()
            self.model.set_value(self.iter, 4, self.model.get_value(self.iter, 4) + 1)
            self.timer = Timer(0.05, self.update_pulse)
            self.timer.start()
        except: 
            pass
        finally:
            gtk.gdk.threads_leave()
    
    def pulse_stop(self):
        """Detiene el indicador de actividad en la barra de progreso. Sólo válido para 
        la interfaz gráfica de Amigu
        
        
        """
        try:
            gtk.gdk.threads_enter()
            self.model.set_value(self.iter, 4,-1)
            self.timer.cancel()
        except: 
            pass
        finally:
            gtk.gdk.threads_leave()


