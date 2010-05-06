# -*- coding: utf-8 -*-

import gettext

gettext.bindtextdomain("amigu", "/usr/share/locale")
gettext.textdomain("amigu")
_ = gettext.gettext

__version__ = "0.7.6"
