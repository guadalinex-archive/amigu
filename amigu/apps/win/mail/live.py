# -*- coding: utf-8 -*-

import os
from amigu import _
from amigu.util.folder import *
from amigu.apps.win.mail.base import *


class windowsmail(mailreader):
    
    def initialize(self):
        """Inicializa los valores específicos de la aplicación."""
        self.size = 0
        self.mailconfigs = []
        self.mailboxes = []
        self.name = _("Windows Mail")
      
        self.mailconfigs = self.get_configuration()
        self.description = self.name +": %d "%len(self.mailconfigs)+ _("cuentas de correo")
        for mb in self.mailboxes:
            self.size += mb.get_size()
        if not self.mailconfigs:
            raise Exception


    def get_configuration(self):
        """Devuelve la configuración de la aplicación de correo"""
        configs = []
        for key in self.option:
            try:
                c = mailconfig(key)
            except:
                continue
            else:
                configs.append(c)
            mb = folder(os.path.dirname(key), False)
            if mb.path:
                self.mailboxes.append(mb)
        return configs

    def convert_mailbox(self, mb):
        """Convierte los correos al formato Mailbox.
        
        Argumentos de entrada:
        mb -> fichero que contiene los correos de la aplicación
        
        """
        eml2mbox(mb.path, os.path.join(self.dest.path, mb.path.split('/')[-1]))
        
    def import_calendar(self):
        pass
        
    def import_contacts(self):
        pass

class windowslivemail(windowsmail):
    
    def initialize(self):
        """Inicializa los valores específicos de la aplicación."""
        self.size = 0
        self.mailconfigs = []
        self.mailboxes = []

        self.name = _("Windows Live Mail")
        self.mailconfigs = self.get_configuration()
        self.description = self.name +": %d "%len(self.mailconfigs)+ _("cuentas de correo")
        for mb in self.mailboxes:
            self.size += mb.get_size()
        if not self.mailconfigs:
            raise Exception
