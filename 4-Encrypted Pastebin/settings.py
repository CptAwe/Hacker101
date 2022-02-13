'''
Keep the global variables organized
'''

from help import replace_chars
from base64 import b64decode

TARGET = f"http://35.190.155.168/253cd950e7/?post="
ORIGINAL_PAYLOAD = "H9Ne8B6YCCj2Jw1ZA8QAZPvwZfkUQfXGd53MeACTl5hYFWrHHyZf5NCAQQKpixlylNxi42ASNMBkNwK2s9y2cifno86SfR1bilUjzhysbBjDjwfmEsCGYey1YV!o4j2svwJMeWWljmWxueGU8m!u1S!J9L6NA7W4SNR64YdW6JprGquVj6ggoCTPeguf2AjiIHMQ4ETGUH--cVAOyh-SsA~~"

CBC_BLOCKSIZE = 16

# Make multiple requests at the same time
USE_THREADS = False

# Decrapify the original payload
ORIGINAL_PAYLOAD = replace_chars(ORIGINAL_PAYLOAD, reverse=False)
ORIGINAL_PAYLOAD =  b64decode(ORIGINAL_PAYLOAD)

NUM_OF_BLOCKS = int(len(ORIGINAL_PAYLOAD)/CBC_BLOCKSIZE)