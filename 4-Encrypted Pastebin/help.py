'''
Helping generic functions
'''

from requests import get

def replace_chars(text: str, reverse=False):

    # These should be done in reverse
    replacements = {
        '~': '=',
        '!': '/',
        '-': '+'
    }
    for i in replacements:
        if reverse:
            text = text.replace(replacements[i], i)
        else:
            text = text.replace(i, replacements[i])
    return text

def make_request(url: str, payload: str = ""):
    payload = url + str(payload)
    response_raw = get(payload)

    if "PaddingException" in response_raw.text:
        return {'0': "Padding Exception"}

    if "ValueError: IV must be 16 bytes long" in response_raw.text:
        return {'1': "IV must be 16 bytes long"}
    
    if "Error: Incorrect padding" in response_raw.text:
        return {'2': "Incorrect padding"}
    
    if "ValueError: Input strings must be a multiple of 16 in length" in response_raw.text:
        return {'3': "Input strings must be a multiple of 16 in length"}
    
    if "UnicodeDecodeError:" in response_raw.text:
        return {'4': "UnicodeDecodeError"}
    
    if "IndexError: string index out of range" in response_raw.text:
        return {'5': "IndexError"}
    
    

    return {'-1' : response_raw}

def add2bytes(byte1: bytes, byte2: bytes):
    '''Adds two bytes (the result must fit in one byte!)'''

    result = int.from_bytes(byte1, 'big') + int.from_bytes(byte2, 'big')
    result = result.to_bytes(1, 'big')
    return result


def xor2bytes(byte1: bytes, byte2: bytes):
    '''
    Python's XOR supports only integers (lol).
    So they must be converted first to integers, then XOR them and then be converted
    back to bytes.

    It was done this way because it is faster: https://stackoverflow.com/questions/29408173/byte-operations-xor-in-python
    '''

    int1 = int.from_bytes(byte1, 'big')
    int2 = int.from_bytes(byte2, 'big')
    int_res = int1 ^ int2
    return int_res.to_bytes(max(len(byte1), len(byte1)), 'big')


