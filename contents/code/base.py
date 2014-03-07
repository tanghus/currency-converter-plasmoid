# -*- coding: utf-8 -*-
# kate: space-indent on; tab-width 4; indent-width 4; indent-mode python; backspace-indents; encoding utf-8; line-numbers on; remove-trailing-space on;
#   Copyright 2009, 2010 Thomas Olsen <tanghus@gmail.com>
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

#from PyQt4.QtCore import QObject, QVariant #, SIGNAL
#from PyQt4.QtGui import *
from PyKDE4.kdecore import  KGlobal, versionString #i18n, KComponentData,
#from PyKDE4.kdeui import KIcon
#from PyKDE4.kio import KIO
#from PyKDE4.plasma import Plasma
#from PyKDE4.solid import *
from PyKDE4.plasmascript import Applet
from distutils import version
from utils import fixType
import commands

class BaseApplet(Applet):

  def __init__(self,parent,args=None):
    Applet.__init__(self, parent)

  def init(self, needsversion=None):
    print "init() in BaseApplet"
    self.setBusy(True)
    self.kdehome = unicode(KGlobal.dirs().localkdedir())
    self.metadata = self.package().metadata()
    self.show_metadata()
    #self.icon = KIcon(u"%scontents/icons/%s.png" % (self.package().path(), self.metadata.pluginName())) #.pixmap(QSize(22,22))
    self.cfg = self.config(self.metadata.pluginName())

    if needsversion is not None:
        current = version.LooseVersion(str(versionString()))
        need = version.LooseVersion(needsversion)
        if current < need:
            self.setFailedToLaunch(True, i18n("You need at least KDE SC version " + str(needsversion)))
            exit

    # Check version
    old = version.LooseVersion(fixType(self.cfg.readEntry("version", "0.0.0")))
    new = version.LooseVersion(str(self.metadata.version()))
    if old < new:
      print u"Updating from version '%s' to '%s'" % (str(old), str(new))
      self.update_version()

  def install_icons(self):
    sizes = ('16', '22', '32', '48', '64', '128')
    for size in sizes:
        out = commands.getstatusoutput("xdg-icon-resource install --noupdate --size " + size + " --context apps " + unicode(self.package().path()) + "contents/icons/%s-%s.png %s" % (self.metadata.pluginName(), size, self.metadata.pluginName()))
        if out[0] == 0:
          print u"%s-%s icon installed" % (self.metadata.pluginName(), size)
        else:
          print u"Error installing %s-%s icon. Code %d" % (self.metadata.pluginName(), size, out[0])
    #size = 'scaled'
    #cmd = "xdg-icon-resource install --noupdate --size " + size + " --context apps " + unicode(self.package().path()) + "contents/icons/%s-%s.svgz %s" % (self.metadata.pluginName(), size, self.metadata.pluginName())
    #print cmd
    # It's not possible to install svgz like this...
    #out = commands.getstatusoutput(cmd)
    #if out[0] == 0:
        #print u"%s-scaled icon installed" % (self.metadata.pluginName())
    #else:
        #print u"Error installing %s-%s icon. Code %d" % (self.metadata.pluginName(), size, out[0])
    out = commands.getstatusoutput("xdg-icon-resource forceupdate")
    if out[0] == 0:
        print "Desktop icon system updated."
    else:
        print "Error updating desktop icon system! Code:", out[0]

  def update_version(self):
    self.install_icons()
    self.cfg.writeEntry("version", self.metadata.version())

  def show_metadata(self):
    print "Name: ", self.metadata.name().toUtf8()
    print "Description: ", self.metadata.description().toUtf8()
    print "Version: ", self.metadata.version()
    print "Category: ", self.metadata.category().toUtf8()
    print "Author: ", self.metadata.author().toUtf8()
    print "Plugin name: ", self.metadata.pluginName()

