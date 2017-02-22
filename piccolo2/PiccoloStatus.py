# Copyright 2014-2016 The Piccolo Team
#
# This file is part of piccolo2-common.
#
# piccolo2-common is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# piccolo2-common is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with piccolo2-common.  If not, see <http://www.gnu.org/licenses/>.

"""
.. moduleauthor:: Magnus Hagdorn <magnus.hagdorn@ed.ac.uk>
"""

__all__ = ['PiccoloStatus']

import ctypes
c_uint32 = ctypes.c_uint32

class PiccoloFlagsBits(ctypes.LittleEndianStructure):
    _fields_ = [
        ("connected", c_uint32, 1 ),  # asByte & 1
        ("busy", c_uint32, 1 ),  # asByte & 2
        ("paused", c_uint32, 1 ),  # asByte & 4
        ("file_incremented", c_uint32, 1 ),  # asByte & 8
        ("new_message", c_uint32, 1 ),  # asByte & 16
        ]

class PiccoloFlags(ctypes.Union):
    _anonymous_ = ("bit",)
    _fields_ = [
        ("bit", PiccoloFlagsBits),
        ("asBytes", c_uint32)
    ]

class PiccoloStatus(object):
    def __init__(self,flagStr=None):
        object.__setattr__(self,"_status",PiccoloFlags())
        if flagStr!=None:
            self._status.asBytes=int(flagStr,16)

    def encode(self):
        return hex(self._status.asBytes)[:-1]
        
    def set(self,name):
        setattr(self._status.bit,name,1)

    def unset(self,name):
        setattr(self._status.bit,name,0)
    
    def __getattr__(self,name):
        return getattr(self._status.bit,name) == 1

    def __setattr__(self,name,value):
        assert isinstance(value,bool)
        if value:
            self.set(name)
        else:
            self.unset(name)

if __name__ == '__main__':
    f = PiccoloStatus()

    print f.busy
    f.busy = True
    print f.busy

    e = f.encode()

    f2 = PiccoloStatus(e)
    print f2.busy
    print f2.paused



