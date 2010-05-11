# -*- coding: utf-8 -*-

import os
import re
from amigu.util.folder import *
from amigu.apps.base import application
from amigu.apps.win.messenger.base import gaim
from amigu import _

class gtalk(application):
    """Clase para el manejo de cuentas de mensajería instantánea de Google Gtalk"""

    def initialize(self):
        """Personaliza los parámetros de la aplicación"""
        self.name = "Gtalk"
        self.option = self.user.get_GTALK_account()
        if not self.option:
            raise Exception
        self.name = self.option.endswith('gmail.com') and self.option or self.option + "@gmail.com"
        self.description = _("Google Talk") +": " +self.name
        self.size = 1


    def do(self, option=None):
        """Realiza el proceso de importación a Pidgin y Kopete
        
        Argumentos de entrada:
        option -> identificador de Google talk
        
        """
        self.pulse_start()
        pidgin = gaim()
        #kopte = kopete()
        if self.option:
            pidgin.config_gtalk(self.option)
            #self.update_progress(60.0)
            #kopte.config_gtalk(self.option)
        self.pulse_stop()
        return 1
