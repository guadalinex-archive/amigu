# -*- coding: utf-8 -*-
# La clase registry permite acceder a la información contenida en el registro de Windows.
# La compatibilidad con los registros de Windows viene dada por el programa 'dumphive'
# que convierte el contenido del registro en un fichero de texto plano.
# Se añaden funcionalidades para buscar claves prefijadas dentro del registro de usuario
# o NTUSER.DAT asi cómo la función genérica de buscar cualquier entrada del registro.
import os
import re
import glob
from amigu.apps.base import application
from amigu.apps.win import messenger, mail, webbrowser, settings
from amigu.computer.users.base import generic_usr
from amigu.util.folder import *
from amigu.util.winreg import regedit
from amigu import _
from gtk import TreeStore


class winuser(regedit, generic_usr):
    """Clase para los usuarios de Windows"""

    def __init__(self, dir, pc, ops):
        """Constructor de la clase.
        Recibe la ruta a la carpeta del usuario de Windows"""
        regedit.__init__(self, dir)
        generic_usr.__init__(self, dir, pc, ops)


    def init_apps(self):
        pass

    def get_copier(self, folder):
        return copier(self, folder)

    def get_path(self):
        """Devuelve la carpeta del usuario"""
        return self.path

    def get_personal_folder(self):
        """Devuelve las carpetas personales y de configuración del usuario"""
        return self.folders['Personal']

    def get_avatar(self):
        if os.path.exists(os.path.join(self.folders["Local AppData"].path,'Temp',self.name+".bmp")):
            return os.path.join(self.folders["Local AppData"].path,'Temp',self.name+".bmp")
        elif os.path.exists(os.path.join(self.folders["AppData"].path.replace(self.name, 'All Users'), 'Microsoft', 'User Account Pictures', self.name+".bmp")):
            return os.path.join(self.folders["AppData"].path.replace(self.name, 'All Users'), 'Microsoft', 'User Account Pictures', self.name+".bmp")
        else:
            return "/usr/share/pixmaps/nobody.png"

    def get_name(self):
        """Devuelve el nombre del usuario de Windows"""
        return self.name

    def get_AOL_accounts(self):
        """Devuelve una lista con los usuarios de AOL Instant Messenger"""
        r = self.search_key("Software\America Online\AOL Instant Messenger (TM)\CurrentVersion\Users")
        return r

    def get_GTALK_account(self):
        """Devuelve el identificador usado en Gtalk"""
        r = self.search_key("Software\Google\Google Talk\Accounts")
        try:
            return r['a'].split('/')[0]
        except:
            return 0

    def get_OUTLOOK_accounts(self):
        claves = {"Outlook9":[], "Outlook Express":[], "Outlook11":[], "Outlook12":[]}
        ou11 = re.compile(r'\[NTUSER\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows Messaging Subsystem\\Profiles\\.*Outlook.*\\\w+\\\d+')
        ou12 = re.compile(r'\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Windows Messaging Subsystem\\Profiles\\Outlook\\\w+\\\d+')
        try:
            reg = open(self.tempreg, 'r')
        except:
            self.error('No fue posible acceder al archivo')
        else:
            for e in reg.readlines():
                if e.find('\Software\\Microsoft\\Office\\Outlook\\OMI Account Manager\\Accounts\\0') != -1:
                    claves["Outlook9"].append(e)
                elif e.find('\Software\\Microsoft\\Internet Account Manager\\Accounts\\0') != -1:
                    claves["Outlook Express"].append(e)
                elif ou11.match(e):
                    claves["Outlook11"].append(e)
                elif e.find('\Software\\Microsoft\\Office\\12.0\\Outlook\\Catalog') != -1:
                    claves["Outlook12"].append(e)
                elif ou12.search(e):
                    claves["Outlook12"].append(e)

            reg.close()
            return claves

    def get_WINDOWS_MAIL_accounts(self):
        dict = {}
        ruta = os.path.join(self.folders["Local AppData"].path, 'Microsoft', 'Windows Mail')
        if os.path.exists(ruta):
            for d in os.listdir(ruta):
                file = os.path.join(ruta, d, '*.oeaccount')
                if glob.glob(file):
                    dict[d] = glob.glob(file)[0]
        return dict
        
    def get_WINDOWS_LIVE_MAIL_accounts(self):
        dict = {}
        ruta = os.path.join(self.folders["Local AppData"].path, 'Microsoft', 'Windows Live Mail')
        if os.path.exists(ruta):
            for d in os.listdir(ruta):
                file = os.path.join(ruta, d, '*.oeaccount')
                if glob.glob(file):
                    dict[d] = glob.glob(file)[0]
        return dict
        
    def get_THUNDERBIRD_accounts(self):
        prefs = self.get_THUNDERBIRD_prefs()
        try:
            p = open(prefs, 'r')
            content = p.readlines()
            p.close()
        except:
            return []
        else:
            pattern = re.compile('.+mail\.accountmanager\.accounts.*\s+\"(?P<accounts>.+)\".*')
            for l in content:
                m = pattern.match(l)
                if m:
                    return m.group('accounts').split(',')
                
            
    def get_THUNDERBIRD_prefs(self):
        prefs = glob.glob(os.path.join(self.folders["AppData"].path, 'Thunderbird', 'Profiles', '*.default', 'prefs.js'))
        if prefs:
            return prefs[0]

    def get_MSN_account(self):
        """Devuelve la cuenta asociada a MSNMessenger"""
        r = self.search_key("Software\Microsoft\MSNMessenger")
        try:
            return r["User .NET Messenger Service"]
        except:
            return 0

    def get_YAHOO_account(self):
        """Devuelve el identificador usado en Yahoo! Messenger"""
        r = self.search_key("Software\Yahoo\pager")
        try:
            return r["Yahoo! User ID"]
        except:
            return 0

    def check_path(self, path):
        i = path.find(':')
        path = path.replace(path[:i+1], self.mount_points[path[i-1:i+1]])
        path = path.replace('\\','/')
        return path

    def get_user_folders(self, pc):
        """Devuelve las carpetas de archivos, confifguraciones y programas del usuario"""
        r = self.search_key("Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
        if r:
            if "!Do not use this registry key" in r:
                del r["!Do not use this registry key"]
            if self.os.find("Vista") > 1:
                r["Downloads"] = os.path.join(os.path.split(r["Personal"])[0], "Downloads")
            #print r
            self.mount_points = pc.map_win_units(r)
            #print "\nGetting shell folders..."
            for k, v in r.iteritems():
                if v:
                    unit = v[:2]
                    try:
                        if not k == 'Wallpaper':
                            r[k] = folder(v.replace(unit, self.mount_points[unit]), False)
                            #print "%s: %s --> %s" % (k, v, r[k].path)
                        else:
                            r[k] = v.replace(unit, self.mount_points[unit])
                            #print "%s: %s --> %s" % (k, v, r[k])

                    except:
                        r = 0
                        print "Unknown partition: %s" % unit
                        break
            print "\n"
            return r
        else:
            raise Exception("Error reading de registry")


    def get_messenger_accounts(self):
        """Devuelve las cuentas de mensajería de Windows Live Messenger"""
        accounts = []
        live_msn = folder(os.path.join(self.folders['Local AppData'].path, 'Microsoft', 'Messenger'), False)
        if live_msn.path and os.path.exists(live_msn.path):
            for m in os.listdir(live_msn.path):
                if m.find('@') != -1:
                    accounts.append(m)
        return accounts

    def get_details(self):
        size = "0Mb"
        if self.os.find("XP") > 1:
            size = "%.2fMb" % (self.folders['Personal'].get_size()/1024.0)
        elif self.os.find("Vista") > 1:
            s = 0
            for p in ("Personal", "My Video", "My Music", "My Pictures", "Desktop", "Downloads"):
                s +=  self.folders[p].get_size()
            size = "%.2fMb" % (int(s)/1024.0)
        return "Sistema Operativo"+": "+self.os +", "+ size +" de datos"

    def get_info(self):
        """Devuelve la información de archivos y programas del usuario"""
        pass

    def all_errors(self):
        """Recopila los errores producidos en tiempo de ejecuccion"""
        self.errors = self.errors + self.gaim.errors + self.firefox.errors + self.thunderbird.errors
        return self.errors

    def get_tree_options(self, update=False):
        """Genera el árbol de opciones para el usario seleccionado"""

        if self.tree_options:
            if update:
                self.tree_options.clear()
            else:
                return self.tree_options
        else:
            self.tree_options = TreeStore( str, 'gboolean', str, str, object)


        name_usr = self.tree_options.append(None, [self.get_name(), None, None, _('Usuario seleccionado'), None])

        # Files
        data = self.tree_options.append(name_usr , [_("Archivos"), None, None, _('Importar archivos'), None] )
        folder_2_copy = []
        if self.os.find("Vista") > 1:
            for s in folder(self.path).get_subfolders():
                add = s.get_size() and not s.get_name() in ('AppData', 'Links', 'Tracing', 'Searches', 'Cookies', 'NetHood', 'PrintHood', 'Local Settings', 'Application Data', 'Recent', 'Templates', 'SendTo', 'Start Menu', 'Saved Games')
                if add:
                    folder_2_copy.append(s)
        else:
            folder_2_copy.append(self.folders['Personal'])
            folder_2_copy.append(self.folders['Desktop'])

            # eMule
        if 'eMule' in self.folders.keys():
            emule_inc = self.get_incoming_path()
            emule_temp = self.get_temp_path()
            try:
                self.tree_options.append( data, [_("Descargados eMule"), None, str(emule_inc.get_size()), _('Archivos descargados: ')+ emule_inc.get_info(), ''] )
                self.tree_options.append( data, [_("Temporales eMule"), None, str(emule_temp.get_size()), _('Archivos temporales: ')+ emule_temp.get_info(), ''] )
            except:
                pass
        for f in folder_2_copy:
            c = self.get_copier(f)
            self.tree_options.append( data, [c.name, None, str(c.size), c.description, c] )


        # configuraciones
        conf = self.tree_options.append(name_usr , [_("Configuraciones"), None, None, _('Importar configuraciones'), None] )

        # Bookmarks
        navegadores = []
        try:
            navegadores.append(webbrowser.winfirefox(self))
        except:
            pass
        try:
            navegadores.append(webbrowser.iexplorer(self))
        except:
            pass
        try:
            navegadores.append(webbrowser.opera(self))
        except:
            pass
        try:
            navegadores.append(webbrowser.chrome(self))
        except:
            pass
        if navegadores:
            nav = self.tree_options.append(conf, [_("Navegadores"), None, None, _('Navegadores web'), None] )
            for n in navegadores:
                self.tree_options.append(nav, [n.name, None, n.size, n.description, n] )

        # Correo
        lectores = []
        out = self.get_OUTLOOK_accounts()
        for k, v in out.iteritems():
            for o in v:
                try:
                    if k == "Outlook12":
                        lectores.append(mail.outlook12(self, o))
                    elif k == "Outlook11":
                        lectores.append(mail.outlook11(self, o))
                    elif k == "Outlook Express":
                        lectores.append(mail.outlook_express(self, o))
                    elif k == "Outlook9":
                        lectores.append(mail.outlook9(self, o))
                except:
                    pass
        for k,v in self.get_WINDOWS_MAIL_accounts().iteritems():
            try:
                lectores.append(mail.windowsmail(self, v))
            except:
                pass
        for k,v in self.get_WINDOWS_LIVE_MAIL_accounts().iteritems():
            try:
                lectores.append(mail.windowslivemail(self, v))
            except:
                pass
        for a in self.get_THUNDERBIRD_accounts():
            try:
                lectores.append(mail.winthunderbird(self, a))
            except:
                pass
        if lectores:
            lec = self.tree_options.append(conf, [_("Gestores de correo"), None, None, _('Gestores de correo electrónico'), None] )
            for l in lectores:
                self.tree_options.append(lec, [l.name, None, l.size, l.description, l] )


        # Instant Messenger
        cuentas = messenger.get_IM_accounts(self)
        if cuentas:
            im = self.tree_options.append(conf, [_("Mensajería Instantánea"), None, None, _('Cuentas de IM'), None] )
        for a in cuentas:
            self.tree_options.append(im, [a.name, None, a.size, a.description, a] )


        # Otras configuraciones
        configuraciones = []
        try:
            configuraciones.append(settings.wallpaper(self))
        except:
            pass
        try:
            configuraciones.append(settings.fonts_installer(self))
        except:
            pass
        try:
            configuraciones.append(settings.emule(self))
        except:
            pass
        try:
            configuraciones.append(settings.avatar(self))
        except:
            pass
        if configuraciones:
            cfg = self.tree_options.append(conf, [_("Otros"), None, None, _('Otras opciones de configuración'), None] )
            for c in configuraciones:
                self.tree_options.append(cfg, [c.name, None, c.size, c.description, c] )


        return self.tree_options
#end class user


############################################################################

def test():
    from amigu.computer.info import pc
    com = pc()
    com.check_all_partitions()
    print "Analizando usuarios de Windows"
    for user_path, ops in com.get_win_users().iteritems():
        u = winuser(user_path, com, ops)
        #print u.get_details()
        #print u.get_avatar()
        try:
            print u.get_OUTLOOK_accounts()
            print u.get_THUNDERBIRD_accounts()
            u.get_tree_options()
        except:
            u.clean()

if __name__ == "__main__":
    test()
