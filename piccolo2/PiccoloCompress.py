import numpy as np
import base64,zlib
import struct
def compressArray(array,dtype='uint16'):
    """Converts a numpy array into a byte array, then gzips it and
    base64 encodes it. Should be ~50% smaller than string representation.
    """
    #only retype array if necessary
    if array.dtype != dtype:
        array = array.astype(dtype)
    byte_data = array.tostring()
    compressed_data = zlib.compress(byte_data)
    b64_data = base64.b64encode(compressed_data)
    return b64_data



def decompressArray(b64_data, dtype='uint16'):
    """Performs inverse operations of compressArray"""
    compressed_data = base64.b64decode(b64_data)
    byte_data = zlib.decompress(compressed_data)
    array = np.fromstring(byte_data,dtype=dtype)
    return array


def compressAsDiff(array,dtype='uint8',fallback_dtype='uint16'):
    """Sometimes a smaller data type can be used if the diff of an array is
    used rather than the array itself.  If the data type can't be made 
    smaller, fall back on the base compression method.
    returns whether the diff method worked, and the compressed array
    """
    diff_arr = np.diff(array)
    if np.max(np.abs(diff_arr)) < np.iinfo(dtype).max:
        return True,compressArray(diff_arr,dtype)
    else:
        return False,compressArray(array,fallback_dtype)

def compressFileList(file_list):
    """File lists are highly repetitive, a simple zip works well"""
    return base64.b64encode(zlib.compress(','.join(file_list)))


def decompressFileList(compressed_files):
    files = zlib.decompress(base64.b64decode(compressed_files)).split(',')
    if files == ['']:
        files.pop()
    return files


def compress16to8(array):
    """scale down from 16 bits to 8 in a not-as-lossy-as-it-could-be way"""
    min_val = array.min()
    array -= min_val
    #cover the smallest range of values possible, this is kinda slow
    max_val = array.max()
    scale_down_factor= 255./max_val
    array*=scale_down_factor
    smaller_arr = (array).astype('uint8')
    byte_arr = struct.pack("fH",scale_down_factor,min_val)
    byte_arr += smaller_arr.tostring()
    return base64.b64encode(zlib.compress(byte_arr))

def decompress8to16(byte_string):
    """Recover an array compressed by compress16to8. Some loss of precision
    will occur.
    """
    byte_arr = zlib.decompress(base64.b64decode(byte_string))
    scale_down_factor,min_val = struct.unpack("fH",byte_arr[:6])
    array = np.fromstring(byte_arr[6:],dtype='uint8')
    out_arr = np.zeros(array.size,dtype='float32')+min_val
    out_arr[:]+=((array.astype('float32'))/scale_down_factor)
    return out_arr

def compressMetadata(spectra_dicts):
    """Compress a list of dictionaries of metadata into a string.
    Takes a list of dictionaries with the following keys:
        'SerialNumber','Dark','Direction','SaturationLevel'
        'WavelengthCalibrationCoefficients'
    And returns a string of the format: [SerialNumber 1 ... SerialNumber N] as 
    plaintext, followed by [WCC 1 SatLvl1 ... WCC N SatLvl N] as base64 strings,
    followed by the serial number index  of each spectrum('0'-'9'), followed by
    a list of upwelling-light ('U') vs downwelling-light ('D') vs upwelling-dark
    ('u') vs downwelling-dark ('d') for each spectrum.
    """
    meta_dicts = [s['Metadata'] for s in spectra_dicts]
    serialNos = list(set([m['SerialNumber'] for m in meta_dicts]))

    #base64 encode WavelengthCalibrationCoefficients and Saturation Levels as 
    #4-byte numbers
    waveCalibCoeffs = []
    satLvls = []
    for sn in serialNos:
        #lazy one liner to find a spectrum with the right serial number
        sn_metas = [m for m in meta_dicts if m['SerialNumber'] == sn]
        m = sn_metas[0]
        wcc_bytes = np.array(m['WavelengthCalibrationCoefficients'],dtype='float32')
        waveCalibCoeffs.append(wcc_bytes.tostring())
        #SaturationLevel isn't always in there for some reason
        sat_bytes = np.array(m.get('SaturationLevel',1), dtype='uint32')
        satLvls.append(sat_bytes.tostring())
    
    numeric_mdata = base64.b64encode(''.join(waveCalibCoeffs+satLvls))

    #get the spectrometer order of the set of records
    sn_order = [str(serialNos.index(m['SerialNumber'])) for m in meta_dicts]
    
    #get the direction and light level of each spectrum
    #this probably isn't very robust
    dir_light = [(2*m['Direction'][0]).title()[m['Dark']]for m in meta_dicts]

    #concatenate everything and return
    return ''.join([' '.join(serialNos),' ',numeric_mdata,' ']+sn_order+dir_light)

def decompressMetadata(meta_string):
    """Reconstruct a list of metadata dictionaries that was encoded by
    compressMetadata
    """
    #divide string into sections: Spectrometer names, numeric metadata, and
    #measurement condition metadata
    split_str = meta_string.split(' ')
    serialNos = split_str[:-2]
    nSerialNos = len(serialNos)

    dir_info = split_str[-1]
    spec_used = dir_info[:len(dir_info)/2]
    dir_light = dir_info[len(dir_info)/2:]

    base64_numbers = split_str[-2]
    number_bytes = base64.b64decode(base64_numbers)
    #there are 16 bytes of wavenumber info per 4 bytes of saturation info
    coeffBytes = number_bytes[:4*len(number_bytes)/5]
    saturationBytes = number_bytes[4*len(number_bytes)/5:]
    saturationLevels = np.fromstring(saturationBytes,dtype='uint32').tolist()
    coeffList = np.fromstring(coeffBytes,dtype='float32').reshape(nSerialNos,4)
    coeffList = coeffList.tolist()
    print(coeffList)

    #reconstruct the list of dictionaries
    out_list = []
    for spec_num,serial_number_idx in enumerate(spec_used):
        i = int(serial_number_idx)
        dark = dir_light[i].islower()
        direction = ["Upwelling","Downwelling"][dir_light[spec_num] in "Dd"]
        out_list.append({
            "Metadata":{
                "SerialNumber":serialNos[i],
                "WavelengthCalibrationCoefficients":coeffList[i],
                "SaturationLevel":saturationLevels[i],
                "Dark":dark,
                "Direction":direction
            }
        })

    return out_list

if __name__ == '__main__':
    import json

    data = np.random.randint(100,2000,100).astype('uint16')
    cdata = compressArray(data)
    jdata = json.dumps(data.tolist())
    print("Raw json size: {}, Compressed size: {} ({}% of raw)".format(
        len(jdata),len(cdata),int((100.*len(cdata))/len(jdata))))

    assert((decompressArray(cdata) == data).all())

    meta_list= [
        {"Metadata":{'WavelengthCalibrationCoefficients':[ 644.8102416992188, 
            0.165981724858284, -1.5631136193405837e-05, -5.75436365224391e-10 ], 
            'SerialNumber':'Foo','Dark':False,'Direction':'Upwelling',
            'SaturationLevel':28000}},
        {"Metadata":{'WavelengthCalibrationCoefficients':[ 500.2352416992188, 
            0.885981724858284, -5.1631136193405837e-05, 8.25436365224391e-10 ],
            'SerialNumber':'Bar','Dark':False,'Direction':'Upwelling',
            'SaturationLevel':38000}},
        {"Metadata":{'WavelengthCalibrationCoefficients':[ 644.8102416992188, 
            0.165981724858284, -1.5631136193405837e-05, -5.75436365224391e-10 ],
            'SerialNumber':'Foo','Dark':False,'Direction':'Downwelling',
            'SaturationLevel':28000}},

        {"Metadata":{'WavelengthCalibrationCoefficients':[ 500.2352416992188, 
            0.885981724858284, -5.1631136193405837e-05, 8.25436365224391e-10 ],
            'SerialNumber':'Bar','Dark':False,'Direction':'Downwelling',
            'SaturationLevel':38000}},
    ]
    cmeta = compressMetadata(meta_list)
    jmeta = json.dumps(meta_list)
    print("Raw json size: {}, Compressed size: {} ({}% of raw)".format(
        len(jmeta),len(cmeta),int((100.*len(cmeta))/len(jmeta))))





