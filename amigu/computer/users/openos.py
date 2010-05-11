# -*- coding: utf-8 -*-

from amigu.computer.users.base import generic_usr
import os
from PIL import Image
from tempfile import mkstemp

class freeuser(generic_usr):
    """Clase para el manejo de usarios Unix y GNU/Linux"""
    
    def get_avatar(self):
        """Devuelve la imagen del usuario"""
        if os.path.exists(os.path.join(self.path, '.face')):
            im = Image.open(os.path.join(self.path, '.face'))
            bwim = im.convert("L")
            face = mkstemp()[1]+'.png'
            bwim.save(face)
            return face
        else:
            return "/usr/share/pixmaps/nobody.png"
