import numpy as np
import base64,zlib

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

if __name__ == '__main__':
    import json

    data = np.random.randint(100,2000,100).astype('uint16')
    cdata = compressArray(data)
    jdata = json.dumps(data.tolist())
    print("Raw json size: {}, Compressed size: {} ({}% of raw)".format(
        len(jdata),len(cdata),int((100.*len(cdata))/len(jdata))))

    assert isinstance(cdata,str)
    assert (decompressArray(cdata) == data).all()

