# -*- coding: utf-8 -*-

import os
import re
import shutil
import glob
from amigu import _
from amigu.util.folder import *
from amigu.apps.win.mail.base import *

__DIR_PST2MBX__="/usr/bin"
__DIR_DBX2MBX__="/usr/bin"

class outlook12(mailreader):
    """Clase para el manejo de Office 2007 (versión 12)"""
    
    def initialize(self):
        """Inicializa los valores específicos de la aplicación."""
        self.size = 0
        self.mailconfigs = []
        self.mailboxes = []
        
        self.name = _("Outlook 2007")
        self.description = _("Datos y configuraciones de MS Office Outlook 2007")
        pst = os.path.join(self.user.folders["Local AppData"].path, 'Microsoft','Outlook', 'Outlook.pst')
        if os.path.exists(pst):
            self.mailboxes.append(pst)
        self.mailconfigs = self.get_configuration()
        if not self.mailconfigs:
            raise Exception

        for mb in self.mailboxes:
            self.size = os.path.getsize(mb)/1024
        self.description = self.name +": %d "%len(self.mailconfigs)+ _("cuentas de correo")


    def get_configuration(self):
        """Devuelve la configuración de la aplicación de correo"""
        configs = []
        for key in self.option:
            r = self.user.search_key(key)
            if not "Email" in r.keys():
                continue
            pst = None
            for k, v in r.iteritems():
                if v.startswith('hex'):
                    r[k]=hex2str(v)
                if k.find('pst') > 0:
                    pst = k
                if k == 'IMAP Store EID':
                    pst = r[k]
            if pst:
                i = pst.find(':')
                pst = self.user.check_path(pst)
                pst = pst.replace('\\','/')
                if os.path.exists(pst) and not pst in self.mailboxes:
                    self.mailboxes.append(pst)
            try:
                c = mailconfig(r)
            except:
                continue
            else:
                configs.append(c)
        return configs

    def convert_mailbox(self, mb):
        """Convierte los correos al formato Mailbox.
        
        Argumentos de entrada:
        mb -> fichero que contiene los correos de la aplicación
        
        """
        readpst = os.path.join(__DIR_PST2MBX__,'readpst')
        com = '%s -w %s -o %s' % (readpst, mb.replace(' ',"\ "), self.dest.path.replace(' ',"\ "))
        os.system(com)



class outlook11(mailreader):
    
    def initialize(self):
        """Inicializa los valores específicos de la aplicación."""
        self.size = 0
        self.mailconfigs = []
        self.mailboxes = []

        self.name = _("Outlook XP-2002-2003")
        pst = glob.glob(os.path.join(self.user.folders["Local AppData"].path, 'Microsoft','Outlook', '?utlook.pst'))
        if pst and os.path.exists(pst[0]):
            self.mailboxes.append(pst[0])
        self.mailconfigs = self.get_configuration()
        self.description = self.name +": %d "%len(self.mailconfigs)+ _("cuentas de correo")
        if not self.mailconfigs:
            raise Exception

        for mb in self.mailboxes:
            self.size = os.path.getsize(mb)/1024

    def get_configuration(self):
        """Devuelve la configuración de la aplicación de correo"""
        configs = []
        for key in self.option:
            r = self.user.search_key(key)
            if not "Email" in r.keys():
                continue
            for k, v in r.iteritems():
                if v.startswith('hex'):
                    r[k]=hex2str(v)
            
            try:
                pst_file = "*Outlook*"+c.get_server()+'-'+self.option.split('\\')[-1][:-3]+'.pst'
                pst_file = glob.glob(os.path.join(self.user.folders["Local AppData"].path, 'Microsoft','Outlook', pst_file))[0]
                if os.path.exists(pst_file) and not pst_file in self.mailboxes:
                    self.mailboxes.append(pst_file)
            except:
                pass
            try:
                c = mailconfig(r)
            except:
                continue
            else:
                configs.append(c)
        return configs

    def convert_mailbox(self, mb):
        """Convierte los correos al formato Mailbox.
        
        Argumentos de entrada:
        mb -> fichero que contiene los correos de la aplicación
        
        """        
        readpst = os.path.join(__DIR_PST2MBX__,'readpst')
        com = '%s -w %s -o %s' % (readpst, mb.replace(' ',"\ "), self.dest.path.replace(' ',"\ "))
        os.system(com)


class outlook9(mailreader):
    
    def initialize(self):
        """Inicializa los valores específicos de la aplicación."""
        self.size = 0
        self.mailconfigs = []
        self.mailboxes = []

        self.name = _("Outlook 2000")
        self.description = _("Datos y configuraciones de MS Office Outlook 2000")
        pst = glob.glob(os.path.join(self.user.folders["Local AppData"].path, 'Microsoft','Outlook', '?utlook.pst'))

        if pst and os.path.exists(pst[0]):
            self.mailboxes.append(pst[0])
        self.mailconfigs = self.get_configuration()
        for mb in self.mailboxes:
            self.size = os.path.getsize(mb)/1024
        self.description = self.name +": %d "%len(self.mailconfigs)+ _("cuentas de correo")
        if not self.mailconfigs:
            raise Exception

    def get_configuration(self):
        """Devuelve la configuración de la aplicación de correo"""
        configs = []
        for key in self.option:
            r = self.user.search_key(key)
            for k, v in r.iteritems():
                if k.find('pst') > 0:
                    pst = self.user.check_path(k)
                    if os.path.exists(pst) and not pst in self.mailboxes:
                        self.mailboxes.append(pst)
            try:
                c = mailconfig(r)
            except:
                continue
            else:
                configs.append(c)
        return configs

    def convert_mailbox(self, mb):
        """Convierte los correos al formato Mailbox.
        
        Argumentos de entrada:
        mb -> fichero que contiene los correos de la aplicación
        
        """
        readpst = os.path.join(__DIR_PST2MBX__,'readpst')
        com = '%s -w %s -o %s' % (readpst, mb.replace(' ',"\ "), self.dest.path.replace(' ',"\ "))
        os.system(com)

        
class outlook_express(mailreader):
    
    def initialize(self):
        """Inicializa los valores específicos de la aplicación."""
        self.size = 0
        self.mailconfigs = []
        self.mailboxes = []

        self.name = _("Outlook Express")
        self.mailconfigs = self.get_configuration()
        for mb in self.mailboxes:
            self.size += mb.get_size()
        self.description = self.name +": %d "%len(self.mailconfigs)+ _("cuentas de correo")
        if not self.mailconfigs:
            raise Exception

    def get_configuration(self):
        """Devuelve la configuración de la aplicación de correo"""
        configs = []
        for key in self.option:
            r = self.user.search_key(key)
            
            mb = glob.glob(os.path.join(self.user.folders["Local AppData"].path, 'Identities','{*}','Microsoft','Outlook Express'))
            if mb:
                self.mailboxes.append(folder(mb[0]))
            try:
                c = mailconfig(r)
            except:
                continue
            else:
                configs.append(c)
        return configs

    def convert_mailbox(self, mb):
        """Convierte los correos al formato Mailbox.
        
        Argumentos de entrada:
        mb -> fichero que contiene los correos de la aplicación
        
        """
        readdbx = os.path.join(__DIR_DBX2MBX__,'readoe')
        output = self.dest.path
        com = '%s -i %s -o %s' % (readdbx, mb.path.replace(' ',"\ "), output.replace(' ','\ '))
        os.system(com)
        for e in os.listdir(output):
            if os.path.splitext(e)[-1] == '.dbx':
                shutil.move(os.path.join(output, e), os.path.join(output, e).replace('.dbx',''))

    def import_contacts(self):
        pass
        
    def import_calendar(self):
        pass
        

