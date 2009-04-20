# -*- coding: utf-8 -*-

from amigu.computer.users.base import generic_usr
import os

class freeuser(generic_usr):
    """Clase para el manejo de usarios Unix y GNU/Linux"""
    def get_avatar(self):
        if os.path.exists(os.path.join(self.path, '.face')):
            return os.path.join(self.path, '.face')
        else:
            return "/usr/share/pixmaps/nobody.png"
