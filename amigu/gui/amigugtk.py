#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import sys, os, re, gobject, gtk, time, threading,  traceback, syslog, shutil
from amigu import __version__ as ver
from amigu import _
from amigu.apps.win import mail, webbrowser, messenger, settings
from amigu.computer.info import pc as mipc
from amigu.computer.users import mswin
from amigu.computer.users import openos
from amigu.computer.users import macos
from amigu.computer.users.base import generic_usr
from amigu.util.folder import *


dir_imagenes = "/usr/share/pixmaps/amigu"
#Initializing the gtk's thread engine
gtk.gdk.threads_init()
version = "AMIGU " + ver
#ver = "0.7"


class Asistente:
    """GUI for AMIGU
    Implementación del asistente de migración de Guadalinex sobre pygtk"""

    def excepthook(self, exctype, excvalue, exctb):
        """Manejador de excepciones"""
        if (issubclass(exctype, KeyboardInterrupt) or issubclass(exctype, SystemExit)):
            return
        tbtext = ''.join(traceback.format_exception(exctype, excvalue, exctb))
        syslog.syslog(syslog.LOG_ERR, "Exception in GTK frontend (invoking crash handler):")
        for line in tbtext.split('\n'):
            syslog.syslog(syslog.LOG_ERR, line)
        print >>sys.stderr, ("Exception in GTK frontend (invoking crash handler):")
        print >>sys.stderr, tbtext

        #self.dialogo_error(tbtext)
        if os.path.exists('/usr/share/apport/apport-gtk'):
            self.previous_excepthook(exctype, excvalue, exctb)
        tbtext = _('Se ha producido un error durante la ejecucción del programa que impide continuar.') + _('Si dicho fallo se repite por favor comuníquelo al equipo de desarrolladores adjuntando el siguiente error:') + '\n\n' + tbtext
        error_dlg = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, message_format=tbtext, buttons=gtk.BUTTONS_CLOSE)
        error_dlg.run()
        error_dlg.destroy()
        self.destroy(None)
        sys.exit(1)

    def __init__(self):
        """Constructor de la interfaz"""
        self.previous_excepthook = sys.excepthook
        sys.excepthook = self.excepthook
        
        self.working = False
        self.abort = False

        # Main Window
        self.window = gtk.Window()
        self.window.set_title(_("Asistente de Migración a Guadalinex"))
        self.window.set_default_size(700, 570)
        self.window.set_border_width(0)
        self.window.move(150, 50)
        self.window.connect("destroy", self.destroy)
        self.window.set_icon_from_file(os.path.join(dir_imagenes, "icon_paginacion.png"))
        # Atributos
        self.paso = 1
        self.url = "http://forja.guadalinex.org/webs/amigu/"

        self.watch = gtk.gdk.Cursor(gtk.gdk.WATCH)
        self.hilo = None

        # Usuarios
        self.list_users = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING, gobject.TYPE_STRING, object)
        self.users = gtk.TreeView(self.list_users)
        self.users.set_rules_hint(True)
        self.users.connect("cursor-changed", self.marcar_usuario)
        self.renderer = gtk.CellRendererText()
        self.renderer2 = gtk.CellRendererText()
        self.renderer3 = gtk.CellRendererText()
        self.renderer_pixbuf = gtk.CellRendererPixbuf()
        self.renderer_pixbuf.set_property("stock-size",3)
        self.renderer_pixbuf.set_property('xalign', 0.5)
        self.renderer_pixbuf.set_property('width', 100)
        self.renderer_pixbuf.set_property('ypad', 5)
        column1 = gtk.TreeViewColumn(_("Cuenta"), self.renderer3, text=1)
        self.renderer3.set_property('scale', 1.5)
        self.renderer3.set_property('width', 300)
        column2 = gtk.TreeViewColumn(_("Sistema Operativo"), self.renderer, text=2)
        column3 = gtk.TreeViewColumn(_("Imagen"), self.renderer_pixbuf, pixbuf=0)
        self.users.append_column( column3 )
        self.users.append_column( column1 )
        self.users.append_column( column2 )
        self.users.expand_all()

        # Opciones
        self.options = gtk.TreeView()
        self.renderer1 = gtk.CellRendererToggle()
        self.renderer1.set_property('activatable', True)
        self.renderer1.connect( 'toggled', self.marcar_opcion)
        column4 = gtk.TreeViewColumn(_("Opción"), self.renderer, text=0)
        column5 = gtk.TreeViewColumn(_("Tamaño"), self.renderer2, text=2)
        self.renderer2.set_property('xalign', 1.0)
        column5.set_cell_data_func(self.renderer2, self.space_units, data=None)

        column6 = gtk.TreeViewColumn(_("Descripción"), self.renderer, text=3)
        column6.set_cell_data_func(self.renderer, self.italic, data=None)
        column7 = gtk.TreeViewColumn(_("Migrar"), self.renderer1 )
        column7.add_attribute( self.renderer1, "active", 1)
        self.options.append_column( column4 )
        self.options.append_column( column7 )
        self.options.append_column( column5 )
        self.options.append_column( column6 )

        #Resumen
        self.tasks = gtk.ListStore( gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_FLOAT, gobject.TYPE_STRING, object)
        self.resumen = gtk.TreeView(self.tasks)
        column8 = gtk.TreeViewColumn(_("Tarea"), self.renderer, text=0)
        column9 = gtk.TreeViewColumn("", self.renderer_pixbuf, stock_id=1)
        progressrenderer = gtk.CellRendererProgress()
        column10 = gtk.TreeViewColumn(_("Progreso"), progressrenderer, value=2, text=3)
        progressrenderer.set_property('height', 10)
        self.resumen.append_column( column9 )
        self.resumen.append_column( column8 )
        self.resumen.append_column( column10 )


        gtk.about_dialog_set_url_hook(self.open_url, self.url)

        # ventana principal
        contenedor = gtk.VBox(False, 1)#Creo la caja vertical principal
        self.inicio = gtk.VBox(False, 1)
        self.segunda = gtk.VBox(False, 1)
        self.tercera = gtk.HBox(False, 1)
        self.cuarta = gtk.VBox(False, 1)
        self.quinta = gtk.VBox(False, 1)
        separador1 = gtk.HSeparator()
        separador2 = gtk.HSeparator()
        self.tooltips = gtk.Tooltips()
        principal = gtk.HBox(False, 1)#Creo lo que se va a quedar siempre en la ventana
        principal0 = gtk.HBox(False, 1)#Creo lo que se va a quedar siempre en la ventana
        principal1 = gtk.VBox(False, 1)#Creo lo que va a ir variando
        principal2 = gtk.HBox(False, 1)#Creo lo que se va a quedar siempre en la ventana
        principal2ver1 = gtk.HBox(False, 1)
        principal2ver2 = gtk.HButtonBox()
        principal2ver2.set_layout(gtk.BUTTONBOX_END)
        principal2ver2.set_size_request(550,60)
        principal2ver2.set_border_width(10)
        image = gtk.Image()
        image.set_from_file(os.path.join(dir_imagenes, "cab_amigu.png"))

        image1 = gtk.Image()
        image1.set_from_file(os.path.join(dir_imagenes, "icon_paginacion.png"))

        self.etapa = gtk.Label()
        self.etapa.set_use_markup(True)
        self.etapa.set_markup("<span face = \"arial\" size = \"8000\" foreground = \"chocolate\"><b>Paso %d de 5</b></span>"%self.paso)

        espacio = gtk.Label()

        # botones
        self.toolbar = gtk.Toolbar()
        self.stop_boton = gtk.Button(stock = gtk.STOCK_CANCEL)
        self.back_boton = gtk.Button(stock = gtk.STOCK_GO_BACK)
        self.forward_boton = gtk.Button(stock = gtk.STOCK_GO_FORWARD)
        self.apply_boton = gtk.Button(stock = gtk.STOCK_APPLY)
        self.exit_boton = gtk.Button(stock = gtk.STOCK_QUIT)
        self.about_boton = gtk.Button(label=_("Acerca de"))


        # añadir
        self.labelpri = gtk.Label("")

        self.labelpri.set_line_wrap(True)
        self.labelpri.set_justify(gtk.JUSTIFY_LEFT)
        self.labelpri.set_use_markup(True)
        principal.pack_start(image, False, False, 0)
        principal0.pack_start(self.labelpri, False, False, 10)
        principal1.pack_start(self.inicio, True, False, 0)
        principal2.pack_start(principal2ver1, False, False, 0)
        principal2.pack_start(principal2ver2, True, False, 0)

        principal2ver1.pack_start(image1, True, True, 0)
        principal2ver1.pack_start(self.etapa, False, False, 1)
        principal2ver2.pack_start(self.about_boton, False, False, 0)
        principal2ver2.pack_start(self.back_boton, False, False, 0)
        principal2ver2.pack_start(self.forward_boton, False, False, 0)
        principal2ver2.pack_start(self.apply_boton, False, False, 0)
        principal2ver2.pack_start(espacio, True, True, 2)
        principal2ver2.pack_start(self.exit_boton, False, False, 0)
        principal2ver2.pack_start(self.stop_boton, True, False, 5)
        contenedor.pack_start(principal, False, False, 1)
        contenedor.pack_start(separador1, False, True, 10)
        contenedor.pack_start(principal0, False, False, 1)
        contenedor.pack_start(principal1, True, True, 1)
        contenedor.pack_start(separador2, False, True, 10)
        contenedor.pack_start(principal2, False, True, 1)
        #contenedor.pack_start(self.toolbar, False, True, 0)
        principal1.pack_start(self.segunda, True, True, 1)
        principal1.pack_start(self.tercera, True, True, 1)
        principal1.pack_start(self.cuarta, True, True, 1)
        principal1.pack_start(self.quinta, True, True, 1)
        self.window.add(contenedor)#Añado a la ventana el contenedor

        # eventos
        self.back_boton.connect("clicked", self.etapa_anterior)
        self.forward_boton.connect("clicked", self.etapa_siguiente)
        self.apply_boton.connect("clicked", self.dialogo_confirmacion)
        self.exit_boton.connect("clicked", self.destroy)
        self.stop_boton.connect_object("clicked", self.dialogo_cancelacion, self.window)
        self.about_boton.connect_object("clicked", self.about, self.window)

        # mostrar ventana
        self.window.show_all()
        self.apply_boton.hide()
        self.exit_boton.hide()


################Primera Ventana

        # crear
        label1 = gtk.Label()
        label1.set_use_markup(True)
        label1.set_line_wrap(True)
        label1.set_justify(gtk.JUSTIFY_CENTER)
        label1.set_markup('<b>'+_('Bienvenido al Asistente de MIgración de GUadalinex - AMIGU') + '\n\n' + _('Este asistente le guiará durante el proceso de migración de sus documentos y configuraciones de su sistema operativo Windows.') + '\n' + _('Pulse el botón Adelante para comenzar.') + '</b>')

        # añadir
        self.inicio.pack_start(label1, True, True, 10)

        # mostrar
        self.back_boton.hide_all()
        self.inicio.show_all()


################Segunda Ventana

        #crear
        self.segundahor1 = gtk.HBox(False, 1)
        self.segundahor2 = gtk.HBox(True, 10)
        self.label2 = gtk.Label()
        self.label2.set_use_markup(True)
        self.label2.set_markup('<b>'+_('Buscando usuarios de otros sistemas...')+'</b>')
        frame1 = gtk.Frame(_("Usuarios encontrados"))
        sw = gtk.ScrolledWindow()
        sw.set_size_request(600, 175)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        # añadir
        sw.add(self.users)
        frame1.add(sw)
        self.segundahor1.pack_start(self.label2, False, False, 10)
        self.segundahor2.pack_start(frame1, True, True, 10)
        self.segunda.pack_start(self.segundahor2, True, True, 1)
        self.segunda.pack_start(self.segundahor1, False, False, 1)



###############################Tercera Ventana

        # crear
        self.terceraver1 = gtk.HBox(False, 10)
        self.terceraver2 = gtk.HBox(False, 5)
        self.terceraver3 = gtk.HBox(True, 10)
        self.terceraver4 = gtk.HBox(True, 10)
        
        self.tercerahor1 = gtk.VBox(False, 3)
        self.tercerahor2 = gtk.VBox(False, 10)
        self.tercerahor3 = gtk.VBox(False, 5)
        self.tercerahor4 = gtk.VBox(True, 5)
        self.tercerahor5 = gtk.VBox(False, 5)
        self.tercerahor6 = gtk.VBox(True, 5)
        self.frame4 = gtk.Frame(_("Cuenta"))
        frame2 = gtk.Frame(_("Espacio requerido"))
        self.entry = gtk.Entry()
        self.entry.set_max_length(50)
        f = folder(os.path.expanduser('~'))
        self.required = {'data':0, 'conf':0}
        self.available = {'data':f.get_free_space(), 'conf':f.get_free_space()}

        self.cuenta = gtk.Label()
        self.cuenta.set_use_markup(True)
        

        self.datos_libre = gtk.Label()
        self.datos_libre.set_use_markup(True)
        self.datos_libre.set_justify(gtk.JUSTIFY_RIGHT)

        self.conf_libre = gtk.Label()
        self.conf_libre.set_use_markup(True)
        self.conf_libre.set_justify(gtk.JUSTIFY_RIGHT)

        self.datos_req = gtk.Label()
        self.datos_req.set_use_markup(True)
        self.datos_req.set_justify(gtk.JUSTIFY_RIGHT)

        self.conf_req = gtk.Label()
        self.conf_req.set_use_markup(True)
        self.conf_req.set_justify(gtk.JUSTIFY_RIGHT)

        self.entry.connect("activate", self.actualizar_espacio)
        self.entry.set_text(f.get_path())
        self.actualizar_espacio()

        boton22 = gtk.Button(label = _("Seleccionar otra carpeta"), stock = None)
        boton22.connect_object("clicked", self.buscar, self.window)
        self.tooltips.set_tip(boton22, _("Elija la carpeta Destino donde quiere guardar los archivos"))

        frame5 = gtk.Frame(_("Opciones de migración"))
        self.arbol_inicializado = False
        self.imagen_usuario = gtk.Image()

        self.sw3 = gtk.ScrolledWindow()
        self.sw3.set_size_request(280, 200)
        self.sw3.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.sw3.add(self.options)

        # añadir
        self.tercera.pack_start(self.terceraver1, False, False, 0)
        self.tercera.pack_start(frame5, True, True, 0)
        self.terceraver1.pack_start(self.tercerahor2, False, False, 10)
        self.terceraver2.pack_start(self.imagen_usuario, True, True, 5)
        self.terceraver2.pack_start(self.cuenta, True, True, 5)
        frame5.add(self.sw3)
        self.frame4.add(self.terceraver2)
        frame2.add(self.tercerahor1)
        self.tercerahor3.pack_start(gtk.Label(_('Datos de usuario')), True, True, 0)
        self.tercerahor3.pack_start(gtk.Label(_('Espacio disponible')), True, True, 0)
        self.tercerahor4.pack_start(self.datos_req, True, False, 0)
        self.tercerahor4.pack_start(self.datos_libre, True, False, 0)
        self.tercerahor1.pack_start(self.terceraver3, True, False, 0)
        self.terceraver3.pack_start(self.tercerahor3, True, False, 0)
        self.terceraver3.pack_start(self.tercerahor4, True, True, 0)
        self.tercerahor1.pack_start(self.entry, True, False, 0)
        self.tercerahor1.pack_start(boton22, True, False, 0)
        self.tercerahor1.pack_start(gtk.HSeparator(), True, False, 0)
        self.tercerahor1.pack_start(self.terceraver4, True, True, 0)
        self.terceraver4.pack_start(self.tercerahor5, True, False, 0)
        self.terceraver4.pack_start(self.tercerahor6, True, True, 0)
        self.tercerahor5.pack_start(gtk.Label(_('Configuraciones')), True, True, 0)
        self.tercerahor5.pack_start(gtk.Label(_('Espacio disponible')), True, True, 0)
        self.tercerahor6.pack_start(self.conf_req, True, False, 0)
        self.tercerahor6.pack_start(self.conf_libre, True, False, 0)
        self.tercerahor2.pack_start(self.frame4, True, False, 0)
        self.tercerahor2.pack_start(frame2, True, False, 0)


################Cuarta Ventana

        # crear
        self.cuartahor1 = gtk.HBox(False, 10)
        frame3 = gtk.Frame(_("Tareas a realizar"))
        sw1 = gtk.ScrolledWindow()
        sw1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw1.set_size_request(600, 225)
        self.progreso = gtk.ProgressBar(None)
        self.progreso.set_fraction(0.0)
        self.progreso.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
        self.progreso.set_text(_("Realizando las tareas solicitadas..."))

        #añadir
        self.cuarta.pack_start(self.cuartahor1, True, True, 0)
        self.cuartahor1.pack_start(frame3, True, True, 10)
        frame3.add(sw1)
        sw1.add(self.resumen)
        self.cuarta.pack_start(self.progreso, False, False, 10)

        try:
            child = gtk.EventBox()
            b =  gtk.LinkButton(self.url, label=_("Más información sobre Amigu"))
            child.add(b)
            text_view.add_child_in_window(child, gtk.TEXT_WINDOW_TEXT, 480, 173)
        except:
            pass


########Cuadros de dialogo

    def about(self, widget):
        dialog = gtk.AboutDialog()
        dialog.set_name("AMIGU")
        dialog.set_version(ver)
        dialog.set_copyright("Copyright © 2006-2009 Junta de Andalucía")
        dialog.set_website(self.url)
        dialog.set_website_label(self.url)
        dialog.set_authors([
            _("Programadores") + ':',
            'Emilia Abad Sánchez <email>\n',
            'Fernando Ruiz Humanes <email>\n'
            #_('Contributors:'), # FIXME: remove ":"
        ])
        dialog.set_artists([_("Diseñadora gráfica") + ':',
            'Emilia Abad Sánchez <email>\n',
            _("Logo e icono") + " por Sadesi"
        ])
        dialog.set_translator_credits(_("Este programa aún no ha sido traducido a otros idiomas"))
        logo_file = os.path.abspath(os.path.join(dir_imagenes, 'icon_paginacion.png'))
        logo = gtk.gdk.pixbuf_new_from_file(logo_file)
        dialog.set_logo(logo)
        if os.path.isfile('/usr/share/common-licenses/GPL'):
            dialog.set_license(open('/usr/share/common-licenses/GPL').read())
        else:
            dialog.set_license("This program is released under the GNU General Public License.\nPlease visit http://www.gnu.org/copyleft/gpl.html for details.")
        dialog.set_comments(_("asistente a la migración de Guadalinex"))
        dialog.run()
        dialog.destroy()


    def dialogo_advertencia(self, mensaje = ""):
        """Muestra mensajes de aviso"""
        # crear
        advertencia = gtk.Dialog(_("Aviso"), self.window, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                     (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,))
        logoad = gtk.Image()
        logoad.set_from_stock(gtk.STOCK_DIALOG_WARNING, 6)
        iconad = advertencia.render_icon(gtk.STOCK_DIALOG_WARNING, 1)
        mensaje = gtk.Label(mensaje)
        h1 = gtk.HBox(False, 10)


        # añadir
        advertencia.set_icon(iconad)
        advertencia.vbox.pack_start(h1, True, False, 10)
        h1.pack_start(logoad, True, False, 10)
        h1.pack_start(mensaje, True, False, 10)
        advertencia.show_all()
        advertencia.set_default_response(gtk.RESPONSE_ACCEPT)
        advertencia.run()
        #r = advertencia.response()
        advertencia.destroy()



    def dialogo_cancelacion(self, widget):
        """Muestra el cuadro diálogo de cancelación del proceso."""
        # crear
        cancelar = gtk.Dialog(_("Alerta"), self.window, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                     (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        logo = gtk.Image()
        logo.set_from_stock(gtk.STOCK_DIALOG_QUESTION, 6)
        icon = cancelar.render_icon(gtk.STOCK_DIALOG_QUESTION, 1)
        cancelar.set_icon(icon)
        if self.working:
            self.pause = True
            pregunta = gtk.Label(_("¿Está seguro que desea detener el proceso de migración?"))
        else:
            pregunta = gtk.Label(_("¿Está seguro que desea salir del asistente de migración?"))
        cancelar.set_default_response(gtk.RESPONSE_REJECT)
        h1 = gtk.HBox(False, 10)

        # añadir
        h1.pack_start(logo, True, False, 10)
        h1.pack_start(pregunta, True, False, 10)
        cancelar.vbox.pack_start(h1, True, False, 10)

        #mostrar
        cancelar.show_all()
        response = cancelar.run()
        cancelar.destroy()
        if response == gtk.RESPONSE_ACCEPT:
            self.destroy(None)
        else:
            self.pause = False


    def dialogo_confirmacion(self, widget):
        """Muestra el diálogo de confirmación antes de empezar la migración"""
        # crear
        confirmar = gtk.Dialog(_("Confirmación"), self.window, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                     (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT, gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        logo = gtk.Image()
        logo.set_from_stock(gtk.STOCK_DIALOG_QUESTION, 6)
        icon = confirmar.render_icon(gtk.STOCK_DIALOG_QUESTION, 1)
        confirmar.set_icon(icon)
        pregunta = gtk.Label(_('El asistente ha reunido la información necesaria para realizar la migración.') + '\n' + _('Es aconsejable cerrar todas las aplicaciones antes continuar.') + '\n' + _('¿Desea comenzar la copia de archivos/configuraciones?'))

        h1 = gtk.HBox(False, 10)

        # añadir
        h1.pack_start(logo, True, False, 10)
        h1.pack_start(pregunta, True, False, 10)

        confirmar.vbox.pack_start(h1, True, False, 10)

        # mostrar
        confirmar.show_all()
        response  = confirmar.run()
        confirmar.destroy()
        if response == gtk.RESPONSE_ACCEPT:
            self.etapa_siguiente(None)


    def buscar(self, widget):
        """Muestra el cuadro diálogo para seleccionar la ubicación de destino de los archivos"""
        # crear
        dialog = gtk.FileChooserDialog(_("Destino"), None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER, (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_SAVE, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_current_folder(os.path.expanduser('~'))

        # run
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            self.entry.set_text(dialog.get_current_folder())
            self.actualizar_espacio(self.window, self.entry)
        dialog.destroy()

########Eventos

    def open_url(self, dialog, url, widget):
        #url_show(url)
        pass

    def destroy(self, widget, data=None):
        """Finaliza la ejecución del asistente y limpiar los archivos temporales"""
        if self.working:
            self.abort = True
            self.pause = False
            return 0
        print _("Saliendo del asistente")
        iter = self.list_users.get_iter_root()
        model = self.users.get_model()
        while iter:
            print _("Eliminando archivos temporales...")
            model.get_value(iter, 3).clean()
            iter = self.list_users.iter_next(iter)
        gtk.main_quit()

    def etapa_siguiente(self, widget):
        """Muestra la siguiente etapa"""
        self.stop_boton.window.set_cursor(self.watch)
        self.paso += 1
        self.mostrar_paso()


    def etapa_anterior(self, widget):
        """Muestra la etapa previa"""
        self.stop_boton.window.set_cursor(self.watch)
        self.paso -= 1
        self.mostrar_paso()


    def marcar_usuario(self, widget):
        self.forward_boton.set_sensitive(True)


    def actualizar_espacio(self, widget=None):
        """Actualiza el espacio libre en disco"""
        destino = self.entry.get_text()
        if os.path.exists(destino):
            d = folder(destino)
            self.available["data"] = d.get_free_space()
        self.datos_libre.set_markup("<i>%dKiB</i>" % self.available["data"])
        self.conf_libre.set_markup("<i>%dKiB</i>" % self.available["conf"])
        self.datos_req.set_markup("<i>%dKiB</i>" % self.required["data"])
        self.conf_req.set_markup("<i>%dKiB</i>" % self.required["conf"])


    def marcar_opcion( self, cell, path):
        """Establece el estado marcado/desmarcado a las opciones de migración y sus descendientes"""
        model = self.options.get_model()
        iterator = model.get_iter(path)
        checked = not cell.get_active()
        self.options.expand_row(path, True)
        self.recorrer_arbol(iterator, model, checked)
        self.actualizar_espacio()
        return checked


######## Metodos
    def mostrar_paso(self):
        """Actualiza el contenido del asistente en función del paso actual"""
        # Ocultar todo
        self.inicio.hide()
        self.segunda.hide()
        self.tercera.hide()
        self.cuarta.hide()
        self.quinta.hide()
        self.back_boton.show_all()
        self.back_boton.set_sensitive(True)
        self.forward_boton.show()
        self.forward_boton.set_sensitive(False)
        self.apply_boton.hide()
        self.about_boton.hide()
        self.etapa.set_markup("<span face=\"arial\" size=\"8000\" foreground=\"chocolate\"><b>"+_('Paso %d de 5')%self.paso+"</b></span>")

        if self.paso == 1:

            self.inicio.show()
            self.labelpri.set_markup('')
            self.back_boton.hide_all()
            self.forward_boton.set_sensitive(True)

        elif self.paso == 2:

            self.segunda.show_all()
            self.labelpri.set_markup('<span face="arial" size="12000" foreground="chocolate"><b>'+_('SELECCIÓN DE USUARIO')+'</b></span>')
            if not len(self.list_users):
                #self.textbuffer.set_text(_('Buscando usuarios de Windows. Por favor espere...'))
                self.stop_boton.window.set_cursor(self.watch)
                self.hilo = threading.Thread(target=self.buscar_usuarios, args=())
                self.hilo.start()
                #self.buscar_usuarios()

        elif self.paso == 3:

            model, iter = self.users.get_selection().get_selected()
            self.selected_user = model.get_value(iter, 3)
            if self.selected_user.os.find('MS') == -1:
                self.paso = 2
                self.segunda.show()
                self.dialogo_advertencia(_("Opción no disponible actualmente. \nSeleccione otro tipo de usuario"))
                return 0
            self.imagen_usuario.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size(self.selected_user.get_avatar(), 80, 80))
            self.cuenta.set_markup('<b>%s</b>\n<i>%s</i>'% (self.selected_user.get_name(), self.selected_user.os))
            self.labelpri.set_markup('<span face="arial" size="12000" foreground="chocolate"><b>'+_('OPCIONES DE MIGRACIÓN')+'</b></span>')
            self.options.set_model( self.selected_user.get_tree_options())
            self.options.expand_row((0,1,1), True)
            #self.options.expand_all()
            self.forward_boton.set_sensitive(True)
            self.tercera.show_all()
            self.forward_boton.show_all()

        elif self.paso == 4:

            self.destino = self.entry.get_text()
            self.forward_boton.set_sensitive(True)
            if self.destino:
                f = folder(self.destino)
                if not f or not f.path:
                    self.paso = 3
                    self.tercera.show()
                    self.dialogo_advertencia(_("Ruta de destino no válida"))

                elif not f.is_writable():
                    self.paso = 3
                    self.tercera.show()
                    self.dialogo_advertencia(_("No dispone de permiso de escritura para la ubicación seleccionada"))

                elif self.available["data"] < self.required["data"]:
                    self.paso = 3
                    self.tercera.show()
                    self.dialogo_advertencia(_("Espacio en disco insuficiente.") + '\n' + _('Seleccione otra ubicación de destino o cambie sus opciones de migración'))

                elif self.available["conf"] < self.required["conf"]:
                    self.paso = 3
                    self.tercera.show()
                    self.dialogo_advertencia(_("Espacio en disco insuficiente.") + '\n' + _('Libere espacio en su carpeta personal o cambie sus opciones de migración'))

                else:
                    self.labelpri.set_markup('<span face="arial" size="12000" foreground="chocolate"><b>'+_('RESUMEN DE TAREAS')+'</b></span>')
                    self.generar_resumen(self.options.get_model())
                    self.forward_boton.hide()
                    self.apply_boton.show_all()
                    self.cuarta.show_all()
                    self.progreso.hide()
            else:
                self.paso = 3
                self.tercera.show()
                self.dialogo_advertencia(_("Introduzca una ubicación de destino"))


        elif self.paso == 5:

            self.labelpri.set_markup('<span face="arial" size="12000" foreground="chocolate"><b>'+_('DETALLES DE LA MIGRACIÓN')+'</b></span>')
            #self.quinta.show_all()
            self.cuarta.show_all()
            self.back_boton.hide_all()
            self.forward_boton.hide_all()
            time.sleep(0.2)
            self.hilo = threading.Thread(target=self.aplicar, args=())
            self.hilo.start()
        self.stop_boton.window.set_cursor(None)


    def buscar_usuarios(self):
        """Busca usuarios de otros sistemas en el ordenador"""
        gtk.gdk.threads_enter()
        self.label2.set_markup('<b>'+_("Buscando usuarios de otros sistemas...")+ '</b>')
        gtk.gdk.threads_leave()
        pc = mipc()
        pc.check_all_partitions()
        self.usuarios = {}
        wusers = pc.get_win_users()
        xusers = pc.get_lnx_users()
        musers = pc.get_mac_users()
        gtk.gdk.threads_enter()
        self.list_users.clear()
        self.users.set_model(self.list_users)
        gtk.gdk.threads_leave()
        n = 1
        options = {}
        aviso = ""

        for u, s in wusers.iteritems():
            try:
                usuario = mswin.winuser(u, pc, s)
            except:
                aviso += _("No se pudo acceder a algunos de los usuarios de Windows.") + "\n"
                continue
            else:
                self.insertar_usuario(usuario)
        for u, s in xusers.iteritems():
            try:
                usuario = openos.freeuser(u, pc, s)
            except:
                aviso += _("No se pudo acceder a algunos de los usuarios de Unix/Linux.") + "\n"
                continue
            else:
                self.insertar_usuario(usuario)
        for u, s in musers.iteritems():
            try:
                usuario = macos.macuser(u, pc, s)
            except:
                aviso += _("No se pudo acceder a algunos de los usuarios de Mac OS.") + "\n"
                continue
            else:
                self.insertar_usuario(usuario)
        if len(self.list_users) == 0:
            gtk.gdk.threads_enter()
            self.label2.set_markup('<b>'+_("No se han encontrado ningún usuario que migrar")+ '</b>' + aviso)
            gtk.gdk.threads_leave()
        else:
            gtk.gdk.threads_enter()
            self.label2.set_markup(_("Resultado de la búsqueda")+ ": "+ self.label2.get_text() + aviso)
            gtk.gdk.threads_leave()


    def main(self):
        gtk.main()


    def space_units(self, treeviewcolumn, cell_renderer, model, iter):
        size = model.get_value(iter, 2)
        if size:
            size = float(size)
        if size > 1024*1024:
            size = '%.2f GiB' % (size/(1024*1024))
        elif size > 1024:
            size = '%.2f MiB' % (size/1024)
        elif size or size == 0:
            size = '%.2f KiB' % size
        cell_renderer.set_property('text', size)

    def italic(self, treeviewcolumn, cell_renderer, model, iter):
        text = model.get_value(iter, 3)
        cell_renderer.set_property('markup', '<i>%s</i>' % text)


    def insertar_usuario(self, u):
        key = u.get_name() + " ("+ u.os +")"
        gtk.gdk.threads_enter()
        self.list_users.append([gtk.gdk.pixbuf_new_from_file_at_size(u.get_avatar(), 80 ,80), u.get_name(), u.os, u])
        if len(self.list_users) == 1:
            self.label2.set_markup('<b>'+str(len(self.list_users))+ '</b>' + ' ' + _("usuario encontrado"))
        elif len(self.list_users) > 1:
            self.label2.set_markup('<b>'+str(len(self.list_users))+ '</b>' + ' ' + _("usuarios encontrados"))
        gtk.gdk.threads_leave()


    def generar_resumen(self, model):
        """Genera el resumen de las tareas pendiente"""
        self.n_tasks = 0
        self.tasks.clear()
        iter = model.get_iter_root()
        if iter:
            self.recorrer_tareas(iter, model)
        if self.n_tasks:
            self.apply_boton.set_sensitive(True)
        else:
            self.dialogo_advertencia(_("No se seleccionado ninguna opción de migración"))
            self.apply_boton.set_sensitive(False)


    def recorrer_tareas(self, iterator, model):
        tarea = model.get_value(iterator, 4)
        if tarea and model.get_value(iterator, 1):
            self.tasks.append([model.get_value(iterator, 3),gtk.STOCK_MEDIA_PAUSE,0,_("Esperando..."), tarea])
            self.n_tasks += 1
        if model.iter_children(iterator):
            #caso recursivo
            hijas = model.iter_children(iterator)
            while hijas:
                self.recorrer_tareas(hijas, model)
                # siguiente elemento
                hijas = model.iter_next(hijas)


    def recorrer_arbol(self, iterator, model, checked):
        """Establece el valor marcado/desmarcado del padre a las opciones hijas"""
        changed = (checked != model.get_value(iterator, 1))
        #ponemos el valor a la raiz
        model.set_value(iterator, 1, checked)
        # modificamos los parametros si hay algun cambio
        if changed:
            model.set_value(iterator, 1, checked)
            task = model.get_value(iterator, 4)
            if checked:
                if task and task.size: self.required[task.type] +=  int(task.size)
            else:
                if task and task.size: self.required[task.type] -=  int(task.size)

        # si tiene filas hijas
        if model.iter_children(iterator):
            hijas = model.iter_children(iterator)
            while hijas:
                self.recorrer_arbol(hijas, model, checked)
                # siguiente elemento
                hijas = model.iter_next(hijas)


    def aplicar(self):
        """Comienza el proceso de migración"""
        task = self.tasks.get_iter_root()
        self.working = True
        self.abort = False
        self.pause = False
        while task and not self.abort:
            tarea = self.tasks.get_value(task, 4)
            if tarea:
                gtk.gdk.threads_enter()
                self.tasks.set_value(task, 1, gtk.STOCK_EXECUTE)
                por = self.progreso.get_fraction() + (1.0/(self.n_tasks+1))
                if por > 1:
                    por = 0.0
                self.progreso.set_fraction(por)
                self.progreso.set_text(_("Importando") + ' '+ tarea.description)
                self.tasks.set_value(task, 3, _("Migrando..."))
                path = self.tasks.get_path(task)
                self.resumen.set_cursor(path)
                gtk.gdk.threads_leave()
                time.sleep(0.5)
                if isinstance(tarea, copier):
                    tarea.set_destination(self.destino)
                try:
                    tarea.run(self.tasks, task)
                except:
                    print tarea.error
                gtk.gdk.threads_enter()
                if tarea.status > 0:
                    self.tasks.set_value(task, 1, gtk.STOCK_YES)
                    self.tasks.set_value(task, 2, 100.0)
                    self.tasks.set_value(task, 3, _("Completado"))
                elif tarea.status < 0:
                    self.tasks.set_value(task, 1, gtk.STOCK_NO)
                    self.tasks.set_value(task, 2, 0.0)
                    self.tasks.set_value(task, 3, _("Fallido"))
                    print tarea.error
                gtk.gdk.threads_leave()
            while self.pause:
                time.sleep(1.0)
            task = self.tasks.iter_next(task)
        time.sleep(1)
        self.working = False
        if self.abort:
            self.abort = False
            gtk.gdk.threads_enter()
            self.progreso.set_text(_("Cancelado"))
            self.stop_boton.show_all()
            self.back_boton.show_all()
            gtk.gdk.threads_leave()
        else:
            gtk.gdk.threads_enter()
            self.progreso.set_fraction(1.0)
            self.progreso.set_text(_("Finalizado"))
            self.stop_boton.hide()
            self.exit_boton.show_all()
            self.about_boton.show()
            self.dialogo_advertencia(_("Algunos cambios tendrán efecto cuando reinicie su equipo"))
            gtk.gdk.threads_leave()


def run():
    print _("Asistente de MIgración de Guadalinex")
    print '(C) 2006-2007 Fernando Ruiz Humanes, Emilia Abad Sanchez\nThis program is freely redistributable under the terms\nof the GNU General Public License.\n'
    base = Asistente()
    base.main()

if __name__ == "__main__":
    run()