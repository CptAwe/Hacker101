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
from flag_2 import byte_flip
result = byte_flip('a', True)
print(result.text)

