'''
Keep the global variables organized
'''

from help import replace_chars
from base64 import b64decode
import os

TARGET = f"http://35.190.155.168/6e75b7be15/?post="
ORIGINAL_PAYLOAD = "V2UdEul6nB9mssW!ygK6nPsBRMJkzyL7DPXNRblqSApeeBiTzXjnaMrFK72wcXSIZmH7-KI9HTLibbxt4WPL98iCTn4AsD9huJppib6b!rjM6OP8FQDwBRLJV1-ZkHBoayofiyfjR!EqEhVDJew-Qo-xh6A35NaKd9jitAxLUyg7BMnKFrASQbt3H9HEjZAWP8VQxwdSmoWWtDih8WuQug~~"

CBC_BLOCKSIZE = 16

# Make multiple requests at the same time
USE_THREADS = True

# Decrapify the original payload
ORIGINAL_PAYLOAD = replace_chars(ORIGINAL_PAYLOAD, reverse=False)
ORIGINAL_PAYLOAD =  b64decode(ORIGINAL_PAYLOAD)

NUM_OF_BLOCKS = int(len(ORIGINAL_PAYLOAD)/CBC_BLOCKSIZE)


SKIPS_FILE_LOCATION = "4-Encrypted Pastebin"+os.sep+"skips.json"
