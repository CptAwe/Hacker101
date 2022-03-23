'''
Keep the global variables organized
'''

from help import replace_chars
from base64 import b64decode
import os

__LINK = "https://056e9c8318ac6614e73f0ee49715e414.ctf.hacker101.com/?post=cP!bfCY!X7egyROKxj2EcZymfK14VJ5-vgZ9bkp6Un0t-A86C!-wmcTQOycIN45ITxAoCp-XSipxg5hoXIQn715Dl4IRG5MyDF7FkvQBOZ-q4t78nNoNjSumuNkbI1mkMoRjP6gekBuwNsPpzz5pXx7ijTCqKjWtEyd8cQK2V3qzeERkfU!uMKTDKkBRlQcbLai2!ILnk!Oc8GgoZvllzQ~~"

TARGET, ORIGINAL_PAYLOAD = __LINK.split("?post=")
TARGET += "?post="

CBC_BLOCKSIZE = 16

# Make multiple requests at the same time
USE_THREADS = True

# Decrapify the original payload
ORIGINAL_PAYLOAD = replace_chars(ORIGINAL_PAYLOAD, reverse=False)
ORIGINAL_PAYLOAD =  b64decode(ORIGINAL_PAYLOAD)

NUM_OF_BLOCKS = int(len(ORIGINAL_PAYLOAD)/CBC_BLOCKSIZE)


FLAG_1_SKIPS_FILE_LOCATION = os.path.join("4-Encrypted Pastebin", "skips", "flag_1_skips.json")
FLAG_3_SKIPS_FILE_LOCATION = os.path.join("4-Encrypted Pastebin", "skips", "flag_3_skips.json")
