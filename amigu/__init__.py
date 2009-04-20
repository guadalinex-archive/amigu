# -*- coding: utf-8 -*-

import gettext

_ = gettext.gettext
gettext.textdomain("amigu")
gettext.bindtextdomain("amigu", "/usr/share/locale")

__version__ = "0.7.2"
