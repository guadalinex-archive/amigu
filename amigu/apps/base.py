# -*- coding: utf-8 -*-
import uuid
import sys
import traceback
import gtk
from amigu import _

class application:

    def __init__(self, user, option = None):
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
        try:
            self.initialize()
        except:
            cla, exc, trbk = sys.exc_info()
            print "Error: %s\nArgs: %s\nTrace: %s" % (cla.__name__, exc, traceback.format_tb(trbk, 10))
            raise Exception
        self.error = ''

    def initialize(self):
        print _("Desktop")
        pass

    def run(self, model=None, iter=None):
        self.model = model
        self.iter = iter
        self.status = -1
        try:
            if self.do():
                self.status = 1
        except:
            cla, exc, trbk = sys.exc_info()
            self.error = "Error: %s\nArgs: %s\nTrace: %s" % (cla.__name__, exc, traceback.format_tb(trbk, 10))
            


    def do(self):
        pass
        
    def update_progress(self, value = 0, delta=0):
        try:
            gtk.gdk.threads_enter()
            if value: self.model.set_value(self.iter, 2, value)
            elif delta: self.model.set_value(self.iter, 2, delta + float(self.model.get_value(self.iter, 2)))
        except: 
            pass
        finally:
            gtk.gdk.threads_leave()


