# -*- coding: utf-8 -*-

import os
import re
from amigu import _
from amigu.util.folder import *
from amigu.apps.win.mail.base import *


class thunderbird(mailreader):
    
    def initialize(self):
        """Inicializa los valores específicos de la aplicación."""
        self.name = _("Mozilla Thunderbird")
        self.mailboxes = []
        self.size = 0
        self.mailconfigs = self.get_configuration()
        self.description = self.name +": %d "%len(self.mailconfigs)+ _("cuentas de correo")
        for mb in self.mailboxes:
            self.size += mb.get_size()
        
        if not self.mailconfigs:
            raise Exception

    def get_configuration(self):
        """Devuelve la configuración asociada a la aplicación"""
        prof = open(os.path.join(self.user.folders["AppData"].path, 'Thunderbird', 'profiles.ini'), 'rb')
        for l in prof.readlines():
            if l.startswith('Path'):
                perfil = l.split('=')[1].replace('\n','').replace('\r','')
        prof.close()
        prefs = os.path.join(self.user.folders["AppData"].path, 'Thunderbird', perfil, 'prefs.js')
        #prefs = self.user.get_THUNDERBIRD_prefs()
        p = open(prefs, 'r')
        content = p.readlines()
        p.close()
        id = 0
        c = {}
        configs = []
        for ac in self.option:
            pid = re.compile('.*'+ac+'\.identities\".+\"(?P<id>\w+)\".+')
            pserver = re.compile('.*'+ac+'\.server\".+\"(?P<server>\w+)\".+')
            
            for l in content:
                m = pid.match(l)
                if m:
                    id = m.group('id')
                    psmtp = re.compile('.*'+id+'\.smtpServer\".+\"(?P<smtp>\w+)\".+')
                else:
                    m = pserver.match(l)
                    if m:
                        server = m.group('server')
                    elif id:
                        m = psmtp.match(l)
                        if m:
                            try:
                                smtp = m.group('smtp')
                            except:
                                pass
            pid = re.compile('.*mail\.identity\.'+id+'\.(?P<key>.+)\".+\s(?P<value>(\".+\")|\d+)\).+')
            pserver = re.compile('.*mail\.server\.'+server+'\.(?P<key>.+)\".+\s(?P<value>(\".+\")|\w+)\).+')
            psmtp = re.compile('.*mail\.smtpserver\.'+smtp+'\.(?P<key>.+)\".+\s(?P<value>(\".+\")|\w+)\).+')
            for l in content:
                m = pid.match(l)
                if m:
                    c[m.group('key')]=m.group('value').replace('\"','')
                else:
                    m = pserver.match(l)
                    if m:
                        c[m.group('key')]=m.group('value').replace('\"','')
                    else:
                        m = psmtp.match(l)
                        if m:
                            c['smtp'+m.group('key')]=m.group('value').replace('\"','')
            configs.append(mailconfig(self.check_config(c)))
        return configs
        
    def check_config(self, c):
        """Comprueba que la configuración de la cuenta está completa
        
        Argumentos de entrada:
        c -> objeto de tipo Mailconfig
        
        """
        c[c['type'].upper()+' Server'] = c['hostname']
        c[c['type'].upper()+' User Name'] = c['userName']
        if 'port' in c.keys(): c[c['type'].upper()+' Port']=eval(c['port'])
        if 'socketType' in c.keys(): 
            c['Connection Type'] = str(c['socketType'])
            if c['socketType'] == '3':
                c[c['type'].upper()+' Use SSL'] = '1'
        c['Account Name'] = c['name']
        c['SMTP Display Name'] = c['fullName']
        c['SMTP Email Address'] = c['smtpusername']
        c['SMTP Server'] = c['smtphostname']
        if 'smtpport' in c.keys(): c['SMTP Port']=eval(c['smtpport'])
        if 'smtptry_ssl' in c.keys(): c['SMTP Use SSL'] = '1'
        c['Email Address'] = c['useremail']
        if 'leave_on_server' in c.keys():
            c['Leave Mail On Server'] = '1'
        if 'empty_trash_on_exit' in c.keys():
            c['Remove When Deleted'] = '1'
        
        #print c
        #print c['directory-rel'].replace("[ProfD]",os.path.dirname(self.user.get_THUNDERBIRD_prefs())+'/')
        self.mailboxes.append(folder(c['directory-rel'].replace("[ProfD]",os.path.dirname(self.user.get_THUNDERBIRD_prefs())+'/')))
        return c
        
    def import_mails(self):
        """Convierte los correos al formato Mailbox."""
        self.dest = folder(os.path.join(os.path.expanduser('~'),'.evolution','mail','local', _("Correo de ")+ self.name +'.sbd'))
        for mb in self.mailboxes:
            mb.copy(self.dest, exclude=['.dat','.msf'])
        

    def do(self):
        """Ejecuta el proceso de migración basado en importar las cuentas
        de correo, los correos almacenados.
        
        Devuelve 1 en caso que el proceso finalice sin errores.
        
        """
        self.update_progress(10.0)
        if not os.path.exists(os.path.join(os.path.expanduser('~'),'.mozilla-thunderbird')):
            self.pulse_start()
            self.direct_import()
            self.pulse_stop()
        #mailreader.do(self)
        self.update_progress(50.0)
        if not self.abort:
            self.import_accounts()
            self.update_progress(70.0)
        if not self.abort:
            self.pulse_start()
            self.import_mails()
            self.pulse_stop()
            self.update_progress(90.0)
        return 1

            
    def direct_import(self):
        """Importa directamente la configuración en Thunderbird"""
        dest = folder(os.path.join(os.path.expanduser('~'), '.mozilla-thunderbird'))
        origen = folder(os.path.join(self.user.folders["AppData"].path, 'Thunderbird'))
        origen.copy(dest)

########################################################################
