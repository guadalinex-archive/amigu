# -*- coding: utf-8 -*-

import os
import re
from amigu.util.folder import *
from amigu.apps.base import application
from amigu.apps.win.messenger.base import gaim
from amigu import _


class windowslive(application):
    """Clase para el manejo de cuentas de mensajería instantánea de Windows
        Programas:
         * Windows Messenger
         * MSN Messenger
         * Live Messenger
    """

    def initialize(self):
        """Personaliza los parámetro de la aplicación"""
        self.name = "Windows Live Messenger"
        if not self.option:
            raise Exception
        self.name = self.option
        self.description = _("Windows Live ID") +": " +self.name
        self.size = 1

    def do(self):
        """Realiza el proceso de importación a Pidgin, Kopete y amsn"""
        self.pulse_start()
        pidgin = gaim()
        #kopte = kopete()
        #self.update_progress(35.0)
        if self.option:
            pidgin.config_msn(self.option)
            #self.update_progress(60.0)
            #kopte.config_msn(self.option)
        self.pulse_stop()
        return 1
