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

from PyQt4.QtCore import QVariant
import sys, os

def fixType(val):
    # FIXME: This is needed to take care of problems with KDE 4.3 bindings, but it should be removed
    # when things are fixed.
    if type(val) == QVariant:
      return str(val.toString())
    else:
      return val

def createDirectory(d):
  if not os.path.isdir(d):
    try:
      os.mkdir(d)
    except IOError as (errno, strerror):
      print "I/O error({0}): {1}".format(errno, strerror)
    except:
      print "Problem creating directory:", d
      print "Unexpected error:", sys.exc_info()[0]

def enum(*sequential, **named):
    """Used like so:
    >>> Numbers = enum('ZERO', 'ONE', 'TWO')
    >>> Numbers.ZERO
    0
    >>> Numbers.ONE
    1"""
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

class Enum(set):
    """Here is its Implementation...
    Animals = Enum(["DOG", "CAT", "Horse"])

    print Animals.DOG"""
    def __getattr__(self, name):
        if name in self:
            return name
        raise AttributeError
