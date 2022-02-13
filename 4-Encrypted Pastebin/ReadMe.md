# Encrypted Pastebin

The website seems to work as follows:
1. It takes a title and some text
1. Makes a POST request to itself `http://__IP__/__ROOM__/` with `title=__title__&body=__body__` in the request body
1. The server encrypts the data
1. The server responds with a 302 response (redirect)
1. The client is redirected and makes a GET request with the link from the `Location` response header
`http://__IP__/__ROOM__ /?post=__payload__`
1. The server receives the payload, decrypts it and returns an html document if it was decrypted successfully.

Example of a payload: `CVvRvrrD8O-kDeVBHh8-7aX56YGWh59sDqMY8TnNL3xHdNEvaXmFdqqI3aS6iVCUjxEHiq!EYogF0moI2V1Pdare4OzG56pftL!PzaWEMtEID2NhbnSAqs7dUQ5-giVPNh3wYYm1WQZbje!cdPtGV!kzoxPjJMwJayhu1PSHqAdu3P21YiNNWNlk94kPwrn0Jn5NlaqrKOXx9plp8FjSuw~~`

The GET request with the above string as `__payload__` responds with:
```HTML
<!doctype html>
<html>
	<head>
		<title>Test -- Encrypted Pastebin</title>
	</head>
	<body>
		<h1>Test</h1>
		<pre>
test
		</pre>
		<img src="tracking.gif">
	</body>
</html>
```

---
## Flag 0 - Improper Error Handling

### Accessing the situation:

When the server is hit with an invalid request it doesn't properly handle the exceptions raised.

### Execution:

Make a request with no `?post=` data like so:
```
http:// {IP} / {ROOM} /?post=
```
The backend spits out an error but first it shows the flag

## Flag 1 - Padding Oracle Attack

### Usefull Info:
[How PadBuster works](https://blog.gdssecurity.com/labs/2010/9/14/automated-padding-oracle-attacks-with-padbuster.html)

[Writeup on this flag](https://sec.wonderingraven.net/hacker-ctf/write-up-hacker101-encrypted-pastebin/)

[Example solution](https://github.com/richardevcom/padding-oracle-attack)

[Extremely useful writeup in chinese](https://xz.aliyun.com/t/7054)

### Accessing the situation:

Making a request `http://__IP__/__ROOM__/?post=` gives this error:
```
Traceback (most recent call last):
  File "./main.py", line 69, in index
    post = json.loads(decryptLink(postCt).decode('utf8'))
  File "./common.py", line 48, in decryptLink
    cipher = AES.new(staticKey, AES.MODE_CBC, iv)
  File "/usr/local/lib/python2.7/site-packages/Crypto/Cipher/AES.py", line 95, in new
    return AESCipher(key, *args, **kwargs)
  File "/usr/local/lib/python2.7/site-packages/Crypto/Cipher/AES.py", line 59, in __init__
    blockalgo.BlockAlgo.__init__(self, _AES, key, *args, **kwargs)
  File "/usr/local/lib/python2.7/site-packages/Crypto/Cipher/blockalgo.py", line 141, in __init__
    self._cipher = factory.new(key, *args, **kwargs)
ValueError: IV must be 16 bytes long
```
**Conclusions**:
* The initializing vector is 16 bytes long
* The encryption is AES CBC with a static key


But `http://__IP__/__ROOM__/?post=1` gives:

```
Traceback (most recent call last):
  File "./main.py", line 69, in index
    post = json.loads(decryptLink(postCt).decode('utf8'))
  File "./common.py", line 46, in decryptLink
    data = b64d(data)
  File "./common.py", line 11, in <lambda>
    b64d = lambda x: base64.decodestring(x.replace('~', '=').replace('!', '/').replace('-', '+'))
  File "/usr/local/lib/python2.7/base64.py", line 328, in decodestring
    return binascii.a2b_base64(s)
Error: Incorrect padding
```
**Conclusions**:
* `[...] lambda x: base64.decodestring [...]` The string is encoded in base64 from UTF-8
* Some replacements take place before the string is decoded

Lastly, `http://__IP__/__ROOM__/?post=16161616161616161616161616161616'` gives:
```
Traceback (most recent call last):
  File "./main.py", line 69, in index
    post = json.loads(decryptLink(postCt).decode(\'utf8\'))
  File "./common.py", line 49, in decryptLink
    return unpad(cipher.decrypt(data))
  File "/usr/local/lib/python2.7/site-packages/Crypto/Cipher/blockalgo.py", line 295, in decrypt
    return self._cipher.decrypt(ciphertext)
ValueError: Input strings must be a multiple of 16 in length
              
```
**Conclusions**:
* Each block is 16 bytes in length


Using this `b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'` as payload gives:
```
Traceback (most recent call last):
  File "./main.py", line 69, in index
    post = json.loads(decryptLink(postCt).decode('utf8'))
  File "./common.py", line 49, in decryptLink
    return unpad(cipher.decrypt(data))
  File "./common.py", line 22, in unpad
    raise PaddingException()
PaddingException
```
**Conclusions**:
* The payload has led to invalid padding. This signals that the payload is of correct length but when being XORed it raised a padding error. This should be the most common error when a successful attack is being executed

Using this `AAAAAAAAAAAAAAAAAAAAAA~~` as payload:
```
Traceback (most recent call last):
  File "./main.py", line 69, in index
    post = json.loads(decryptLink(postCt).decode(utf8))
  File "./common.py", line 49, in decryptLink
    return unpad(cipher.decrypt(data))
  File "./common.py", line 19, in unpad
    padding = data[-1]
IndexError: string index out of range
```
**Conclusions**:
* This is one of the errors that the padding was correct and the server attempted to decipher the message. No data block was attached to the payload, so the server had nothing to decipher.

Using this `AAAAAAAAAAAAAAAAAAAAADbjZUA89fHn3Q5OfxFJteUyBWk8PVGXdZnPdkWgEKWq-37h78BxQEM57uhy74ATSJgnFrH05xRnDwYcd3eNKm4MmjSDxQ8WnclBYlUkaKrbwF3DyKAoFmZ3k9WTWSzd8Ujt!WJ-xj6ZtRHb87jEOgZWLCw1AhdudKGm9IbeLLMfzxawrmuikHHjTNv!CTki!w~~` as payload (our IV and some demo data):
```
Traceback (most recent call last):
  File "./main.py", line 69, in index
    post = json.loads(decryptLink(postCt).decode('utf8'))
  File "/usr/local/lib/python2.7/encodings/utf_8.py", line 16, in decode
    return codecs.utf_8_decode(input, errors, True)
UnicodeDecodeError: 'utf8' codec can't decode byte 0xb7 in position 0: invalid start byte
```
**Conclusions**:
* This is one of the errors that the padding was correct, and the server encountered an error while decoding the deciphered data.


### Execution:

Pressing the `post` button with no text or title makes a request with this as `__payload__`:

`zDwjyajP0AQGO0UaTlkk9jbjZUA89fHn3Q5OfxFJteUyBWk8PVGXdZnPdkWgEKWq-37h78BxQEM57uhy74ATSJgnFrH05xRnDwYcd3eNKm4MmjSDxQ8WnclBYlUkaKrbwF3DyKAoFmZ3k9WTWSzd8Ujt!WJ-xj6ZtRHb87jEOgZWLCw1AhdudKGm9IbeLLMfzxawrmuikHHjTNv!CTki!w~~`

Some replacements need to be made by the server ` [...] x.replace('~', '=').replace('!', '/').replace('-', '+') [...]` (as seen from the above errors) which result in:

`zDwjyajP0AQGO0UaTlkk9jbjZUA89fHn3Q5OfxFJteUyBWk8PVGXdZnPdkWgEKWq+37h78BxQEM57uhy74ATSJgnFrH05xRnDwYcd3eNKm4MmjSDxQ8WnclBYlUkaKrbwF3DyKAoFmZ3k9WTWSzd8Ujt/WJ+xj6ZtRHb87jEOgZWLCw1AhdudKGm9IbeLLMfzxawrmuikHHjTNv/CTki/w==`


This is then decoded from base64 into a string of bytes:

`b'\xcc<#\xc9\xa8\xcf\xd0\x04\x06;E\x1aNY$\xf66\xe3e@<\xf5\xf1\xe7\xdd\x0eN\x7f\x11I\xb5\xe52\x05i<=Q\x97u\x99\xcfvE\xa0\x10\xa5\xaa\xfb~\xe1\xef\xc0q@C9\xee\xe8r\xef\x80\x13H\x98\'\x16\xb1\xf4\xe7\x14g\x0f\x06\x1cww\x8d*n\x0c\x9a4\x83\xc5\x0f\x16\x9d\xc9AbU$h\xaa\xdb\xc0]\xc3\xc8\xa0(\x16fw\x93\xd5\x93Y,\xdd\xf1H\xed\xfdb~\xc6>\x99\xb5\x11\xdb\xf3\xb8\xc4:\x06V,,5\x02\x17nt\xa1\xa6\xf4\x86\xde,\xb3\x1f\xcf\x16\xb0\xaek\xa2\x90q\xe3L\xdb\xff\t9"\xff'`

which has a length of 160 bytes. We know (from the above errors) that the initializing vector and each block should be 16 bytes long. So the message consists of 10 16 byte long blocks.

Nearly every solution for this flag suggests to use [PadBuster](https://github.com/AonCyberLabs/PadBuster), but I am not a script kiddie. I will DIY this bitch.

Reading on how PadBuster works from the [Info](###-usefull-info:) we can deduce that:
* The 1st block is the initialization vector
* The rest 9 blocks are the data that once decrypted should give us the message

We split these ten blocks in pairs of 2. The first pair is the original IV and the 1st data block. Then we will take the 1st data block and the 2nd data block, etc. We send two blocks at a time because the server may respond with unrelated errors when we send more.

For each pair we refer to its first block as the *IV* and the *data*. The *data* block is not important for the attack. It just feeds the server with some valid data. We only care about how the server handles the *IV*.

We start by saving the *IV*. We will use it later. Then we generate a new initialization vector -we will refer to it as *proposed_IV*- and put next to it the *data*. We have to apply some changes (replacements, utf8 encoding, etc.) that are specific to this flag before making any get request to the server.

We then attack as explained in the [How PadBuster works](https://blog.gdssecurity.com/labs/2010/9/14/automated-padding-oracle-attacks-with-padbuster.html) write up.

We care about only two responses. An error response about invalid padding and one about any internal server error. There are internal several errors regarding this flag. Not every single one should be considered as successful attempt in finding a byte. Their frequency should be compared.

After we find the correct *proposed_IV* and the original plaintext for that specific block of data we move on to the next pair {(original IV, 1st data block), (1st data block, 2nd data block), (2nd data block, 3rd data block), ...} and make the same attack.

The deciphering for each block is independent of one another. So I run the attack on multiple threads for each block, the server seemed to handle this just fine, and then combined their results.

When using multiple threads (tested on an i7-1165G7 with 8 threads) it took ~20 minutes, instead of ~128 minutes when testing one block after another. The time is cut significantly.

The deciphered payload should look something like this:
`b'{"flag": "^FLAG^****************************************************************$FLAG$", "id": "11", "key": "b8pxpJxttgLbgIGtUZ1MDg~~"}\n\n\n\n\n\n\n\n\n'`


## Flag 2 - CBC byte flipping attack


### Usefull Info:

[CBC byte flipping 101](https://resources.infosecinstitute.com/topic/cbc-byte-flipping-attack-101-approach/)


### Accessing the situation:


### Execution:


