'''
Keep the global variables organized
'''

from help import replace_chars
from base64 import b64decode
import os

__LINK = "http://35.190.155.168/13041c545c/?post=opjdpixztsUmd9FPxsy7-dMpTMdxjSmEFDAU!gyiG6FwTphUDBY-PNzFM3yb0IGqbaD4FQ2hW!S80XB1AYRiMxFXp-cLdKIq068aBXk6HrUQ1w!EfiAwdhaMGZ0Pf3uUmPxlGOcdtrA3QkH5jem!tYH20qr4DYXJtImJ5qVobq1AKC6n-iMJS8w5S0yfsa1yyHhjPQOUxWALAP7Zi6GFVg~~"

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
