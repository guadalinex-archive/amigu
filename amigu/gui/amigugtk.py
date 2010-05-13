#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygtk
pygtk.require('2.0')
import sys
import os
import re
import gobject
import gtk
import time
import threading
import traceback
import syslog
import shutil
import cairo
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
        self.pc = None

        self.watch = gtk.gdk.Cursor(gtk.gdk.WATCH)
        self.hilo = None

        # Usuarios
        self.list_users = gtk.ListStore(gtk.gdk.Pixbuf, gobject.TYPE_STRING, gobject.TYPE_STRING, object)
        self.users = gtk.TreeView(self.list_users)
        self.users.set_rules_hint(True)
        self.users.connect("cursor-changed", self.marcar_usuario)
        rndr = gtk.CellRendererText()
        rndr2 = gtk.CellRendererText()
        rndr3 = gtk.CellRendererText()
        rndr_pixbuf = gtk.CellRendererPixbuf()
        rndr_pixbuf.set_property("stock-size",3)
        rndr_pixbuf.set_property('xalign', 0.5)
        rndr_pixbuf.set_property('width', 100)
        rndr_pixbuf.set_property('ypad', 5)
        column1 = gtk.TreeViewColumn(_("Cuenta"), rndr3, text=1)
        rndr3.set_property('scale', 1.5)
        rndr3.set_property('width', 300)
        column2 = gtk.TreeViewColumn(_("Sistema Operativo"), rndr, text=2)
        column3 = gtk.TreeViewColumn(_("Imagen"), rndr_pixbuf, pixbuf=0)
        self.users.append_column( column3 )
        self.users.append_column( column1 )
        self.users.append_column( column2 )
        self.users.expand_all()

        # Opciones
        self.options = gtk.TreeView()
        rndr1 = gtk.CellRendererToggle()
        rndr1.set_property('activatable', True)
        rndr1.connect( 'toggled', self.marcar_opcion)
        column4 = gtk.TreeViewColumn(_("Opción"), rndr, text=0)
        column5 = gtk.TreeViewColumn(_("Tamaño"), rndr2, text=2)
        rndr2.set_property('xalign', 1.0)
        column5.set_cell_data_func(rndr2, self.space_units, data=None)

        column6 = gtk.TreeViewColumn(_("Descripción"), rndr, text=3)
        column6.set_cell_data_func(rndr, self.italic, data=None)
        column7 = gtk.TreeViewColumn(_("Migrar"), rndr1 )
        column7.add_attribute( rndr1, "active", 1)
        self.options.append_column( column4 )
        self.options.append_column( column7 )
        self.options.append_column( column5 )
        self.options.append_column( column6 )

        #Resumen
        self.tasks = gtk.ListStore( gobject.TYPE_STRING, gobject.TYPE_STRING, gobject.TYPE_FLOAT, gobject.TYPE_STRING, gobject.TYPE_INT, object)
        self.resumen = gtk.TreeView(self.tasks)
        column8 = gtk.TreeViewColumn(_("Tarea"), rndr, text=0)
        column9 = gtk.TreeViewColumn("", rndr_pixbuf, stock_id=1)
        progressrenderer = gtk.CellRendererProgress()
        column10 = gtk.TreeViewColumn(_("Progreso"), progressrenderer, value=2, text=3, pulse=4)
        progressrenderer.set_property('height', 10)
        self.resumen.append_column( column9 )
        self.resumen.append_column( column8 )
        self.resumen.append_column( column10 )


        gtk.about_dialog_set_url_hook(self.open_url, self.url)

        # ventana box_principal
        box_principal = gtk.VBox(False, 0)#Creo la caja vertical box_principal
        # Etapas o Stages
        self.box_inicial = gtk.VBox(False, 1)
        self.box_usuarios = gtk.VBox(False, 1)
        self.box_opciones = gtk.HBox(False, 1)
        self.box_migracion = gtk.VBox(False, 1)
        
        separador1 = gtk.HSeparator()
        separador2 = gtk.HSeparator()
        
        
        box_statico_sup = gtk.HBox(False, 1)#Creo lo que se va a quedar siempre en la ventana
        box_variable = gtk.VBox(False, 1)#Creo lo que va a ir variando
        box_statico_inf = gtk.HBox(False, 1)#Creo lo que se va a quedar siempre en la ventana
        box_statico_infver1 = gtk.HBox(False, 1)
        box_statico_infver2 = gtk.HButtonBox()
        box_statico_infver2.set_layout(gtk.BUTTONBOX_END)
        box_statico_infver2.set_size_request(550,60)
        box_statico_infver2.set_border_width(10)
        image = gtk.Image()
        image.set_from_file(os.path.join(dir_imagenes, "cab_amigu.png"))

        image1 = gtk.Image()
        image1.set_from_file(os.path.join(dir_imagenes, "icon_paginacion.png"))

        self.etapa = gtk.Label()
        self.etapa.set_use_markup(True)
        self.etapa.set_markup("<span face = \"arial\" size = \"8000\" foreground = \"chocolate\"><b>Paso %d de 5</b></span>"%self.paso)

        espacio = gtk.Label()

        # botones
        self.stop_boton = gtk.Button(stock = gtk.STOCK_CANCEL)
        self.back_boton = gtk.Button(stock = gtk.STOCK_GO_BACK)
        self.forward_boton = gtk.Button(stock = gtk.STOCK_GO_FORWARD)
        self.apply_boton = gtk.Button(stock = gtk.STOCK_APPLY)
        self.exit_boton = gtk.Button(stock = gtk.STOCK_QUIT)
        self.about_boton = gtk.Button(label=_("Acerca de"))
        self.jump_boton = gtk.Button(label=_("Omitir"))


        # añadir
        self.labelpri = gtk.Label("")
        self.labelpri.set_line_wrap(True)
        self.labelpri.set_justify(gtk.JUSTIFY_LEFT)
        self.labelpri.set_use_markup(True)
        

        box_statico_sup.pack_start(self.labelpri, False, False, 10)
        box_variable.pack_start(self.box_inicial, True, False, 0)
        box_statico_inf.pack_start(box_statico_infver1, False, False, 0)
        box_statico_inf.pack_start(box_statico_infver2, True, False, 0)

        box_statico_infver1.pack_start(image1, True, True, 10)
        box_statico_infver1.pack_start(self.etapa, False, False, 1)
        box_statico_infver2.pack_start(self.about_boton, False, False, 0)
        box_statico_infver2.pack_start(self.back_boton, False, False, 0)
        box_statico_infver2.pack_start(self.forward_boton, False, False, 0)
        box_statico_infver2.pack_start(self.apply_boton, False, False, 0)
        box_statico_infver2.pack_start(espacio, True, True, 2)
        box_statico_infver2.pack_start(self.exit_boton, False, False, 0)
        box_statico_infver2.pack_start(self.jump_boton, False, False, 0)
        box_statico_infver2.pack_start(self.stop_boton, True, False, 5)
        box_principal.pack_start(image, False, False, 0)
        box_principal.pack_start(separador1, False, True, 10)
        box_principal.pack_start(box_statico_sup, False, False, 1)
        box_principal.pack_start(box_variable, True, True, 1)
        box_principal.pack_start(separador2, False, True, 10)
        box_principal.pack_start(box_statico_inf, False, True, 1)
        box_variable.pack_start(self.box_usuarios, True, True, 1)
        box_variable.pack_start(self.box_opciones, True, True, 1)
        box_variable.pack_start(self.box_migracion, True, True, 1)
        self.window.add(box_principal)#Añado a la ventana el box_principal

        # eventos
        self.back_boton.connect("clicked", self.etapa_anterior)
        self.forward_boton.connect("clicked", self.etapa_siguiente)
        self.apply_boton.connect("clicked", self.dialogo_confirmacion)
        self.exit_boton.connect("clicked", self.destroy)
        self.stop_boton.connect_object("clicked", self.dialogo_cancelacion, self.window)
        self.about_boton.connect_object("clicked", self.about, self.window)
        self.jump_boton.connect_object("clicked", self.omitir, self.window)

        # mostrar ventana
        self.window.show_all()
        self.apply_boton.hide()
        self.exit_boton.hide()
        self.jump_boton.hide()


################Primera Ventana

        # crear
        label1 = gtk.Label()
        label1.set_use_markup(True)
        label1.set_line_wrap(True)
        label1.set_justify(gtk.JUSTIFY_CENTER)
        label1.set_markup('<b>'+_('Bienvenido al Asistente de MIgración de GUadalinex - AMIGU') + '\n\n' + _('Este asistente le guiará durante el proceso de migración de sus documentos y configuraciones de su sistema operativo Windows.') + '\n' + _('Pulse el botón Adelante para comenzar.') + '</b>')

        # añadir
        self.box_inicial.pack_start(label1, True, True, 10)

        # mostrar
        self.back_boton.hide_all()
        self.box_inicial.show_all()


################Segunda Ventana

        #crear
        self.box_usuarioshor1 = gtk.HBox(False, 1)
        self.box_usuarioshor2 = gtk.HBox(True, 10)
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
        self.box_usuarioshor1.pack_start(self.label2, False, False, 10)
        self.box_usuarioshor2.pack_start(frame1, True, True, 10)
        self.box_usuarios.pack_start(self.box_usuarioshor2, True, True, 1)
        self.box_usuarios.pack_start(self.box_usuarioshor1, False, False, 1)



###############################Tercera Ventana

        # crear
        self.box_opcionesver1 = gtk.HBox(False, 10)
        self.box_opcionesver2 = gtk.HBox(False, 5)
        self.box_opcionesver3 = gtk.HBox(False, 10)
        self.box_opcionesver4 = gtk.HBox(False, 10)
        
        self.box_opcioneshor1 = gtk.VBox(False, 3)
        self.box_opcioneshor2 = gtk.VBox(False, 10)
        self.box_opcioneshor3 = gtk.VBox(False, 5)
        self.box_opcioneshor4 = gtk.VBox(False, 5)
        self.box_opcioneshor5 = gtk.VBox(False, 5)
        self.box_opcioneshor6 = gtk.VBox(False, 5)
        self.frame4 = gtk.Frame(_("Cuenta"))
        frame2 = gtk.Frame(_("Espacio requerido"))
        self.entry = gtk.Entry()
        self.entry.set_max_length(50)
        f = folder(os.path.expanduser('~'))
        self.required = {'data':0, 'conf':0}
        self.available = {'data':f.get_free_space(), 'conf':f.get_free_space()}

        self.cuenta = gtk.Label()
        self.cuenta.set_use_markup(True)
        

        self.datos = SpaceIndicator(self.window)
        self.configuraciones = SpaceIndicator(self.window)

        self.entry.connect("activate", self.actualizar_espacio)
        self.entry.set_text(f.get_path())
        self.actualizar_espacio()

        boton22 = gtk.Button(label = _("Seleccionar otra carpeta"), stock = None)
        boton22.connect_object("clicked", self.buscar, self.window)
        #tip22 = gtk.Tooltip(boton22)
        #tip22.set_text(_("Elija la carpeta Destino donde quiere guardar los archivos"))

        frame5 = gtk.Frame(_("Opciones de migración"))
        self.arbol_inicializado = False
        self.imagen_usuario = gtk.Image()

        self.sw3 = gtk.ScrolledWindow()
        self.sw3.set_size_request(280, 200)
        self.sw3.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.sw3.add(self.options)

        # añadir
        self.box_opciones.pack_start(self.box_opcionesver1, False, False, 0)
        self.box_opciones.pack_start(frame5, True, True, 0)
        self.box_opcionesver1.pack_start(self.box_opcioneshor2, False, False, 10)
        self.box_opcionesver2.pack_start(self.imagen_usuario, True, True, 5)
        self.box_opcionesver2.pack_start(self.cuenta, True, True, 5)
        frame5.add(self.sw3)
        self.frame4.add(self.box_opcionesver2)
        frame2.add(self.box_opcioneshor1)

        self.box_opcioneshor1.pack_start(gtk.Label(_('Datos de usuario')), True, True, 0)
        self.box_opcioneshor1.pack_start(self.datos, True, True, 0)

        self.box_opcioneshor1.pack_start(self.entry, True, False, 0)
        self.box_opcioneshor1.pack_start(boton22, True, False, 0)
        self.box_opcioneshor1.pack_start(gtk.HSeparator(), True, False, 0)
        self.box_opcioneshor1.pack_start(gtk.Label(_('Configuraciones')), True, True, 0)
        self.box_opcioneshor1.pack_start(self.configuraciones, True, True, 0)
        self.box_opcioneshor2.pack_start(self.frame4, True, False, 0)
        self.box_opcioneshor2.pack_start(frame2, True, False, 0)


################Cuarta Ventana

        # crear
        self.box_migracionhor1 = gtk.HBox(False, 10)
        frame3 = gtk.Frame(_("Tareas a realizar"))
        sw1 = gtk.ScrolledWindow()
        sw1.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw1.set_size_request(600, 225)
        self.progreso = gtk.ProgressBar(None)
        self.progreso.set_fraction(0.0)
        self.progreso.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
        self.progreso.set_text(_("Realizando las tareas solicitadas..."))

        #añadir
        self.box_migracion.pack_start(self.box_migracionhor1, True, True, 0)
        self.box_migracionhor1.pack_start(frame3, True, True, 10)
        frame3.add(sw1)
        sw1.add(self.resumen)
        #self.box_migracion.pack_start(gtk.Label(_("Estado del proceso de migración")), True, False, 2)
        self.box_migracion.pack_start(self.progreso, False, False, 9)

        try:
            child = gtk.EventBox()
            b =  gtk.LinkButton(self.url, label=_("Más información sobre Amigu"))
            child.add(b)
            text_view.add_child_in_window(child, gtk.TEXT_WINDOW_TEXT, 480, 173)
        except:
            pass

        self.window.set_focus(self.forward_boton)

########Cuadros de dialogo

    def about(self, widget):
        dialog = gtk.AboutDialog()
        dialog.set_name("AMIGU")
        dialog.set_version(ver)
        dialog.set_copyright("Copyright © 2006-2010 Junta de Andalucía")
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


    def dialogo_advertencia(self, mensaje = "", progreso=False):
        """Muestra mensajes de aviso"""
        # crear
        self.advertencia = gtk.Dialog(_("Aviso"), self.window, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                     (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        
        h1 = gtk.HBox(False, 10)

        # añadir
        self.advertencia.vbox.pack_start(h1, True, False, 10)
        if progreso:
            self.progreso2 = gtk.ProgressBar(None)
            self.progreso2.pulse()
            self.advertencia.vbox.pack_start(self.progreso2, True, False, 1)
            stock = gtk.STOCK_EXECUTE
            self.wait = True
            hilo2 = threading.Thread(target=self.pulse, args=())
            hilo2.start()
        else:
            stock = gtk.STOCK_DIALOG_WARNING
        logoad = gtk.Image()
        logoad.set_from_stock(stock, 6)
        iconad = self.advertencia.render_icon(stock, 1)
        self.advertencia.set_icon(iconad)
        mensaje = gtk.Label(mensaje)
        h1.pack_start(logoad, True, False, 10)
        h1.pack_start(mensaje, True, False, 10)
        self.advertencia.show_all()
        self.advertencia.set_default_response(gtk.RESPONSE_ACCEPT)
        r = self.advertencia.run()
        self.advertencia.destroy()
        self.advertencia = None
        self.wait = False



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

    def omitir(self, widget, data=None):
        """Aborta la tarea actual pero no el proceso de migración"""
        if self.working:
            self.jump_boton.set_sensitive(False)
            self.tarea.cancel()
            return 0

    def destroy(self, widget, data=None):
        """Finaliza la ejecución del asistente y limpiar los archivos temporales"""
        if self.working:
            self.abort = True
            self.tarea.cancel()
            self.pause = False
            return 0
        print _("Saliendo del asistente")
        iter = self.list_users.get_iter_root()
        model = self.users.get_model()
        while iter:
            print _("Eliminando archivos temporales...")
            model.get_value(iter, 3).clean()
            iter = self.list_users.iter_next(iter)
            
        if self.pc:
            print _("Desmontando particiones...")
            self.pc.umount_all_partitions()
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
        self.window.set_focus(self.forward_boton)


    def actualizar_espacio(self, widget=None, other=None):
        """Actualiza el espacio libre en disco"""
        destino = self.entry.get_text()
        if os.path.exists(destino):
            d = folder(destino)
            self.available["data"] = d.get_free_space()
        #self.datos_libre.set_markup("<i>%dKiB</i>" % self.available["data"])
        #self.conf_libre.set_markup("<i>%dKiB</i>" % self.available["conf"])
        #self.datos_req.set_markup("<i>%dKiB</i>" % self.required["data"])
        #self.conf_req.set_markup("<i>%dKiB</i>" % self.required["conf"])
        self.datos.update_values(self.required["data"], self.available["data"])
        self.configuraciones.update_values(self.required["conf"], self.available["conf"])
        self.datos.queue_draw()
        self.configuraciones.queue_draw()


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
        self.box_inicial.hide()
        self.box_usuarios.hide()
        self.box_opciones.hide()
        self.box_migracion.hide()
        self.back_boton.show_all()
        self.back_boton.set_sensitive(True)
        self.forward_boton.show()
        self.forward_boton.set_sensitive(False)
        self.apply_boton.hide()
        self.jump_boton.hide()
        self.about_boton.hide()
        self.etapa.set_markup("<span face=\"arial\" size=\"8000\" foreground=\"chocolate\"><b>"+_('Paso %d de 5')%self.paso+"</b></span>")

        if self.paso == 1:

            self.box_inicial.show()
            self.labelpri.set_markup('')
            self.back_boton.hide_all()
            self.forward_boton.set_sensitive(True)

        elif self.paso == 2:

            self.box_usuarios.show_all()
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
            if self.selected_user.os.find('Windows') == -1:
                self.paso = 2
                self.box_usuarios.show()
                self.dialogo_advertencia(_("Opción no disponible actualmente. \nSeleccione otro tipo de usuario"))
                return 0
            self.imagen_usuario.set_from_pixbuf(gtk.gdk.pixbuf_new_from_file_at_size(self.selected_user.get_avatar(), 80, 80))
            self.cuenta.set_markup('<b>%s</b>\n<span face="arial" size="8000"><i>%s</i></span>'% (self.selected_user.get_name(), self.selected_user.os))
            self.labelpri.set_markup('<span face="arial" size="12000" foreground="chocolate"><b>'+_('OPCIONES DE MIGRACIÓN')+'</b></span>')
            #self.options.set_model(self.selected_user.get_tree_options())
            
            self.options.set_model(None)
            self.hilo = threading.Thread(target=self.load_options, args=())
            self.hilo.start()
            
            self.box_opciones.show_all()
            self.forward_boton.show_all()
            self.dialogo_advertencia(_("Analizando usuario..."),True)

        elif self.paso == 4:

            self.destino = self.entry.get_text()
            self.forward_boton.set_sensitive(True)
            if self.destino:
                f = folder(self.destino)
                if not f or not f.path:
                    self.paso = 3
                    self.box_opciones.show()
                    self.dialogo_advertencia(_("Ruta de destino no válida"))

                elif not f.is_writable():
                    self.paso = 3
                    self.box_opciones.show()
                    self.dialogo_advertencia(_("No dispone de permiso de escritura para la ubicación seleccionada"))

                elif self.available["data"] < self.required["data"]:
                    self.paso = 3
                    self.box_opciones.show()
                    self.dialogo_advertencia(_("Espacio en disco insuficiente.") + '\n' + _('Seleccione otra ubicación de destino o cambie sus opciones de migración'))

                elif self.available["conf"] < self.required["conf"]:
                    self.paso = 3
                    self.box_opciones.show()
                    self.dialogo_advertencia(_("Espacio en disco insuficiente.") + '\n' + _('Libere espacio en su carpeta personal o cambie sus opciones de migración'))

                else:
                    self.labelpri.set_markup('<span face="arial" size="12000" foreground="chocolate"><b>'+_('RESUMEN DE TAREAS')+'</b></span>')
                    self.generar_resumen(self.options.get_model())
                    self.forward_boton.hide()
                    self.apply_boton.show_all()
                    self.box_migracion.show_all()
                    self.progreso.hide()
                    self.window.set_focus(self.apply_boton)
            else:
                self.paso = 3
                self.box_opciones.show()
                self.dialogo_advertencia(_("Introduzca una ubicación de destino"))


        elif self.paso == 5:

            self.labelpri.set_markup('<span face="arial" size="12000" foreground="chocolate"><b>'+_('DETALLES DE LA MIGRACIÓN')+'</b></span>')
            self.box_migracion.show_all()
            self.back_boton.hide_all()
            self.forward_boton.hide_all()
            time.sleep(0.2)
            self.hilo = threading.Thread(target=self.aplicar, args=())
            self.hilo.start()
        self.stop_boton.window.set_cursor(None)

    def pulse(self):
        while self.wait:
            gtk.gdk.threads_enter()
            self.progreso2.pulse()
            gtk.gdk.threads_leave()
            time.sleep(0.15)

    def load_options(self):
        tree_options = self.selected_user.get_tree_options()
        gtk.gdk.threads_enter()
        try:
            self.advertencia.response(gtk.RESPONSE_CLOSE)
        except:
            pass
        else:
            self.options.set_model(tree_options)
            self.options.expand_all()
            self.forward_boton.set_sensitive(True)
        gtk.gdk.threads_leave()
        self.wait = False

    def buscar_usuarios(self):
        """Busca usuarios de otros sistemas en el ordenador"""
        gtk.gdk.threads_enter()
        self.label2.set_markup('<b>'+_("Buscando usuarios de otros sistemas...")+ '</b>')
        gtk.gdk.threads_leave()
        self.pc = mipc()
        self.pc.check_all_partitions()
        self.usuarios = {}
        wusers = self.pc.get_win_users()
        xusers = self.pc.get_lnx_users()
        musers = self.pc.get_mac_users()
        gtk.gdk.threads_enter()
        self.list_users.clear()
        self.users.set_model(self.list_users)
        gtk.gdk.threads_leave()
        n = 1
        options = {}
        aviso = ""

        for u, s in wusers.iteritems():
            try:
                usuario = mswin.winuser(u, self.pc, s)
            except:
                aviso += _("No se pudo acceder a algunos de los usuarios de Windows.") + "\n"
                continue
            else:
                self.insertar_usuario(usuario)
        for u, s in xusers.iteritems():
            try:
                usuario = openos.freeuser(u, self.pc, s)
            except:
                aviso += _("No se pudo acceder a algunos de los usuarios de Unix/Linux.") + "\n"
                continue
            else:
                self.insertar_usuario(usuario)
        for u, s in musers.iteritems():
            try:
                usuario = macos.macuser(u, self.pc, s)
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
            self.tasks.append([model.get_value(iterator, 3),gtk.STOCK_MEDIA_PAUSE,0,_("Esperando..."), -1, tarea])
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
        self.jump_boton.show_all()
        self.progreso.set_fraction(0)
        while task and not self.abort:
            self.tarea = self.tasks.get_value(task, 5)
            if self.tarea:
                gtk.gdk.threads_enter()
                self.jump_boton.set_sensitive(True)
                self.tasks.set_value(task, 1, gtk.STOCK_EXECUTE)
                por = self.progreso.get_fraction() + (1.0/(self.n_tasks+1))
                if por > 1:
                    por = 0.0
                self.progreso.set_fraction(por)
                self.progreso.set_text(_("Importando") + ' '+ self.tarea.description)
                if self.tarea.size > 102400:
                    self.tasks.set_value(task, 3, _("Migrando...(Puede llevar algún rato)"))
                elif self.tarea.size > 1024000:
                    self.tasks.set_value(task, 3, _("Migrando...(Tenga paciencia)"))
                else:
                    self.tasks.set_value(task, 3, _("Migrando..."))
                path = self.tasks.get_path(task)
                self.resumen.set_cursor(path)
                gtk.gdk.threads_leave()
                time.sleep(0.5)
                if isinstance(self.tarea, copier) or isinstance(self.tarea, converter):
                    self.tarea.set_destination(self.destino)
                try:
                    self.tarea.run(self.tasks, task)
                except:
                    print self.tarea.error
                gtk.gdk.threads_enter()
                if self.tarea.status > 0:
                    self.tasks.set_value(task, 1, gtk.STOCK_YES)
                    self.tasks.set_value(task, 2, 100.0)
                    self.tasks.set_value(task, 3, _("Completado"))
                elif self.tarea.status < 0:
                    self.tasks.set_value(task, 1, gtk.STOCK_NO)
                    self.tasks.set_value(task, 2, 0.0)
                    self.tasks.set_value(task, 3, _("Fallido"))
                elif self.tarea.status == 0:
                    self.tasks.set_value(task, 1, gtk.STOCK_NO)
                    self.tasks.set_value(task, 2, 0.0)
                    self.tasks.set_value(task, 3, _("Abortado"))
                self.tasks.set_value(task, 4, -1)
                gtk.gdk.threads_leave()
                print self.tarea.error
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
            self.jump_boton.hide()
            gtk.gdk.threads_leave()
        else:
            gtk.gdk.threads_enter()
            self.progreso.set_fraction(1.0)
            self.progreso.set_text(_("Finalizado"))
            self.stop_boton.hide()
            self.exit_boton.show_all()
            self.about_boton.show()
            self.jump_boton.hide()
            #self.dialogo_advertencia(_("Algunos cambios tendrán efecto cuando reinicie su equipo"))
            gtk.gdk.threads_leave()
            

class SpaceIndicator(gtk.DrawingArea):

    def __init__(self, parent):
        self.par = parent
        super(SpaceIndicator, self).__init__()
        self.set_size_request(-1, 30)
        self.connect("expose-event", self.expose)
        self.ticks = 4
        self.offset = 25
    

    def expose(self, widget, event):
        
        cr = self.window.cairo_create()
        
        cr.set_line_width(0.8)

        cr.select_font_face("Sans", 
            cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(11)

        width = self.allocation.width - (2 * self.offset)
     
        #self.cur_width = self.par.get_cur_value()
        #self.max_width = self.par.get_max_value()
        
        step = round(width / float(self.ticks))

        till = (width / self.max_width) * self.cur_width
        full = (width / (self.cur_width+1)) * self.max_width
        
        if (self.cur_width >= self.max_width):
            
            needed = self.cur_width
            linear = cairo.LinearGradient(self.offset, 0.0, full+self.offset, 30.0)          #gradient
            linear.add_color_stop_rgb(0.0,  0, 1, 0)                  #gradient
            linear.add_color_stop_rgb(0.75,  0, 1, 0)                  #gradient
            linear.add_color_stop_rgb(0.9,  1, 1, 0)                #gradient
            linear.add_color_stop_rgb(1.0,  1, 0, 0)   

            cr.set_source(linear)
            cr.rectangle(self.offset, 0, full, 10)
            cr.fill ()

            cr.set_source_rgb(1.0, 0.0, 0.0)
            cr.rectangle(full+self.offset, 0, till-full-self.offset, 10)
            cr.fill ()

        else: 
        
            needed = self.max_width
            cr.set_source_rgb(0.7, 0.7, 0.7)
            cr.rectangle(self.offset, 0, width, 10)
            cr.fill ()
            
            linear = cairo.LinearGradient(self.offset, 0.0, width+self.offset, 30.0)          #gradient
            linear.add_color_stop_rgb(0.0,  0, 1, 0)                  #gradient
            linear.add_color_stop_rgb(0.75,  0, 1, 0)                #gradient
            linear.add_color_stop_rgb(0.9,  1, 1, 0)                #gradient
            linear.add_color_stop_rgb(1.0,  1, 0, 0)   
            
            cr.set_source(linear)            
            cr.rectangle(self.offset, 0, till, 10)
            cr.fill ()
       
        
        cr.set_source_rgb(0.35, 0.31, 0.24)
        self.num = range(0, int(needed*(1+1.0/self.ticks)), int(needed/self.ticks))
        for i in range(0, len(self.num)):
            cr.move_to(self.offset+i*step, 0)
            cr.line_to(self.offset+i*step, 10)
            cr.stroke()
            
            if i > 0:
                cr.move_to(self.offset+i*step-step/2, 0)
                cr.line_to(self.offset+i*step-step/2, 5)
                cr.stroke()
            
            label = adjust_units(self.num[i])
            (x, y, width, height, dx, dy) = cr.text_extents(label)
            cr.move_to(self.offset+i*step-width/2, 20)
            cr.text_path(label)
            cr.stroke()
            
    def update_values(self, cur, max):
        self.cur_width = float(cur)
        self.max_width = float(max)
        self.queue_draw()
        

def adjust_units(size):
    if size is None:
        return None
    size = float(size)
    if size > 1024*1024:
        size = '%.1fG' % (round(size/(1024*1024), 1))
    elif size > 1024:
        size = '%dM' % (round(size/1024))
    elif size or size == 0:
        size = '%dK' % round(size)
    return size

def run():
    print _("Asistente de MIgración de Guadalinex")
    print '(C) 2006-2010 Fernando Ruiz Humanes, Emilia Abad Sanchez\nThis program is freely redistributable under the terms\nof the GNU General Public License.\n'
    base = Asistente()
    base.main()

if __name__ == "__main__":
    run()
