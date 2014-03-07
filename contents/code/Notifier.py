# -*- coding: utf-8 -*-
# kate: space-indent on; tab-width 4; indent-width 4; indent-mode python; backspace-indents; encoding utf-8; line-numbers on; remove-trailing-space on;
#   Copyright 2010 Thomas Olsen <tanghus@gmail.com>
#
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Library General Public License as
#   published by the Free Software Foundation; either version 2 or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#
#   GNU General Public License for more details
#
#
#   You should have received a copy of the GNU Library General Public
#   License along with this program; if not, write to the
#   Free Software Foundation, Inc.,
#
#   51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#

from PyQt4 import QtCore
from PyQt4.QtGui import QPixmap
from PyKDE4.kdecore import i18n, KComponentData, KGlobal
from PyKDE4.kdeui import KNotification
import sys, os, shutil
from utils import createDirectory

class Notifier(QtCore.QObject):

    def __init__(self, parent):
        QtCore.QObject.__init__(self)
        self.applet = parent
        self.kdehome = unicode(KGlobal.dirs().localkdedir())
        if not os.path.exists(self.kdehome+u"share/apps/%s/%s.notifyrc" % (self.applet.metadata.pluginName(), self.applet.metadata.pluginName())):
            # Install notifyrc file if required
            self.install_notifications()

    def notify(self, strType, msg=""):
        KNotification.event(strType,
            msg,
            QPixmap(), #self.icon.pixmap(QSize(22,22)), #KIcon("google-translator").pixmap(QSize(22,22))
            None,
            KNotification.CloseOnTimeout,
            KComponentData(str(self.applet.metadata.pluginName()), str(self.applet.metadata.pluginName()), KComponentData.SkipMainComponentRegistration)
            )

    def install_notifications(self):
        src = u"%scontents/%s.notifyrc" % (self.applet.package().path(), self.applet.metadata.pluginName())
        dst = self.kdehome+"share/apps/%s/%s.notifyrc" % (self.applet.metadata.pluginName(), self.applet.metadata.pluginName())
        print u"Installing %s to %s" % (src, dst)
        if os.path.exists(self.kdehome+"share/apps"):
            createDirectory(self.kdehome+"share/apps/%s" % self.applet.metadata.pluginName())
            try:
                shutil.copy(src, dst)
            except IOError as (errno, strerror):
                print "I/O error({0}): {1}".format(errno, strerror)
                print "Problem writing to file: %s" % dst
            except:
                print "Problem writing to file: %s" % dst
                print "Unexpected error:", sys.exc_info()[0]
                #self.setFailedToLaunch(True, "Unable to install notification configuration file '%s'" % dst)

        else:
            self.applet.setFailedToLaunch(True, i18n("KDE directory '%s' doesn't exist!") % self.kdehome+"share/apps")



