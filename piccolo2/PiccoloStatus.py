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

__all__ = ['PiccoloStatus','PiccoloExtendedStatus']

import ctypes
from bitarray import bitarray
import base64
import math
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

class PiccoloExtendedStatus(object):
    def __init__(self,spectrometers,shutters):
        self._spectrometers = list(spectrometers)
        self._spectrometers.sort()
        self._shutters = list(shutters)
        self._shutters.sort()

        self._nBits = 2+ len(self._shutters) + \
                      len(self._spectrometers)*len(self._shutters)
        
        self._status = bitarray(8*int(math.ceil(self._nBits/8.))) # round up to bytes
        self._status[:] = False

    def __len__(self):
        return self._nBits
        
    @property
    def status(self):
        return self._status[:self._nBits].tolist()
    @property
    def spectrometers(self):
        return self._spectrometers
    @property
    def shutters(self):
        return self._shutters
        
    def _shutter_idx(self,shutter):
        return 2+self.shutters.index(shutter)
    def _auto_idx(self,spectrometer,shutter):
        return 2+len(self.shutters) + \
            self.spectrometers.index(spectrometer)*len(self.shutters) + \
            self.shutters.index(shutter)

    def start_autointegration(self):
        self._status[0] = True
    def stop_autointegration(self):
        self._status[0] = False
    def isAutointegrating(self):
        return self._status[0]
    
    def start_recording(self):
        self._status[1] = True
    def stop_recording(self):
        self._status[1] = False
    def isRecording(self):
        return self._status[1]
    
    def open(self,shutter):
        self._status[self._shutter_idx(shutter)] = True
    def close(self,shutter):
        self._status[self._shutter_idx(shutter)] = False
    def isOpen(self,shutter):
        return self._status[self._shutter_idx(shutter)]
    def isClosed(self,shutter):
        return not self._status[self._shutter_idx(shutter)]

    def setAutointegrationResult(self,spectrometer,shutter,result):
        self._status[self._auto_idx(spectrometer,shutter)] = bool(result)
    def autoSuccess(self,spectrometer,shutter):
        self.setAutointegrationResult(spectrometer,shutter,True)
    def autoFail(self,spectrometer,shutter):
        self.setAutointegrationResult(spectrometer,shutter,False)
    def isAutointegrationSuccessful(self,spectrometer,shutter):
        return self._status[self._auto_idx(spectrometer,shutter)]

    def encode(self):
        return base64.b64encode(self._status.tobytes())
    def update(self,b64status):
        self._status = bitarray()
        self._status.frombytes(base64.b64decode(b64status))
    
if __name__ == '__main__':
    f = PiccoloStatus()

    print f.busy
    f.busy = True
    print f.busy

    e = f.encode()

    f2 = PiccoloStatus(e)
    print f2.busy
    print f2.paused


    shutters = ['up','down']
    spectrometers = ['sA','sB']

    eStatus = PiccoloExtendedStatus(spectrometers,shutters)
    print eStatus.status, len(eStatus),eStatus.isOpen('up'),eStatus.isAutointegrationSuccessful('sA','down')

    eStatus.open('up')
    print eStatus.status, len(eStatus),eStatus.isOpen('up'),eStatus.isAutointegrationSuccessful('sA','down')

    eStatus.autoSuccess('sA','down')
    print eStatus.status, len(eStatus),eStatus.isOpen('up'),eStatus.isAutointegrationSuccessful('sA','down')

    e2Status = PiccoloExtendedStatus(spectrometers,shutters)
    e2Status.update(eStatus.encode())
    print
    print e2Status.status
