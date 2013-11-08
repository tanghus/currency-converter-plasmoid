# -*- coding: utf-8 -*-
# kate: space-indent on; tab-width 4; indent-width 4; indent-mode python; backspace-indents; encoding utf-8; line-numbers on; remove-trailing-space on;
#
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

from urllib import urlencode
from datetime import datetime
from PyQt4.QtCore import Qt, pyqtSignal, QObject, QVariant, QString, QSize, QTimer, SIGNAL
from PyQt4.QtGui import QDoubleValidator, QGraphicsWidget, QGraphicsGridLayout, QGraphicsLinearLayout, QSizePolicy
from PyKDE4.kdecore import KGlobal, i18n, i18nc, KCurrencyCode, KDateTime, KUrl
from PyKDE4.kdeui import KIcon, KDoubleValidator
from PyKDE4.kio import KIO
from PyKDE4.plasma import Plasma

class CurrencyConverter(QGraphicsWidget):
    updated = pyqtSignal()

    def __init__(self,parent):
        QGraphicsWidget.__init__(self)
        self.applet = parent


    def init(self):
        print ("CurrencyConverter: init")

        self.swapping = False
        self.grid_layout = None
        self.timer = None
        self.last_updated = ""

        self.def_from = self.applet.cfg.readEntry("default_from", QString("USD")).toString()
        print "System default country:", KGlobal.locale().country()
        print "System default currency code:", KGlobal.locale().currencyCode()
        self.def_to = self.applet.cfg.readEntry("default_to", KGlobal.locale().currencyCode()).toString()
        #self.def_to = self.applet.cfg.readEntry("default_to", QString("EUR")).toString()
        self.def_amount = self.applet.cfg.readEntry("default_amount", 1.0).toString()
        self.update_interval = self.applet.cfg.readEntry("update_interval", QVariant(60)).toInt()[0] # why does this return a tuple?

        print "Update interval:", self.update_interval

        #self.theme = Plasma.Svg(self)
        #self.theme.setImagePath("widgets/background")
        #self.setBackgroundHints(Plasma.Applet.DefaultBackground)

        # init arrows svg
        #self.arrows_svg = Plasma.Svg(self);
        #self.arrows_svg.setImagePath("widgets/configuration-icons");
        #self.arrows_svg.setContainsMultipleImages(True);
        #self.arrows_svg.resize(KIconLoader.SizeSmall, KIconLoader.SizeSmall);

        #self.collapse_button = Plasma.ToolButton()
        #self.collapse_button.setZValue(3)
        #self.collapse_button.nativeWidget().setMaximumSize(QSize(24, 24))
        #if self.collapsed:
            #self.collapse_button.nativeWidget().setIcon(KIcon(QIcon(self.arrows_svg.pixmap("collapse"))))
            ##self.collapse_button.nativeWidget().setIcon(KIcon("arrow-down"))
        #else:
            #self.collapse_button.nativeWidget().setIcon(KIcon(QIcon(self.arrows_svg.pixmap("restore"))))
            ##self.collapse_button.nativeWidget().setIcon(KIcon("arrow-up"))
        #self.collapse_button.nativeWidget().setToolTip(i18n("Show/Hide controls"))
        #self.collapse_button.clicked.connect(self.collapse_or_expand)

        invert = "%scontents/icons/invert.png" % self.applet.package().path()
        self.invert_button = Plasma.ToolButton()
        self.invert_button.setZValue(3)
        self.invert_button.nativeWidget().setMaximumSize(QSize(24, 24))
        self.invert_button.nativeWidget().setIcon(KIcon(invert))
        self.invert_button.nativeWidget().setToolTip(i18n("Swap currencies"))
        self.invert_button.clicked.connect(self.invert_currencies)

        self.title_label = Plasma.Label()
        self.title_label.nativeWidget().setWordWrap(False)
        #self.title_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.title_label.setText(i18n("Currency Converter"))
        self.title_label.setAlignment(Qt.AlignCenter)
        f = self.title_label.nativeWidget().font()
        f.setBold(True)
        self.title_label.nativeWidget().setFont(f)

        self.from_label = Plasma.Label()
        self.from_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.from_label.nativeWidget().setAlignment(Qt.AlignRight)
        self.from_label.setText(i18n("From:"))

        self.currency_from = Plasma.ComboBox()
        self.currency_from.setZValue(2)
        self.currency_from.setFocusPolicy(Qt.NoFocus)

        self.to_label = Plasma.Label()
        self.to_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.to_label.nativeWidget().setAlignment(Qt.AlignRight)
        self.to_label.setText(i18n("To:"))

        self.currency_to = Plasma.ComboBox()
        self.currency_to.setZValue(1)
        self.currency_to.setFocusPolicy(Qt.NoFocus)

        self.amount_label = Plasma.Label()
        self.amount_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.amount_label.nativeWidget().setAlignment(Qt.AlignTop) # NOTE: This is a hack because otherwise it flows down when you resize :-/
        self.amount_label.nativeWidget().setAlignment(Qt.AlignRight)
        self.amount_label.setText(i18n("Amount:"))

        self.amount = Plasma.LineEdit()
        self.amount.setClearButtonShown(True)
        self.amount_validator = QDoubleValidator(self.amount.nativeWidget())
        #if KGlobal.locale().decimalSymbol() == ",":
        #    self.amount_validator.setAcceptLocalizedNumbers(True)
        self.amount.nativeWidget().setValidator(self.amount_validator)
        print "Default amount:", self.def_amount
        self.amount.setText(self.def_amount)
        self.amount.setFocus()

        self.amount.editingFinished.connect(self.amount_editing_finished)

        self.from_amount_label = Plasma.Label()
        self.from_amount_label.setMinimumWidth(30)

        self.equal_label = Plasma.Label()
        self.equal_label.setText("=")

        # shows the currency symbol or abbreviation
        self.to_amount_label = Plasma.Label()
        self.to_amount_label.setMinimumWidth(30)

        self.conversion_result = Plasma.LineEdit()
        self.conversion_result.nativeWidget().setAlignment(Qt.AlignRight)
        self.conversion_result.nativeWidget().setReadOnly(True)

        self.credits_label = Plasma.Label()
        self.credits_label.setAlignment(Qt.AlignRight)
        self.credits_label.nativeWidget().setOpenExternalLinks(True)
        logo = "%scontents/images/yahoo-attribution.png" % self.applet.package().path()
        self.credits_label.setText(i18n("Data from <a href=\"http://finance.yahoo.com/currency-converter\"><img src=\"%s\"</a>" % logo))
        f = self.credits_label.nativeWidget().font()
        f.setPointSize(self.font_size()-2)
        self.credits_label.nativeWidget().setFont(f)
        QObject.connect(self.credits_label.nativeWidget(), SIGNAL("linkActivated(const QString&)"), self.open_link)
        QObject.connect(self.credits_label, SIGNAL("linkActivated(const QString&)"), self.open_link)
        self.credits_label.linkActivated.connect(self.open_link)

        # Limit the number of currencies shown at a time if docked in bottom panel.
        #if ((self.applet.formFactor() == Plasma.Horizontal) or (self.applet.formFactor() == Plasma.Vertical)):
        if ((self.applet.formFactor() == Plasma.Horizontal) and (self.applet.location() == Plasma.BottomEdge)):
          self.currency_from.nativeWidget().setMaxVisibleItems(6)
          self.currency_to.nativeWidget().setMaxVisibleItems(4)

        m_locale = KGlobal.locale()
        #cc_list = l.currency().allCurrencyCodesList(KCurrencyCode.ActiveCurrency|KCurrencyCode.SuspendedCurrency|KCurrencyCode.ObsoleteCurrency)
        cc_list = m_locale.currency().allCurrencyCodesList(KCurrencyCode.ActiveCurrency)
        cc_namelist = []
        #print "CC's:", len(l.currency().allCurrencyCodesList())
        #print "# KDE Currency Codes:", len(cc_list)
        for cc in cc_list:
          cc_namelist.append(i18nc( "@item currency name and currency code", "%1 (%2)",
                                    m_locale.currency().currencyCodeToName( cc ), cc ) )

        #cc_namelist.sort()
        for cur in sorted(set(cc_namelist)):
          #print u"Currency:", unicode(cur)
          self.currency_from.nativeWidget().addItem( cur, QVariant( cur.mid( cur.length()-4, 3 ) ) )
          self.currency_to.nativeWidget().addItem( cur, QVariant( cur.mid( cur.length()-4, 3 ) ) )

        self.currency_from.nativeWidget().setCurrentIndex( self.currency_from.nativeWidget().findData( QVariant( self.def_from ) ) )
        self.currency_to.nativeWidget().setCurrentIndex( self.currency_to.nativeWidget().findData( QVariant( self.def_to ) ) )

        self.currency_from.textChanged.connect(self.currency_changed)
        self.currency_to.textChanged.connect(self.currency_changed)

        self.layout_widgets()
        if self.applet.nwmon.connected():
          self.applet.setBusy(False)
          self.start_timer()

    def open_link(self, lnk):
        print "open_link:", lnk

    def start_timer(self):
        print "CurrencyConverter::start_timer '%s'" % self.update_interval
        if not self.timer:
            self.timer = QTimer(self)
        else:
            self.timer.stop()
        if self.update_interval > 0:
            self.timer.setInterval(1000*60*self.update_interval)
            self.timer.timeout.connect(self.do_convert)
            self.timer.start()
            self.do_convert()


    def setEnabled(self, state):
        self.collapse_button.setEnabled(state)
        self.invert_button.setEnabled(state)
        self.currency_from.setEnabled(state)
        self.currency_to.setEnabled(state)
        self.amount.setEnabled(state)
        self.conversion_result.setEnabled(state)

    def invert_currencies(self):
        self.swapping = True
        idx_from = self.currency_from.nativeWidget().currentIndex()
        self.currency_from.nativeWidget().setCurrentIndex(self.currency_to.nativeWidget().currentIndex())
        self.currency_to.nativeWidget().setCurrentIndex(idx_from)
        cur = self.currency_from.text()
        self.def_from = cur.mid( cur.length()-4, 3 )
        cur = self.currency_to.text()
        self.def_to = cur.mid( cur.length()-4, 3 )
        self.swapping = False
        self.do_convert()

    def layout_widgets(self):
      # Layout
      if self.grid_layout <> None:
        del self.grid_layout
      self.grid_layout = QGraphicsGridLayout()
      header_layout = QGraphicsLinearLayout()
      header_layout.addItem(self.invert_button)
      header_layout.addItem(self.title_label)
      self.grid_layout.addItem(header_layout, 0, 0, 1, 2)
      #self.grid_layout.addItem(self.collapse_button, 0, 0)
      #self.grid_layout.addItem(self.title_label, 0, 1)
      self.grid_layout.addItem(self.from_label, 1, 0)
      self.grid_layout.addItem(self.currency_from, 1, 1)
      self.grid_layout.addItem(self.to_label, 2, 0)
      self.grid_layout.addItem(self.currency_to, 2, 1)
      self.grid_layout.addItem(self.amount_label, 3, 0)
      self.amount_layout = QGraphicsLinearLayout()
      self.amount_layout.addItem(self.amount)
      self.amount_layout.addItem(self.from_amount_label)
      self.amount_layout.addItem(self.equal_label)
      self.amount_layout.addItem(self.conversion_result)
      self.amount_layout.addItem(self.to_amount_label)
      self.grid_layout.addItem(self.amount_layout, 3, 1)
      self.grid_layout.addItem(self.credits_label, 4, 0, 1, 2)

      self.setLayout(self.grid_layout)

    def currency_changed(self):
      print "CurrencyConverter::currency_changed"
      if self.swapping or not self.applet.nwmon.connected():
        return

      try:
        cur = self.currency_from.text()
        self.def_from = cur.mid( cur.length()-4, 3 )
        #self.def_from = convert_from = self.currency_from.text()[0:3]

        cur = self.currency_to.text()
        self.def_to = cur.mid( cur.length()-4, 3 )
        #self.def_to = convert_to = self.currency_to.text()[0:3]
        self.applet.cfg.writeEntry("default_from", self.def_from)
        self.applet.cfg.writeEntry("default_to", self.def_to)
        self.applet.cfg.sync()
      except RuntimeError:
        print "CurrencyConverter::currency_changed: Regular update."
      self.do_convert()

    def do_convert(self):
        print "CurrencyConverter::do_convert"
        print "CurrencyConverter::do_convert. Update interval:", self.update_interval
        print "Convert from:", self.def_from, "to", self.def_to
        url = "http://quote.yahoo.com/d/quotes.csv?s=%s%s=X&f=l1&e=.csv" % (self.def_from, self.def_to)
        print url
        self.applet.setBusy(True)
        job = KIO.get(KUrl(url), KIO.NoReload, KIO.HideProgressInfo)
        job.warning.connect(self.job_warning)
        job.data.connect(self.job_received)
        job.result.connect(self.job_done)
        self.timer.start() # restart the timer on activity

    def job_warning(self, job, txt, richtxt):
        print "Job warning: '%s' - '%s'" % (txt, richtxt)
        self.applet.showMessage(KIcon("dialog-information"), richtxt, Plasma.ButtonOk)

    def job_done(self, job):
        print "Job done."
        if job.error():
            self.applet.notifier.notify("networkerror", job.errorString())
            print job.errorString()
            #self.applet.showMessage(KIcon("dialog-error"), job.errorString(), Plasma.ButtonOk)
            #print job.errorText()

    def job_received(self, job, data):
      if len(data) > 0:
        amount = self.def_amount
        # NOTE: Check if self.amount.text() is localized and convert it if neccesary.
        # Isn't there a better way of doing this?
        if KGlobal.locale().decimalSymbol() == ",":
          # remove any "."s and replace "," with "."
          # there ought to bet a prettier way to do this
          if amount.contains(","):
            amount = amount.replace(".", "").replace(",", ".")
        print "%f * %f = %f" % (float(amount), float(data), float(data)*float(amount))
        print float(data)*float(amount)
        self.conversion_result.setText(str(float(data)*float(amount)))
        self.from_amount_label.setText(KCurrencyCode(self.def_from).defaultSymbol())
        self.to_amount_label.setText(KCurrencyCode(self.def_to).defaultSymbol())
        #self.from_amount_label.setText(QString.fromUtf8(CURRENCY[str(self.currency_from.text())[0:3]].get_symbol()))
        #self.to_amount_label.setText(QString.fromUtf8(CURRENCY[str(self.currency_to.text())[0:3]].get_symbol()))
        print "Last updated:", KGlobal.locale().formatDateTime(KDateTime.currentLocalDateTime())
        self.last_updated = KGlobal.locale().formatDateTime(KDateTime.currentLocalDateTime())
        #self.last_updated = str(datetime.now().ctime())
        self.credits_label.nativeWidget().setToolTip(str(i18n("Last updated: %s")) % self.last_updated)
        self.applet.setBusy(False)
        print "Data recieved:", data
        self.updated.emit()

    def amount_editing_finished(self):
      print "Amount editing finished"
      self.def_amount = self.amount.text()
      self.applet.cfg.writeEntry("default_amount", self.def_amount)
      self.applet.cfg.sync()
      self.do_convert()

    def font_size(self):
      return Plasma.Theme.defaultTheme().font(Plasma.Theme.DefaultFont).pointSize()

    def fromCurrency(self):
      return KCurrencyCode(self.def_from).defaultSymbol()

    def toCurrency(self):
      return KCurrencyCode(self.def_to).defaultSymbol()

    def fromAmount(self):
      return self.amount.text()

    def toAmount(self):
      return self.conversion_result.text()

    def lastUpdated(self):
      return self.last_updated
