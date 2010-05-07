# -*- coding: utf-8 -*-

import os
import re
from amigu.util.folder import *
from amigu.apps.base import application
from amigu import _


class gaim:
    """Clase para el programa Gaim, actualmente Pidgin"""

    def __init__(self):
        """Constructor de la clase"""
        self.errors = []
        self.config_file = os.path.join(os.path.expanduser('~'), '.purple', 'accounts.xml')
        if not os.path.exists(self.config_file):
            folder(os.path.join(os.path.expanduser("~"),'.purple'))
            try:
                f = open (self.config_file, "w")
                f.write('<?xml version=\'1.0\' encoding=\'UTF-8\' ?>\n')
                f.write('<account version=\'1.0\'>\n')
                f.write('\n')
                f.write('</account>')
                f.close()
            except:
                self.error('Failed to create %s' % config_file)
                return 0

    def error(self,e):
        """Almacena los errores en tiempo de ejecución"""
        self.errors.append(e)

    def config_msn(self, cuenta):
        """Configura la cuenta de MSN
        
        Argumento de entrada:
        cuenta -> identificador de cuenta
        
        """
        bak = backup(self.config_file)
        if bak:
            try:
                o = open (bak, "r")
                f = open (self.config_file, "w")
                for linea in o.readlines():
                    f.write(linea)
                    if re.search('account version',linea): # insert after that line (only once)
                        f.write('\t<account>\n')
                        f.write('\t\t<protocol>prpl-msn</protocol>\n')
                        f.write('\t\t<name>%s</name>\n' % cuenta)
                        f.write('\t\t<settings>\n')
                        f.write('\t\t\t<setting name=\'check-mail\' type=\'bool\'>1</setting>\n')
                        f.write('\t\t\t<setting name=\'server\' type=\'string\'>messenger.hotmail.com</setting>\n')
                        f.write('\t\t\t<setting name=\'http_method\' type=\'bool\'>0</setting>\n')
                        f.write('\t\t\t<setting name=\'port\' type=\'int\'>1863</setting>\n')
                        f.write('\t\t\t<setting name=\'http_method_server\' type=\'string\'>gateway.messenger.hotmail.com</setting>\n')
                        f.write('\t\t</settings>\n')
                        f.write('\t\t\t<settings ui=\'gtk-gaim\'>\n')
                        f.write('\t\t\t<setting name=\'auto-login\' type=\'bool\'>1</setting>\n')
                        f.write('\t\t</settings>\n')
                        f.write('\t</account>\n')
                    # write de rest of de original config
                o.close()
                f.close()
            except:
                self.error('Failed to modify %s' % self.config_file)
                restore_backup(bak)
                o.close()
                f.close()
        else:
            self.error("Config Gaim failed")

    def config_yahoo(self, cuenta):
        """Configura la cuenta de Yahoo!
        
        Argumento de entrada:
        cuenta -> identificador de la cuenta de Yahoo!
        
        """
        bak = backup(self.config_file)
        if bak:
            try:
                o = open (bak, "r")
                f = open (self.config_file, "w")
                for linea in o.readlines():
                    f.write(linea)
                    if re.search('account version',linea): # insert after that line (only once)
                        f.write('\t<account>\n')
                        f.write('\t\t<protocol>prpl-yahoo</protocol>\n')
                        f.write('\t\t<name>%s</name>\n' % cuenta)
                        f.write('\t\t<settings>\n')
                        f.write('\t\t<setting name=\'check-mail\' type=\'bool\'>1</setting>\n')
                        f.write('\t\t<setting name=\'server\' type=\'string\'>scs.msg.yahoo.com</setting>\n')
                        f.write('\t\t<setting name=\'yahoojp\' type=\'bool\'>0</setting>\n')
                        f.write('\t\t<setting name=\'port\' type=\'int\'>5050</setting>\n')
                        f.write('\t\t<setting name=\'serverjp\' type=\'string\'>cs.yahoo.co.jp</setting>\n')
                        f.write('\t\t<setting name=\'port\' type=\'int\'>5050</setting>\n')
                        f.write('\t\t<setting name=\'xferjp_host\' type=\'string\'>filetransfer.msg.yahoo.co.jp</setting>\n')
                        f.write('\t\t<setting name=\'xfer_host\' type=\'string\'>filetransfer.msg.yahoo.com</setting>\n')
                        f.write('\t\t<setting name=\'xfer_port\' type=\'int\'>80</setting>\n')
                        f.write('\t\t</settings>\n')
                        f.write('\t\t<settings ui=\'gtk-gaim\'>\n')
                        f.write('\t\t<setting name=\'auto-login\' type=\'bool\'>1</setting>\n')
                        f.write('\t\t</settings>\n')
                        f.write('\t</account>\n')
                    # write de rest of de original config
                o.close()
                f.close()
            except:
                self.error('Failed to modify %s' % self.config_file)
                restore_backup(bak)
                o.close()
                f.close()
        else:
            self.error("Config Gaim failed")

    def config_gtalk (self, cuenta):
        """Configura la cuenta de Gtalk
        
        Argumento de entrada:
        cuenta -> identificador de la cuenta de Google Talk
        
        """
        bak = backup(self.config_file)
        if bak:
            try:
                o = open (bak, "r")
                f = open (self.config_file, "w")
                for linea in o.readlines():
                    f.write(linea)
                    if re.search('account version',linea): # insert after that line (only once)
                        f.write('\t<account>\n')
                        f.write('\t\t<protocol>prpl-jabber</protocol>\n')
                        f.write('\t\t<name>%s/Home</name>\n' % cuenta)
                        f.write('\t\t<settings>\n')
                        f.write('\t\t<setting name=\'require_tls\' type=\'bool\'>0</setting>\n')
                        f.write('\t\t<setting name=\'use_tls\' type=\'bool\'>1</setting>\n')
                        f.write('\t\t<setting name=\'connect_server\' type=\'string\'>talk.google.com</setting>\n')
                        f.write('\t\t<setting name=\'old_ssl\' type=\'bool\'>1</setting>\n')
                        f.write('\t<setting name=\'port\' type=\'int\'>5223</setting>\n')
                        f.write('\t\t</settings>\n')
                        f.write('\t\t<settings ui=\'gtk-gaim\'>\n')
                        f.write('\t\t<setting name=\'auto-login\' type=\'bool\'>1</setting>\n')
                        f.write('\t\t</settings>\n')
                        f.write('\t</account>\n')
                    # write de rest of de original config
                o.close()
                f.close()
            except:
                self.error('Failed to modify %s' % self.config_file)
                restore_backup(bak)
                o.close()
                f.close()
        else:
            self.error("Config Gaim failed")

# end class gaim

############################################################################


class kopete:
    """Clase para el programa Kopete"""

    def __init__(self):
        """Constructor de la clase"""
        self.errors = []
        self.config_file = os.path.join(os.path.expanduser('~'), '.kde', 'share', 'config', 'kopeterc')
        folder(os.path.join(os.path.expanduser('~'), '.kde', 'share', 'config'))

    def error(self, e):
        """Almacena los errores en tiempo de ejecución"""
        self.errors.append(e)

    def config_msn(self, cuenta):
        """Configura la cuenta de MSN
        
        Argumento de entrada:
        cuenta -> identificador de cuenta de MSN
        
        """
        bak = backup(self.config_file)
        try:
            f = open (self.config_file, "a")
            #insert at the bottom, the program automatically will reorder the file
            f.write('\n[Account_MSNProtocol_%s]\n' % cuenta)
            f.write('AccountId=%s\n' % cuenta)
            f.write('Protocol=MSNProtocol\n')
            f.write('serverName=messenger.hotmail.com\n')
            f.write('serverPort=1863\n')
            f.write('useHttpMethod=false\n')
            f.close()
        except:
            f.close()
            self.error("Failed to modify %s" % self.config_file)
            restore_backup(bak)

    def config_yahoo(self, cuenta):
        """Configura la cuenta de Yahoo!
        
        Argumento de entrada:
        cuenta -> identificador de cuenta de Yahoo!
        
        """
        bak = backup(self.config_file)
        try:
            f = open (self.config_file, "a")
            #insert at the bottom, the program automatically will reorder the file
            f.write('\n[Account_YahooProtocol_%s]\n' % cuenta)
            f.write('AccountId=%s\n' % cuenta)
            f.write('Protocol=YahooProtocol\n')
            f.write('Server=scs.msg.yahoo.com\n')
            f.write('Port=5050\n')
            f.close()
        except:
            f.close()
            self.error("Failed to modify %s" % self.config_file)
            restore_backup(bak)

    def config_gtalk(self, cuenta):
        """Configura la cuenta de Gtalk
        
        Argumento de entrada:
        cuenta -> identificador de cuenta de Google Talk
        
        """
        bak = backup(self.config_file)
        try:
            f = open (self.config_file, "a")
            #insert at the bottom, the program automatically will reorder the file
            f.write('\n[Account_YahooProtocol_%s]\n' % cuenta)
            f.write('\n[Account_JabberProtocol_%s]\n' % cuenta)
            f.write('AccountId=%s\n' % cuenta)
            f.write('AllowPlainTextPassword=true\n')
            f.write('CustomServer=true\n')
            f.write('Server=talk.google.com\n')
            f.write('Port=5223\n')
            f.write('HideSystemInfo=false\n')
            f.write('Protocol=JabberProtocol\n')
            f.write('UseSSL=true\n')
            f.close()
        except:
            f.close()
            self.error("Failed to modify %s" % self.config_file)
            restore_backup(bak)

# end class kopete

############################################################################



if __name__ == "__main__":
    pass
