# -*- coding: utf-8 -*-

import os
import re
import random
import time
import shutil
import commands
import glob
from amigu import _
import binascii
from xml.dom import minidom
from amigu.util.folder import *
from amigu.apps.base import application


class mailconfig:
    """Clase para el manejo de configuraciones de correo.
    Visit http://msdn2.microsoft.com/en-us/library/ms715237.aspx for more information about the values"""

    def __init__(self, config):
        """Constructor de la clase.
        
        Argumentos de entrada:
        config -- puede ser un diccionario que contenga información sobre
        una cuenta de correo o un archivo xml de Windows Live Mail
        
        """
        if isinstance(config, dict):
            self.c = config
        elif os.path.exists(config):
            self.c = self.readconfig_wm(config)
        else:
            raise Exception
        if not self.get_server():
            raise Exception
        #print self.c
        

    def get_type(self):
        """Devuelve el tipo de cuenta de correo"""
        if 'IMAP Server' in self.c.keys():
            t = "imap"
        elif 'POP3 Server' in self.c.keys():
            t = "pop3"
        elif 'HTTPMail Server' in self.c.keys():
            t = "HTTPMail"
        else:
            t = "Unknown"
        return t

    def get_user_name(self):
        """Devuelve el nombre del usuario de la cuenta"""
        if self.get_type() == "imap":
            if 'IMAP User Name' in self.c.keys():
                r = self.c['IMAP User Name']
            elif 'IMAP User' in self.c.keys():
                r = self.c['IMAP User']
        elif self.get_type() == "pop3":
            if 'POP3 User Name' in self.c.keys():
                r = self.c['POP3 User Name']
            elif 'POP3 User' in self.c.keys():
                r = self.c['POP3 User']
        elif self.get_type() == "HTTPmail":
            r = self.c['HTTPMail User Name']
        else:
            r = None
        return r

    def get_account_name(self):
        """Devuelve el nombre de la cuenta de correo"""
        return self.c['Account Name']

    def get_connection_type(self):
        """Devuelve el tipo de conexión con el servidor"""
        return self.c['Connection Type']

    def get_server(self):
        """Devuelve el servidor de correo entrante"""
        if self.get_type() == "imap":
            r = self.c['IMAP Server']
        elif self.get_type() == "pop3":
            r = self.c['POP3 Server']
        elif self.get_type() == "HTTPMail":
            r = self.c['HTTPMail Server']
        else:
            r = None
        return r

    def use_SSL(self):
        """Devuelve si la conexión es segura"""
        if self.get_type() == "imap" and 'IMAP Secure Connection' in self.c.keys():
            r = hex2dec(self.c['IMAP Secure Connection'])
        elif self.get_type() == "imap" and 'IMAP Use SSL' in self.c.keys():
            r = hex2dec(self.c['IMAP Use SSL'])
        elif self.get_type() == "pop3" and 'POP3 Secure Connection' in self.c.keys():
            r = hex2dec(self.c['POP3 Secure Connection'])
        elif self.get_type() == "pop3" and 'POP3 Use SSL' in self.c.keys():
            r = hex2dec(self.c['POP3 Use SSL'])
        else:
            r = None
        return r

    def get_port(self):
        """Devuelve el puerto del servidor de correo entrante"""
        if self.get_type() == "imap":
            if 'IMAP Port' in self.c.keys():
                r = hex2dec(self.c['IMAP Port'])
            elif self.use_SSL():
                r = 993
            else:
                r = 143
        elif self.get_type() == "pop3":
            if 'POP3 Port' in self.c.keys():
                r = hex2dec(self.c['POP3 Port'])
            elif self.use_SSL():
                r = 995
            else:
                r = 110
        else:
            r = None
        return r

    def get_timeout(self):
        """Devuelve el tiempo de espera"""
        try:
            if self.get_type() == "imap":
                r = self.c['IMAP Timeout']
            elif self.get_type() == "pop3":
                r = self.c['POP3 Timeout']
        except:
            r = 60
        return r

    def remove_expired(self):
        """Devuelve si se eliminan los correos con el paso del tiempo"""
        if 'Remove When Expired' in self.c.keys():
            return hex2dec(self.c['Remove When Expired']) and 'true' or 'false'

    def remove_deleted(self):
        """Devuelve si se eliminan los correos del servidor al ser borrados"""
        if 'Remove When Deleted' in self.c.keys():
            return hex2dec(self.c['Remove When Deleted']) and 'true' or 'false'

    def get_SMTP_display_name(self):
        """Devuelve el nombre del servidor de correo saliente"""
        if 'SMTP Display Name' in self.c.keys():
            return self.c['SMTP Display Name']
        elif 'Display Name' in self.c.keys():
            return self.c['Display Name']
        else:
            return ""

    def get_SMTP_port(self):
        """Devuelve el puerto del servidor de correo saliente"""
        if 'SMTP Port' in self.c.keys():
            return hex2dec(self.c['SMTP Port'])
        else:
            return 25

    def get_SMTP_server(self):
        """Devuelve el servidor de correo saliente"""
        return self.c['SMTP Server']

    def get_SMTP_email_address(self):
        """Devuelve la direccion de correo saliente"""
        if 'SMTP Email Address' in self.c.keys():
            return self.c['SMTP Email Address']
        elif 'Email' in self.c.keys():
            return self.c['Email']


    def get_SMTP_timeout(self):
        """Devuelve el tiempo de espera del servidor de correo saliente"""
        if 'SMTP Timeout' in self.c.keys():
            return hex2dec(self.c['SMTP Timeout'])
        else: 
            return 60

    def use_SMTP_SSL(self):
        """Devuelve si la conexión con el servidor de correo saliente es segura"""
        if 'SMTP Secure Connection' in self.c.keys():
            return hex2dec(self.c['SMTP Secure Connection'])
        elif 'SMTP Use SSL' in self.c.keys():
            return hex2dec(self.c['SMTP Use SSL'])

    def leave_mail(self):
        """Devuelve si los mensajes deben conservarse en el servidor"""
        r = 'false'
        if 'Leave Mail On Server' in self.c.keys():
            r = hex2dec(self.c['Leave Mail On Server']) and 'true' or 'false'
        return r
        
    def readconfig_wm(self, config):
        """Lee la configuación de correo de Windows Mail
        
        Argumentos de entrada:
        config -- archivo XML de configuración de Windows Mail
        """
        c = {}
        xmldoc = minidom.parse(config)
        for node in xmldoc.firstChild.childNodes:
            if node.nodeType == node.ELEMENT_NODE:
                c[node.tagName.replace('_',' ')] = node.firstChild.data
        return c
        
# end class mail

############################################################################

class mailreader(application):
    """Clase para el manejo de aplicaciones de correo"""
    
    def initialize(self):
        """Inicializa los valores específicos de la aplicación.
        Este método debe ser apliado en las clases hijas
        """
        self.name = _("Lector de correo")
        self.size = 0
        self.mailconfigs = []
        self.mailboxes = []
        self.dest = folder(os.path.join(os.path.expanduser('~'),'.evolution','mail','local', _("Correo de ")+ self.name +'.sbd'))
        self.description = self.name +": %d"%len(self.mailconfigs)+ _("cuentas de correo")
        
    def get_configuration(self):
        """Método abstracto para obtener la configuración de la aplicación
        de correo
        
        """
        pass

    def do(self):
        """Ejecuta el proceso de migración basado en importar las cuentas
        de correo, los correos almacenados, los contactos y el calendario
        en caso de que la apliación disponga de él.
        
        Devuelve 1 en caso que el proceso finalice sin errores.
        
        """
        self.update_progress(5.0)
        if not self.abort:
            self.import_accounts()
        if not self.abort:
            self.pulse_start()
            self.import_mails()
            self.pulse_stop()
            self.update_progress(80.0)
        if not self.abort:
            self.import_contacts()
            self.update_progress(90.0)
        if not self.abort:
            self.import_calendar()
        return 1

    def import_mails(self):
        """Importa los correos almacenados"""
        self.dest = folder(os.path.join(os.path.expanduser('~'),'.evolution','mail','local', _("Correo de ")+ self.name +'.sbd'))
        for mb in self.mailboxes:
            self.convert_mailbox(mb)
            self.update_progress(delta=30.0/len(self.mailconfigs))
            
    def convert_mailbox(self, mb):
        """Método abstracto para convertir los correos de la apliación 
        al formato mailbox de Evolution
        
        Argumentos de entrada:
        mb -- carpeta o fichero que contengan correos
        """
        
        pass

    def import_accounts(self):
        """Configura las cuentas de correo de la aplicación para que 
        puedan ser usadas en Evolution y Thunderbird
        
        """
        for a in self.mailconfigs:
            try:
                self.config_EVOLUTION(a)
            except: 
                print a
            try:
                self.config_THUNDERBIRD(a)
            except:
                print a
            self.update_progress(delta=45.0/len(self.mailboxes))
        
    def import_calendar(self):
        """Importa el calendario de la aplicación"""
        self.config_EVOLUTION_calendar()
        
    def import_contacts(self):
        """Importa la libreta de contactos de la aplicación"""
        self.config_EVOLUTION_addressbook()

    def config_EVOLUTION(self, a):
        """Configura la cuenta dada en Evolution
        
        Argumentos de entrada:
        a -- objeto de tipo Mailconfig
        
        """
        #a = self.mailconfig
        ssl = a.use_SSL() and 'always' or 'never'
        smtpssl = a.use_SMTP_SSL() and 'always' or 'never'
        server_type = a.get_type()
        if server_type == 'pop3':
            m = 'pop'
            draft = "mbox:" + os.path.expanduser('~') + "/.evolution/mail/local#Drafts"
            sent = "mbox:" + os.path.expanduser('~') + "/.evolution/mail/local#Sent"
            command = ''
        elif server_type == 'imap':
            m = 'imap'
            draft, sent = '', ''
            command = ";check_all;command=ssh%20-C%20-l%20%25u%20%25h%20exec%20/usr/sbin/imapd"
        elif server_type == "HTTPMail" or server_type == "Unknown":
            warning("Account type %s won't be added" % server_type)
            return 0
        # get previous accounts
        try:
            l = os.popen("gconftool --get /apps/evolution/mail/accounts")
            laccounts = str(l.read())
            l.close()
            if not laccounts:
                laccounts = "[]\n"
            elif laccounts.find(a.get_SMTP_email_address()) > 0:
                return 1
        except:
            error ("Evolution configuration is not readable")
        else:
            # generate new xml list
            e = "<?xml version=\"1.0\"?>\n" + \
            "<account name=\"%s\" uid=\"%s\" enabled=\"true\">" % (a.get_account_name(), str(time.time())) + \
            "<identity>" + \
            "<name>%s</name>" % a.get_SMTP_display_name() + \
            "<addr-spec>%s</addr-spec><signature uid=\"\"/>" % a.get_SMTP_email_address() + \
            "</identity>" + \
            "<source save-passwd=\"false\" keep-on-server=\"%s\" auto-check=\"true\" auto-check-timeout=\"10\">" % a.leave_mail() + \
            "<url>%s://%s@%s:%d/%s;use_ssl=%s</url>" % (m, a.get_user_name().replace('@','%40'), a.get_server(), a.get_port(), command, ssl) + \
            "</source>" + \
            "<transport save-passwd=\"false\">" + \
            "<url>smtp://%s;auth=PLAIN@%s:%d/;use_ssl=%s</url>" % (a.get_user_name().replace('@','%40'), a.get_SMTP_server(), a.get_SMTP_port(), smtpssl) + \
            "</transport>" + \
            "<drafts-folder>%s</drafts-folder>" % draft + \
            "<sent-folder>%s</sent-folder>" % sent + \
            "<auto-cc always=\"false\"><recipients></recipients></auto-cc><auto-bcc always=\"false\"><recipients></recipients></auto-bcc><receipt-policy policy=\"never\"/>" + \
            "<pgp encrypt-to-self=\"false\" always-trust=\"false\" always-sign=\"false\" no-imip-sign=\"false\"/><smime sign-default=\"false\" encrypt-default=\"false\" encrypt-to-self=\"false\"/>" + \
            "</account>\n"
            # concatenate elemennt to the list
            #print e
            if laccounts == "[]\n":
                #create list
                laccounts = "[" + e +"]"
            else:
                #add to list
                laccounts = laccounts[:-2] + ',' + e + "]"
            # set the modified list
            try:
                os.system("gconftool --set /apps/evolution/mail/accounts --type list --list-type string \"" + laccounts.replace("\"", "\\\"") +"\"")
                progress("Account %s added successfully" % a.get_account_name())
            except:
                self.errors += "Evolution configuration is not writable"
    
    def config_EVOLUTION_calendar(self):
        """Convierte e integra el calendario en Evolution"""
        vcal = os.path.join(self.dest.path, _("Calendario"))
        if not os.path.exists(vcal):
            vcal = commands.getoutput("rgrep -l VEVENT %s" % self.dest.path.replace(' ', '\ '))
        if not vcal or not os.path.exists(vcal):
            return 0
        old = None
        dates = []
        evo_cal = os.path.join(os.path.expanduser('~'),'.evolution','calendar','local','system','calendar.ics')
        folder(os.path.dirname(evo_cal))
        if os.path.exists(evo_cal):
            old = backup(evo_cal)
            if old:
                new_cal = open(evo_cal, "w")
                old_cal = open(old, 'r')
                for l in old_cal.readlines():
                    if l.find('END:VCALENDAR') == -1:
                        new_cal.write(l)
                    if l.find('BEGIN:VEVENT') != -1:
                        dt, sum = None, None
                    elif l.find('END:VEVENT') != -1:
                        if dt and sum:
                            dates.append(dt+sum)
                    elif l.find('DTSTART') != -1:
                        dt = l.replace('DTSTART:', '')
                    elif l.find('SUMMARY') != -1:
                        sum = l.replace('SUMMARY:', '')
                old_cal.close()
        orig = open(vcal,"r")
        events = False
        if not old:
            new_cal = open(evo_cal, "w")
            new_cal.write('BEGIN:VCALENDAR\n')
            new_cal.write('CALSCALE:GREGORIAN\n')
            new_cal.write('VERSION:2.0\n')
        buffer = ''
        for l in orig.readlines():
            buffer += l
            if l.find('BEGIN:VEVENT') != -1:
                dt, sum = None, None
                buffer = l
            elif l.find('END:VEVENT') != -1:
                if dt and sum and not dt+sum in dates:
                    new_cal.write(buffer)
            elif l.find('DTSTART') != -1:
                dt = l.replace('DTSTART:', '')
            elif l.find('SUMMARY') != -1:
                sum = l.replace('SUMMARY:', '')
        new_cal.write('END:VCALENDAR\n')
        orig.close()
        os.remove(vcal)
                
    def config_EVOLUTION_addressbook(self):
        """Convierte e integra los contactos en la libreta de direcciones
        de Evolution
        
        """
        vcard = os.path.join(self.dest.path, _("Contactos"))
        if not os.path.exists(vcard):
            vcard = commands.getoutput("rgrep -l VCARD %s" % self.dest.path.replace(' ', '\ '))
        if not vcard or not os.path.exists(vcard):
            return 0
        import bsddb
        adb=os.path.join(os.path.expanduser('~'),'.evolution','addressbook','local','system','addressbook.db')
        folder(os.path.dirname(adb))
        db = bsddb.hashopen(adb,'w')
        if not 'PAS-DB-VERSION\x00' in db.keys():
            db['PAS-DB-VERSION\x00'] = '0.2\x00'
        contacts = open(vcard, 'r')
        while 1:
            l = contacts.readline()
            if not l:
                break
            if l.find('BEGIN:VCARD') != -1:
                randomid = 'pas-id-' + str(random.random())[2:]
                db[randomid+'\x00'] = 'BEGIN:VCARD\r\nUID:' + randomid + '\r\n'
                while 1:
                    v = contacts.readline()
                    if v.find('END:VCARD') != -1:
                        db[randomid+'\x00'] += 'END:VCARD\x00'
                        break
                    else:
                        db[randomid+'\x00'] += v.replace('PERSONAL','HOME').replace('\n', '\r\n')
        db.sync()
        db.close()
        os.remove(vcard)
    
    def config_THUNDERBIRD(self, a):
        """Configura la cuenta dada en Mozilla Thunderbird
        
        Argumentos de entrada:
        a -- objeto de tipo Mailconfig
        
        """
        th = mozillathunderbird()
        try:
            th.config_account(a)
        except:
            pass

    
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


########################################################################

def hex2dec(hexa):
    """Convierte valores hexadecimales del registro en valores enteros"""
    if not isinstance(hexa, int):
        hexa = hexa.replace('dword:','0x')
        return int(hexa, 16)
    else:
        return int(hexa)


def hex2str(hexa):
    """Convierte valores hexadecimales del registro en cadenas de caracteres"""
    hexa = hexa.replace('hex:','')
    hexa = hexa.replace(',00','')
    hexa = hexa.replace(',','')
    hexa = hexa.replace(' ','')
    return binascii.unhexlify(hexa)
      
def eml2mbox(emlpath, mbxpath):
    """Convierte archivos .eml a formato mailbox
    
    Argumentos de entrada:
    emlpath -> ruta donde residen los archivos eml
    mbxpath -> ruta de destino de los archivos mailbox
    
    """
    i = 0
    pattern = re.compile('(?P<date>Date:)\s+(?P<day>\w{3})\s+(?P<number>\d{1,2})\s+(?P<month>\w{3})\s+(?P<year>\d{4})\s+(?P<hour>[\d:]{5,8}).+')
    try:
        d = open(mbxpath, 'w')
    except: 
        return 0
    for e in os.listdir(emlpath):
        if os.path.isdir(os.path.join(emlpath, e)):
            new = folder(mbxpath+'.sbd')
            eml2mbox(os.path.join(emlpath, e), os.path.join(new.path, e))
        elif os.path.splitext(e)[-1] == '.eml':
            try:
                m = open(os.path.join(emlpath, e),'r')
                content = m.readlines()
                m.close()
            except:
                continue
            else:
                for l in content:
                    r = pattern.match(l.replace(',',''))
                    if r:
                        d.write("From - %s %s  %s %s %s\n" % (r.group('day'),
                                                            r.group('month'),
                                                            r.group('number'),
                                                            r.group('hour'),
                                                            r.group('year')))
                        for l in content:
                            d.write(l.replace('\r', ''))
                        d.write('\n\n')
                        i += 1
                        break
    d.close()
    print "Carpeta %s: %d archivos procesados" % (os.path.basename(emlpath), i)

       

class mozillathunderbird:
    """Clase para el gestro de correo Thunderbird"""

    def __init__(self):
        """Constructor de la clase"""
        thunderbird = folder(os.path.join(os.path.expanduser('~'),'.mozilla-thunderbird'))
        self.profile = self.get_thunderbird_profile(thunderbird.path)
        self.errors = []
        if not self.profile and thunderbird.path:
            try:
                prof = open(os.path.join(thunderbird.path,'profiles.ini'), 'w')
                prof.write("[General]\n")
                prof.write("StartWithLastProfile=1\n\n")
                prof.write("[Profile0]\n")
                prof.write("Name=migrated\n")
                prof.write("IsRelative=1\n")
                prof.write("Path=m1gra73d.default\n")
                prof.close()
                self.profile = thunderbird.create_subfolder("m1gra73d.default")
            except:
                self.error("Unable to create Mozilla Thunderbird profile")
                return 0
        self.config_file  = os.path.join(self.get_thunderbird_profile(thunderbird.path), 'prefs.js')

    def error (self, e):
        """Almacena los errores en tiempo de ejecución"""
        self.errors.append(e)

    def get_thunderbird_profile(self, thunderbird = '~/.mozilla-thunderbird'):
        """Devuelve el perfil actual de Thunderbird. En caso de no existir crea uno nuevo"""
        profiles_ini = os.path.join(thunderbird,'profiles.ini')
        if os.path.exists(profiles_ini):
            try:
                prof = open(profiles_ini, 'r')
            except:
                self.error ('Unable to read Thunderbird profiles')
            else:
                relative = 0
                for e in prof.read().split('\n'):
                    if re.search("IsRelative=1",e):
                        relative = 1
                    if re.search("Path",e):
                        profile = e.split('=')[1]
                prof.close()
                if relative:
                    path_profile = os.path.join(thunderbird, profile)
                else:
                    path_profile = profile
                if path_profile[-1]=='\r':
                    return path_profile[:-1]
                else:
                    return path_profile

    def config_account(self, account):
        """Configura la cuenta leida del registro"""
        n = str(random.randint(100,999))
        #check if the mail config is valid
        a = account
        server_type = a.get_type()
        if server_type == "HTTPMail" or server_type == "Unknown":
            warning("Acoount type %s won't be added" % server_type)
            return 0
        elif os.path.exists(self.config_file):
            bak = backup (self.config_file)
            try:
                p = open(self.config_file, 'w')
                b = open(bak, 'r')
            except:
                p.close()
                b.close()
                self.error('Unable to modify %s' % self.config_file)
                return 0
            else:
                added_account, added_smtpserver = False, False
                for l in b.readlines():
                    if re.search('mail.accountmanager.accounts',l): #add the new account
                        l = l[:-4] + ',account' + n + l[-4:]
                        added_account = True
                    if re.search('mail.smtpservers', l): #add the new smtp
                        l = l[:-4] + ',smtp' + n + l[-4:]
                        added_smtpserver = True
                    p.write(l)
                if not added_account:
                    p.write("user_pref(\"mail.accountmanager.accounts\", \"account%s\");\n" % n)
                if not added_smtpserver:
                    p.write("user_pref(\"mail.smtpservers\", \"smtp%s\");\n" % n)
                b.close()
        else:
            try:
                p = open(self.config_file, 'w')
            except:
                self.error('Unable to create %s' % self.config_file)
                return 0
            else:
                p.write("# Mozilla User Preferences\n\n")
                p.write("user_pref(\"mail.accountmanager.accounts\", \"account%s\");\n" % n)
                p.write("user_pref(\"mail.smtpservers\", \"smtp%s\");\n" % n)
                p.write("user_pref(\"mail.root.none\", \"%s/Mail\");\n" % self.profile)
                p.write("user_pref(\"mail.root.none-rel\", \"[ProfD]Mail\");\n")
                if server_type == "imap":# only for IMAP accounts
                    p.write("user_pref(\"mail.root.imap\", \"%s/ImapMail\");\n" % self.profile)
                    p.write("user_pref(\"mail.root.imap-rel\", \"[ProfD] ImapMail\");\n")
                    #p.write("user_pref(\"mail.server.server%s.directory\", \"%s/ImapMail/%s\");\n"% (n, self.profile, a.get_server()))
                elif server_type == "pop3": # only for POP3 accounts
                    p.write("user_pref(\"mail.root.pop3\", \"%s/Mail\");\n" % self.profile)
                    p.write("user_pref(\"mail.root.pop3-rel\", \"[ProfD]Mail\");\n")
                    #p.write("user_pref(\"mail.server.server%s.leave_on_server\", %s);\n" % (n, a.leave_mail()))
                    #p.write("user_pref(\"mail.server.server%s.directory\", \"%s/Mail/%s\");\n" % (n, self.profile, a.get_server()))
                    #p.write ("user_pref(\"mail.server.server%s.delete_by_age_from_server\", %s);\n" % (n, a.remove_deleted()))
                    #p.write("user_pref(\"mail.server.server%s.delete_mail_left_on_server\", %s);\n" % (n, a.remove_expired()))
        # for both types
        p.write("user_pref(\"mail.account.account%s.identities\", \"id%s\");\n" % (n, n))
        p.write("user_pref(\"mail.account.account%s.server\", \"server%s\");\n" % (n, n))
        # identity configuration
        p.write("user_pref(\"mail.identity.id%s.fullName\", \"%s\");\n" % (n, a.get_SMTP_display_name()))
        p.write("user_pref(\"mail.identity.id%s.useremail\", \"%s\");\n" % (n, a.get_SMTP_email_address()))
        p.write("user_pref(\"mail.identity.id%s.smtpServer\", \"smtp%s\");\n" % (n, n))
        p.write("user_pref(\"mail.identity.id%s.valid\", true);\n" % n )
        # server configuration
        p.write("user_pref(\"mail.server.server%s.login_at_startup\", true);\n" % n )
        p.write("user_pref(\"mail.server.server%s.name\", \"%s\");\n" % (n, a.get_account_name()))
        p.write("user_pref(\"mail.server.server%s.hostname\", \"%s\");\n"% (n, a.get_server()))
        p.write("user_pref(\"mail.server.server%s.type\", \"%s\");\n" % (n, server_type))
        p.write("user_pref(\"mail.server.server%s.userName\", \"%s\");\n" % (n, a.get_user_name()))
        if a.use_SSL():
            p.write("user_pref(\"mail.server.server%s.socketType\", 3);\n"% n)
            p.write("user_pref(\"mail.server.server%s.port\", %d);\n" % (n, a.get_port()))
        # SMTP configuration
        p.write("user_pref(\"mail.smtpserver.smtp%s.hostname\", \"%s\");\n" % (n, a.get_SMTP_server()))
        p.write("user_pref(\"mail.smtpserver.smtp%s.username\", \"%s\");\n" % (n, a.get_user_name()))
        if a.use_SMTP_SSL():
            p.write("user_pref(\"mail.smtpserver.smtp%s.try_ssl\", 3);\n" % n)
            p.write("user_pref(\"mail.smtpserver.smtp%s.port\", %d);\n" % (n, a.get_SMTP_port()))
        p.close()

    def import_windows_settings(self, AppData):
        """Importa la configuración de Thunderbird en Windows. SOBREESCRIBE LA INFORMACIÓN EXISTENTE"""
        winprofile = folder(self.get_thunderbird_profile(os.path.join(AppData, 'Thunderbird')))
        if winprofile:
            # copy all files from the winprofile
            winprofile.copy(self.profile)
            # modify prefs.js
            try:
                wp = open (os.path.join(winprofile.path, 'prefs.js'), 'r')
                p = open (self.config_file, 'w')
                for l in wp.readlines():
                    if l.find(':\\') == -1:
                        p.write(l)
            except:
                self.error("Failed to copy Thunderbird profile")
            wp.close()
            p.close()
        return 0

    def is_installed_on_Windows(self, AppData):
        """Devuelve si Firefox está instalado en Windows"""
        return self.get_thunderbird_profile(os.path.join(AppData.path, 'Thunderbird'))

    def generate_impab(self, l):
        """Inserta el contacto en la libreta de direcciones de Thunderbird"""
        try:
            backup(os.path.join(self.profile,'impab.mab'))
            f = open(os.path.join(self.profile,'impab.mab'),'w')
        except:
            self.error( "Fallo al crear contactos de Thunderbird")
        else:
            f.write("// <!-- <mdb:mork:z v=\"1.4\"/> -->\n< <(a=c)> // (f=iso-8859-1)\n  (B8=Custom3)(B9=Custom4)(BA=Notes)(BB=LastModifiedDate)(BC=RecordKey)\n  (BD=AddrCharSet)(BE=LastRecordKey)(BF=ns:addrbk:db:table:kind:pab)\n  (C0=ListName)(C1=ListNickName)(C2=ListDescription)\n  (C3=ListTotalAddresses)(C4=LowercaseListName)\n  (C5=ns:addrbk:db:table:kind:deleted)\n  (80=ns:addrbk:db:row:scope:card:all)\n  (81=ns:addrbk:db:row:scope:list:all)\n  (82=ns:addrbk:db:row:scope:data:all)(83=FirstName)(84=LastName)\n  (85=PhoneticFirstName)(86=PhoneticLastName)(87=DisplayName)\n  (88=NickName)(89=PrimaryEmail)(8A=LowercasePrimaryEmail)\n  (8B=SecondEmail)(8C=DefaultEmail)(8D=CardType)(8E=PreferMailFormat)\n  (8F=PopularityIndex)(90=WorkPhone)(91=HomePhone)(92=FaxNumber)\n  (93=PagerNumber)(94=CellularNumber)(95=WorkPhoneType)(96=HomePhoneType)\n  (97=FaxNumberType)(98=PagerNumberType)(99=CellularNumberType)\n  (9A=HomeAddress)(9B=HomeAddress2)(9C=HomeCity)(9D=HomeState)\n  (9E=HomeZipCode)(9F=HomeCountry)(A0=WorkAddress)(A1=WorkAddress2)\n  (A2=WorkCity)(A3=WorkState)(A4=WorkZipCode)(A5=WorkCountry)\n  (A6=JobTitle)(A7=Department)(A8=Company)(A9=_AimScreenName)\n  (AA=AnniversaryYear)(AB=AnniversaryMonth)(AC=AnniversaryDay)\n  (AD=SpouseName)(AE=FamilyName)(AF=DefaultAddress)(B0=Category)\n  (B1=WebPage1)(B2=WebPage2)(B3=BirthYear)(B4=BirthMonth)(B5=BirthDay)\n  (B6=Custom1)(B7=Custom2)>\n\n")

            f.write("<(80=0)>\n{1:^80 {(k^BF:c)(s=9)}\n  [1:^82(^BE=0)]}\n\n")

            f.write("@$${1{@\n\n<")
            i, j = 1, 1
            for a in l:
                f.write("(%d=%d)(%d=%s)"%(80 + 2*(len(l) - j + 1) , len(l) - j + 1 , 80 + i, a ))
                i += 2
                j += 1
            f.write(">\n{-1:^80 {(k^BF:c)(s=9)} \n  [1:^82(^BE=%d)]"%(j-1))
            i, j = 1, 1
            for a in l:
                f.write("\n  [-%d(^89^%d)(^8A^%d)(^BC=%d)]"%(j, 80+i, 80+i, j))
                i += 2
                j += 1
            f.write("}\n@$$}1}@")
            f.close()
            self.add_impab()
            return 1

    def add_impab(self):
        """Añade la libreta de direcciones importada a Thunderbird"""
        p = None
        if os.path.exists(self.config_file):
            bak = backup (self.config_file)
            try:
                p = open(self.config_file, 'a')
            except:
                p.close()
                self.error('Unable to modify %s' % self.config_file)
                return 0

        else:
            try:
                p = open(self.config_file, 'w')
            except:
                self.error('Unable to create %s' % self.config_file)
                return 0
            else:
                p.write("# Mozilla User Preferences\n\n")
                p.write("user_pref(\"mail.accountmanager.accounts\", \"\");\n")
                p.write("user_pref(\"mail.smtpservers\", \"\");\n")
                p.write("user_pref(\"mail.root.none\", \"%s/Mail\");\n"%self.profile)
                p.write("user_pref(\"mail.root.none-rel\", \"[ProfD]Mail\");\n")
        if p:
            p.write("user_pref(\"ldap_2.servers.contactosOutlook.description\", \"contactos_Outlook\");\n")
            p.write("user_pref(\"ldap_2.servers.contactosOutlook.dirType\", 2);\n")
            p.write("user_pref(\"ldap_2.servers.contactosOutlook.filename\", \"impab.mab\");\n")
            p.write("user_pref(\"ldap_2.servers.contactosOutlook.isOffline\", false);\n")
            p.write("user_pref(\"ldap_2.servers.contactosOutlook.protocolVersion\", \"2\");\n")
            p.write("user_pref(\"ldap_2.servers.contactosOutlook.replication.lastChangeNumber\", 0);\n")
            p.write("user_pref(\"ldap_2.servers.contactosOutlook.position\", 1);\n")
            p.close()

# end class thunderbird

############################################################################


class kmail:
    """Clase para el gestor de correo Kmail integrado en Kontact"""

    def __init__(self):
        """Constructor de la clase"""
        self.errors = []
        self.config_file = os.path.join(os.path.expanduser('~'),'.kde', 'share', 'config', 'kmailrc')
        if os.path.exists(self.config_file):
            try:
                b = open (self.config_file, 'r')
                for l in b.readlines():
                    if re.search('accounts=',l): # increase account
                        self.iaccount = int(l[9:]) + 1
                    if re.search('transports=', l): # increase smtp
                        self.itransport = int(l[11:]) + 1
                b.close()
            except:
                b.close()
                self.error("Unable to read %s" % self.config_file)
        else:
            self.iaccount, self.itransport = 0, 0
            try:
                b = open (self.config_file, 'r')
                b.write("[Composer]\n")
                b.write("default-transport=%s\n" % a.get_SMTP_display_name())
                b.write("\n[General]\n")
                b.write("accounts=1\n")
                b.write("checkmail-startup=true\n")
                b.write("first-start=false\n")
                b.write("transports=1\n")
                b.close()
            except:
                b.close()
                self.error("Unable to create %s" % self.config_file)
        self.identities = os.path.join(os.path.expanduser('~'), '.kde', 'share', 'config', 'emailidentities')
        self.maxid = 0
        if os.path.exists(self.identities):# configuration file already exists
            try:
                b = open(self.identities, 'r')
                for l in b.readlines():
                    if re.search('Identity #',l): # increase account
                        maxid = (maxid <= int(l[11:-2])) and int(l[11:-2]) + 1 or maxid
                b.close()
            except:
                b.close()
                self.error('Unable to access %s' % self.identities)


    def error(self, e):
        """Almacena los errores en tiempo de ejecución"""
        self.errors.append(e)

    def config_account(self, account):
        """Configura la cuenta dada en Kmail"""
        #check if the mail config is valid
        a = mailconfig(account)
        server_type = a.get_type()
        if server_type == "HTTPMail" or server_type == "Unknown":
            warning("Acoount type %s won't be added" % server_type)
            return 0
        self.itransport = self.itransport + 1
        self.iaccount = self.iaccount + 1
        bak = backup (self.config_file)
        if bak:
            try:
                p = open(self.config_file, 'w')
                # config account
                p.write("\n[Account %i]\n" % self.iaccount)
                p.write("Folder=inbox\n")
                p.write("Id=%s\n" % str(time.time()))
                p.write("Name=%s\n" % a.get_account_name())
                if server_type=='imap':
                    p.write("auth=*\n")
                    p.write("Type=%s\n" % server_type)
                if server_type=='pop3':
                    p.write("auth=USER\n")
                    p.write("Type=pop\n")
                p.write("host=%s\n" % a.get_server())
                p.write("leave-on-server=%s\n" % a.leave_mail())
                p.write("login=%s\n" % a.get_user_name())
                p.write("port=%s\n" % a.get_port())
                p.write("use-ssl=%s\n" % a.use_SSL())
                p.write("use-tls=false\n")
                #config transport (SMTP)
                p.write("\n[Transport %i]\n" % self.itransport)
                p.write("auth=false\n")
                p.write("authtype=PLAIN\n")
                p.write("encryption=SSL\n")
                p.write("host=%s\n" % a.get_SMTP_server())
                p.write("id=%s\n" % str(time.time()))
                p.write("name=%s\n" % a.get_SMTP_server())
                p.write("port=%s\n" % a.get_SMTP_port())
                p.write("type=smtp\n")
                p.write("user=\n")
                p.close()
                #config identity
                self.add_identity(account)
            except:
                p.close()
                self.itransport = self.itransport - 1
                self.iaccount = self.iaccount - 1
                self.error('Failed to modify %s' % self.config_file)
                return 0

    def add_identity(self, a):
        """Añade la identidad"""
        bak = backup(self.identities)
        if bak:
            try:
                p = open(self.identities, 'a')
                p.write("\n[Identity #%i]\n" % self.maxid)
                p.write("Email Address=%s\n" % a.get_SMTP_email_address())
                p.write("Name=%s\n" % a.get_SMTP_display_name())
                p.write("Transport=%s\n" % a.get_SMTP_server())
                p.write("uoid=%s\n" % str(time.time()*100))
                p.close()
            except:
                p.close()
                self.error("Failed to add identity")
                restore_backup(bak)

# end class kmail

############################################################################


if __name__ == "__main__":
    from amigu.computer.info import pc
    from amigu.computer.users.mswin import winuser
    com = pc()
    com.check_all_partitions()
    print "Analizando usuarios de Windows"
    for user_path, ops in com.get_win_users().iteritems():
        u = winuser(user_path, com, ops)
        try:
            print u.get_OUTLOOK_accounts()
        except:
            pass
        u.clean()
