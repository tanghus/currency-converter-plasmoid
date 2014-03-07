# -*- coding: utf-8 -*-
# kate: space-indent on; tab-width 4; indent-width 4; indent-mode python; backspace-indents; encoding utf-8; line-numbers on; remove-trailing-space modified;
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
from PyKDE4.solid import Solid
import sys

statusString = {
                  Solid.Networking.Unknown: "Unknown",\
                  Solid.Networking.Unconnected: "Unconnected",\
                  Solid.Networking.Disconnecting: "Disconnecting",\
                  Solid.Networking.Connecting: "Connecting",\
                  Solid.Networking.Connected: "Connected"\
                }

class NetworkMonitor(QtCore.QObject):
    status_changed = QtCore.pyqtSignal(bool)

    def __init__(self):
        QtCore.QObject.__init__(self)

        self.is_connected = (Solid.Networking.status() == Solid.Networking.Connected) or (Solid.Networking.status() == Solid.Networking.Unknown) == True
        print "NetworkMonitor: %i" % self.is_connected

        try:
            # Apparently this is only possible from KDE SC 4.4.X
            notifier = Solid.Networking.notifier()
            #notifier.statusChanged.connect(self.netstate_changed)
            notifier.connect(notifier, QtCore.SIGNAL("statusChanged(Solid::Networking::Status)"), self.netstate_changed)
            print("NetworkMonitor: Connected to network notifier.")
        except AttributeError as e: # (errno, strerror):
            #print "I/O error({0}): {1}".format(errno, strerror)
            print(e)
            print("NetworkMonitor: Trouble setting up network monitor")
        except:
            print("NetworkMonitor: Trouble setting up network monitor")
            print "NetworkMonitor: Unexpected error:", sys.exc_info()[0]

        print "NetworkMonitor: Network is connected:", (Solid.Networking.status() == Solid.Networking.Connected)
        print "NetworkMonitor: Current status:", statusString[Solid.Networking.status()]

    def connected(self):
        return self.is_connected

    @QtCore.pyqtSlot(int, name="netstate_changed", result="Solid::Networking::Status")
    def netstate_changed(self, status):
        print "NetworkMonitor: Network status changed! %s" % statusString[status]
        if (status == Solid.Networking.Connected) or (status == Solid.Networking.Unknown):
            print "NetworkMonitor: Connected!"
            self.is_connected = True
        elif status == Solid.Networking.Unconnected:
            self.is_connected = False
            print "NetworkMonitor: Not connected!"
        self.status_changed.emit(self.is_connected)


if __name__== '__main__' :
    NetworkMonitor()