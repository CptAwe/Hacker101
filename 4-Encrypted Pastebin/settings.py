'''
Keep the global variables organized
'''

from help import replace_chars
from base64 import b64decode
import os

__LINK = "https://1e6b5b5dda6efd0cf0edeae6ef41e5e0.ctf.hacker101.com/?post=vxkRSNvy4ADEDPB3dDaukJknllu1WWuVI!6uT6kGbAgEwW7xYeja5FhNlQLSKG5Mha0rT6SSEY7-DYOpilR1ixM5Y!Qbh9TY3HyaGIK8!f1MDAVWhF5yrw1fDwo1z87h48V!TkhTXIE5-bGKDK4tJJvCINQ2!eaxH1XUEDkRfKHO9dnIg00M3QEy8xG0hjwZqypbUnqM6YQk494K6NTtRQ~~"

TARGET, ORIGINAL_PAYLOAD = __LINK.split("?post=")
TARGET += "?post="

CBC_BLOCKSIZE = 16

# Make multiple requests at the same time
USE_THREADS = True

# Decrapify the original payload
ORIGINAL_PAYLOAD = replace_chars(ORIGINAL_PAYLOAD, reverse=False)
ORIGINAL_PAYLOAD =  b64decode(ORIGINAL_PAYLOAD)

NUM_OF_BLOCKS = int(len(ORIGINAL_PAYLOAD)/CBC_BLOCKSIZE)


SKIPS_FILE_LOCATION = "4-Encrypted Pastebin"+os.sep+"skips.json"
