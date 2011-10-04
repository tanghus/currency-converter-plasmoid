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

from PyQt4 import QtCore
from PyQt4.QtCore import pyqtSlot, QVariant, SIGNAL
from PyQt4.QtGui import QWidget, QAction
from PyKDE4.kdecore import KGlobal, i18n, i18nc
from PyKDE4.kdeui import KIcon, KDialog
from PyKDE4.kio import KIO
from PyKDE4.kutils import *
from PyKDE4.plasma import Plasma
from CurrencyConverter import CurrencyConverter
from NetworkMonitor import NetworkMonitor
from Notifier import Notifier
from currency_converter_config_ui import *
#from currencies import *
import base
import PyKDE4.pykdeconfig

class CurrencyConverterConfig(QWidget,Ui_CurrencyConverterConfig):
    def __init__(self,parent):
        QWidget.__init__(self,parent)
        self.setupUi(self)
        #self.connect(self.localTimeZone, SIGNAL("stateChanged(int)"), self, SLOT("slotLocalTimeZoneToggled(int)"))

class CurrencyConverterApplet(base.BaseApplet):

    def __init__(self,parent,args=None):
        base.BaseApplet.__init__(self,parent)

    def init(self):
        base.BaseApplet.init(self, needsversion="4.5")
        if self.hasFailedToLaunch():
            return

        KGlobal.locale().insertCatalog(self.metadata.pluginName())
        lang = KGlobal.locale().language()
        print "Language:", lang
        print "Translated?", KGlobal.locale().isApplicationTranslatedInto(lang)

        self._widget = None
        self.dialog = None
        self.has_tooltip = False
        self.setHasConfigurationInterface(True)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)

        self.notifier = Notifier(self)
        self.nwmon = NetworkMonitor()
        if self.nwmon.connected():
            self.setBusy(False)
        else:
            self.notifier.notify("waiting-for-network", i18n("Waiting for network connection."))

        self.nwmon.status_changed.connect(self.netstate_changed)

        # Main widget
        print("CurrencyConverterApplet: Creating main widget.")
        self._widget = CurrencyConverter(self)
        self._widget.init()
        self.setGraphicsWidget(self._widget)
        self.setPopupIcon(self.metadata.pluginName())

        self.setGraphicsWidget(self._widget)

        #self.setup_tooltip()

        self.configChanged()
        self._widget.updated.connect(self.setup_tooltip)

    def createConfigurationInterface(self, dialog):

        self.ui = CurrencyConverterConfig(self.dialog)
        p = dialog.addPage(self.ui, i18n("General") )
        p.setIcon( KIcon("currency-converter") )

        #self.notify_widget = KCModuleProxy("kcmnotify", dialog, ["currency-converter",])
        #real_module = self.notify_widget.realModule()
        ##print "Module:", real_module
        #p = dialog.addPage(self.notify_widget, i18n("Notifications") )
        #p.setIcon( KIcon("dialog-information") )

        dialog.setButtons(KDialog.ButtonCodes(KDialog.ButtonCode(KDialog.Ok | KDialog.Cancel | KDialog.Apply)))
        dialog.showButton(KDialog.Apply, False)

        #self.connect(dialog, SIGNAL("applyClicked()"), self, SLOT("configAccepted()"))
        #self.connect(dialog, SIGNAL("okClicked()"), self, SLOT("configAccepted()"))
        dialog.applyClicked.connect(self.configAccepted)
        dialog.okClicked.connect(self.configAccepted)

        self.ui.update_interval.setValue(self._widget.update_interval)

    #@pyqtSignature("configAccepted()")
    @pyqtSlot(name="configAccepted")
    def configAccepted(self):
        print "CurrencyConverterApplet::configAccepted"

        self._widget.update_interval = self.ui.update_interval.value()
        self.cfg.writeEntry("update_interval", QVariant(self._widget.update_interval))
        self.constraintsEvent(Plasma.SizeConstraint)
        self.update()
        self._widget.start_timer()
        self.emit(SIGNAL("configNeedsSaving()"))
        #self.configNeedsSaving.emit()

    def contextualActions(self):
        # Add custom context menus
        print "CurrencyConverterApplet::contextualActions"
        actions = []
        ac_update = QAction(KIcon("view-refresh"), i18n("Update now"), self)
        #checkNow = QAction(KIcon(self.package().path() + "contents/icons/check.svg"), "Check email now", self)
        #self.connect(ac_update, SIGNAL("triggered()"), self._widget.do_convert)
        if hasattr(self, '_widget') and self._widget is not None:
            ac_update.triggered.connect(self._widget.do_convert)
            actions.append(ac_update)
        print actions
        return actions

    # Never called..?
    def updateToolTipContent(self):
        print "CurrencyConverterApplet::updateToolTipContent"

    @QtCore.pyqtSlot(name="setup_tooltip")
    def setup_tooltip(self):
        print "setup_tooltip: Last updated:", self._widget.lastUpdated()
        # Tool tip for panel
        if self.has_tooltip:
            Plasma.ToolTipManager.self().clearContent(self.applet)
        self.metadata = self.package().metadata()
        self.tooltipdata = Plasma.ToolTipContent()
        self.tooltipdata.setAutohide(False)
        self.tooltipdata.setMainText(self.metadata.name())
        #self.tooltipdata.setSubText(self.metadata.description())
        tooltip_txt = str(i18nc("From code From Amount = To code To Amount - Last updated", "%s %s = %s %s<br /><br />Last updated:<br />%s"))
        tooltip_txt= tooltip_txt % (self._widget.fromCurrency(), self._widget.fromAmount(),
                                    self._widget.toCurrency(), self._widget.toAmount(),
                                    self._widget.lastUpdated())
        #print tooltip_txt
        self.tooltipdata.setSubText(tooltip_txt)
        self.tooltipdata.setImage(KIcon(self.metadata.pluginName()))
        Plasma.ToolTipManager.self().setContent(self.applet, self.tooltipdata)

        # Only register the tooltip in panels
        #if (self.formFactor() != Plasma.Planar):
        if ((self.formFactor() == Plasma.Horizontal) or (self.formFactor() == Plasma.Vertical)):
            #print("CurrencyConverterApplet: In Panel")
            Plasma.ToolTipManager.self().registerWidget(self.applet)
            self.has_tooltip = True
        else:
            Plasma.ToolTipManager.self().clearContent(self.applet)
            Plasma.ToolTipManager.self().unregisterWidget(self.applet)
            #print("CurrencyConverterApplet: Not in Panel")
            self.has_tooltip = False


    def configChanged(self):
        print("CurrencyConverterApplet: configChanged")
        # TODO:
        #   Clear ComboBoxes
        #   Add currencies
        #   Select currencies
        #   Convert


    @QtCore.pyqtSlot(bool, name="netstate_changed")
    def netstate_changed(self, connected):
        print "CurrencyConverterApplet: Network status changed!", connected
        if connected:
            print("CurrencyConverterApplet: Connected!")
            self._widget.setEnabled(True)
            self._widget.start_timer()
            self.setBusy(False)
        else:
            self.notifier.notify("waiting-for-network", i18n("Waiting for network connection."))
            self._widget.setEnabled(False)
            print("CurrencyConverterApplet: Not connected!")
            self.setBusy(True)

    # Whys isn't this called?
    @QtCore.pyqtSlot(name="toolTipAboutToShow")
    def toolTipAboutToShow(self):
        print "CurrencyConverterApplet:toolTipAboutToShow"

def CreateApplet(parent):
  return CurrencyConverterApplet(parent)

