"""
.. moduleauthor:: Magnus Hagdorn <magnus.hagdorn@ed.ac.uk>
.. moduleauthor:: Iain Robinson <iain.robinson@ed.ac.uk>
"""

__all__ = ['PiccoloSpectraList','PiccoloSpectrum']

from collections import MutableMapping, MutableSequence
from datetime import datetime
import json
import os.path

protectedKeys = ['Direction','Dark','Datetime']

class PiccoloSpectraList(MutableSequence):
    """a collection of spectra"""
    def __init__(self,outDir='',seqNr=0, prefix=None):
        self._spectra = []
        self._outDir = outDir
        self._seqNr = seqNr
        self._prefix=prefix

    def __getitem__(self,i):
        return self._spectra[i]
    def __setitem__(self,i,y):
        assert isinstance(y,PiccoloSpectrum)
        self._spectra[i] = y
    def __delitem__(self,i):
        raise RuntimeError, 'cannot delete spectra'
    def __len__(self):
        return len(self._spectra)
    def insert(self,i,y):
        assert isinstance(y,PiccoloSpectrum)
        self._spectra.insert(i,y)

    @property
    def outName(self):
        if self._prefix!=None:
            outp = '{}_'.format(self._prefix)
        else:
            outp = ''
        return '{0}{1:06d}.pico'.format(outp,self._seqNr)

    @property
    def outPath(self):
        return os.path.join(self._outDir,self.outName)

    def serialize(self,pretty=True):
        """serialize to JSON

        :param pretty: when set True (default) produce indented JSON"""

        spectra = []
        for s in self._spectra:
            spectra.append({'Metadata':dict(s.items()), 'Pixels':s.pixels})
        root = {'Spectra':spectra}

        if pretty:
            return json.dumps(root, sort_keys=True, indent=1)
        else:
            return json.dumps(root)

    def write(self,prefix='',clobber=True):
        """write spectra to file

        :param prefix: output prefix"""

        outDir = os.path.join(prefix,self._outDir)
        if not os.path.exists(outDir):
            os.makedirs(outDir)

        fname = os.path.join(outDir,self.outName)
        if not clobber and os.path.exists(fname):
            raise RuntimeError, '{} already exists'.format(fname)

        with open(fname,'w') as outf:
            outf.write(self.serialize())

class PiccoloSpectrum(MutableMapping):
    """An object containing an optical spectrum."""
    def __init__(self):
        self._meta = {}
        self._meta['Direction'] = 'Missing metadata'
        self._meta['Dark'] = 'Missing metadata'
        self._pixels = None
        self.setDatetime()

    def __getitem__(self,key):
        return self._meta[key]

    def __setitem__(self,key,value):
        if key in protectedKeys:
            raise KeyError, 'field {0} is a protected key'.format(key)
        self._meta[key] = value
    
    def __delitem__(self,key):
        if key in protectedKeys:
            raise KeyError, 'field {0} is a protected key'.format(key)
        del self._meta[key]
        
    def __iter__(self):
        return iter(self._meta)

    def __len__(self):
        return len(self._meta)

    def setUpwelling(self,value=None):
        if value == None:
            self._meta['Direction'] = 'Upwelling'
        else:
            assert isinstance(value,bool)
            if value:
                self.setUpwelling()
            else:
                self.setDownwelling()

    def setDownwelling(self):
        self._meta['Direction'] = 'Downwelling'

    def setDark(self,value=None):
        if value==None:
            self._meta['Dark'] = True
        else:
            assert isinstance(value,bool)
            self._meta['Dark'] = value

    def setLight(self):
        self._meta['Dark'] = False
        
    def setDatetime(self,dt=None):
        if dt == None:
            ts = datetime.now()
        elif isinstance(dt,datetime):
            ts = dt
        else:
            ts = datetime.strptime(dt,'%Y-%m-%dT%H:%M:%S')

        self._meta['Datetime'] = '{}Z'.format(ts.isoformat())

    @property
    def pixels(self):
        if self._pixels == None:
            raise RuntimeError, 'The pixel values have not been set.'
        if len(self._pixels) == 0:
            raise RuntimeError, 'There are no pixels in the spectrum.'
        return self._pixels
    @pixels.setter
    def pixels(self,values):
        self._pixels = values

    def getNumberOfPixels(self):
        return len(self.pixels)

