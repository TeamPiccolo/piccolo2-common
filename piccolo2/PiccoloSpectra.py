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
    def __init__(self,seqNr=0,data=None):
        self._spectra = []
        self._seqNr = seqNr
        self._prefix = ''

        # initialise from json if available
        if data!=None:
            if isinstance(data,(str,unicode)):
                data = json.loads(data)
            self._seqNr = data['SequenceNumber']
            for s in data['Spectra']:
                self.append(PiccoloSpectrum(data=s))

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
    def seqNr(self):
        return self._seqNr
    
    @property
    def prefix(self):
        return self._prefix
    @prefix.setter
    def prefix(self,p):
        self._prefix = p
    
    @property 
    def outName(self):
        return '{0}{1:06d}.pico'.format(self.prefix,self.seqNr)

    @property
    def directions(self):
        dirs = set()
        for s in self._spectra:
            dirs.add(s['Direction'])
        return list(dirs)

    def getSpectra(self,direction,spectrum):
        if spectrum == 'Dark':
            dark = True
        elif spectrum == 'Light':
            dark = False
        else:
            raise KeyError, 'spectrum must be one of Dark or Light'
        spectra = []
        for s in self._spectra:
            if s['Direction'] == direction and s['Dark'] == dark:
                 spectra.append(s)
        return spectra

    def serialize(self,pretty=True):
        """serialize to JSON

        :param pretty: when set True (default) produce indented JSON"""

        spectra = []
        for s in self._spectra:
            spectra.append(s.as_dict)
        root = {'Spectra':spectra, 'SequenceNumber': self._seqNr}

        if pretty:
            return json.dumps(root, sort_keys=True, indent=1)
        else:
            return json.dumps(root)

    def write(self,prefix='',clobber=True):
        """write spectra to file

        :param prefix: output prefix"""

        outName = os.path.join(prefix,self.outName)
        outDir = os.path.dirname(outName)

        if not os.path.exists(outDir):
            os.makedirs(outDir)

        if not clobber and os.path.exists(outName):
            raise RuntimeError, '{} already exists'.format(outName)

        with open(outName,'w') as outf:
            outf.write(self.serialize())

class PiccoloSpectrum(MutableMapping):
    """An object containing an optical spectrum."""
    def __init__(self,data=None):
        self._meta = {}
        self._meta['Direction'] = 'Missing metadata'
        self._meta['Dark'] = 'Missing metadata'
        self._pixels = None
        self.setDatetime()

        # initialise from json if available
        if data != None:
            if isinstance(data,str):
                data = json.loads(data)
            for key in data['Metadata']:
                self._meta[key] = data['Metadata'][key]
            self._pixels = data['Pixels']

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
    
    @property
    def as_dict(self):
        spectrum = {}
        spectrum['Metadata'] = dict(self.items())
        spectrum['Pixels'] = self.pixels
        return spectrum

    def serialize(self,pretty=True):
        spectrum = self.as_dict
        if pretty:
            return json.dumps(spectrum, sort_keys=True, indent=1)
        else:
            return json.dumps(spectrum)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv)>1:
        data = open(sys.argv[1],'r').read()
        
        spectra = PiccoloSpectraList(data=data)
        print spectra.directions
        
