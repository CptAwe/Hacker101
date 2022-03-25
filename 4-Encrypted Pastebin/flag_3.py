from settings import CBC_BLOCKSIZE, FLAG_3_SKIPS_FILE_LOCATION, TARGET
from help import add2bytes, make_request, ENCODING, xor2bytes
import json
import os

allSolutions = {}# To keep the solutions safe
RANDOM_DATA =[ b'A']*CBC_BLOCKSIZE# Random data for the end of the payload for the first loop
EMPTY_DATA = [b'\x00']*CBC_BLOCKSIZE

def __addPadding(text: str|bytes):
    '''Adds padding'''
    if len(text) > CBC_BLOCKSIZE:
        raise ValueError(f"Can't add padding to block, it exceeds the CBC block size ({len(text)}, should be <= {CBC_BLOCKSIZE})")
    
    bytes_left = CBC_BLOCKSIZE - len(text)
    if type(text) == str:
        text = text.encode(ENCODING)
    text = text + bytes([bytes_left])*bytes_left

    return text

def __splitIntoBlocks(text: str | bytes):
    '''Splits the text into blocks of the appropriate block size'''

    blocks = [
        text[i: i+CBC_BLOCKSIZE].encode(ENCODING) if type(text) == str
            else text[i: i+CBC_BLOCKSIZE]
        for i in range(0, len(text), CBC_BLOCKSIZE)
    ]

    if len(blocks[-1]) < CBC_BLOCKSIZE:
        blocks[-1] = __addPadding(blocks[-1])
    else:
        # A new block of padding needs to be added
        last_block = __addPadding(b'')
        blocks.append(last_block)

    return blocks

def __load_skips():
    '''
    Loads the skips
    '''
    if not os.path.isfile(FLAG_3_SKIPS_FILE_LOCATION):
        return None

    with open(FLAG_3_SKIPS_FILE_LOCATION, 'r') as skips_file:
        skips = skips_file.read()

        skips = json.loads(skips)
    
    return skips

def __save_skips(skips: dict):
    '''
    Saves the skips to a json file
    '''

    with open(FLAG_3_SKIPS_FILE_LOCATION, 'w') as skips_file:
        skips = json.dumps(skips, sort_keys=True, indent=4)
        skips_file.write(skips)

def __fetch_intermediary_for_block(num_of_block: int, last_block: bytes, solutions: dict = None):
    '''Actually uses the padding oracle attack to find the intermidiate bytes by encrypting an empty string and testing it against the server'''

    global allSolutions

    if not solutions:
        solutions = {}

    # The first payload is all zeroes
    proposed_payload = EMPTY_DATA.copy()

    # Test to see if the server thinks the message has valid encoding
    for num_of_byte in range(-1, -CBC_BLOCKSIZE-1, -1):

        how_much_to_add = 0
        if str(num_of_byte) in solutions:
            how_much_to_add = solutions[str(num_of_byte)]

        while True:

            payload_temp = proposed_payload.copy()

            # prepare the payload
            payload_temp[num_of_byte] = add2bytes(
                payload_temp[num_of_byte],
                bytes([how_much_to_add])
            )
            payload_temp = b''.join(payload_temp)

            try:
                result = make_request(
                    TARGET,
                    payload=payload_temp + b''.join(last_block)# Add the random data at the end
                )
                print(f"\rBlock #{num_of_block}, Byte #{abs(num_of_byte): >3}/{CBC_BLOCKSIZE} was summed with {how_much_to_add: <3} to create the payload {str(payload_temp): <67} -> {result}", end='\r')
            except Exception as e:
                allSolutions[str(num_of_block)][str(num_of_byte)] = how_much_to_add
                __save_skips(allSolutions)
                raise ValueError(f"\nThe following error has occurred:\n{e.args}\nI have already saved the progress...")

            if '0' not in result:
                # A propable byte of the message has been found
                byte_solution = payload_temp[num_of_byte:]

                # Save the solution
                solutions[str(num_of_byte)] = how_much_to_add
                allSolutions[str(num_of_block)][str(num_of_byte)] = how_much_to_add

                # Calculate what valid padding we caused
                caused_valid_padding = bytes([abs(num_of_byte)]*abs(num_of_byte))

                # We can now XOR these bytes (or byte) with the padding we caused to get the intermediary byte
                intermediary = xor2bytes(byte_solution, caused_valid_padding)
                
                print(f"\nBlock #{num_of_block}, Byte #{abs(num_of_byte): >3}/{CBC_BLOCKSIZE} after adding {how_much_to_add}/255: Caught {byte_solution}")
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
                    proposed_payload[xor_res_byte_ind] = xor_res_byte
                break
            
            # Add 1 bit to the byte
            how_much_to_add += 1
            if how_much_to_add>=256:
                # No solution has been found, something is wrong
                raise Exception("\nAll responses were the same. Have you found the error that talks about the padding?")

    print(f"Block #{num_of_block}: A solution has been found: {intermediary}")

    return num_of_block, intermediary, solutions


def padding_oracle_encrypt(message: str, use_skips: bool = True):
    '''Wrapper for executing __fetch_intermediary_for_block() for each block of the message '''

    # Make a test message to find the valid encoding
    message_blocks = __splitIntoBlocks(message)

    # prepare the global variable for the solutions
    global allSolutions
    if use_skips:
        allSolutions = __load_skips()
    else:
        for i in range(len(message_blocks)):
            allSolutions[str(i)] = {}

    intermediaries = {}
    for reverse_block_index in range(-1, -len(message_blocks)-1, -1):

        num_of_block = len(message_blocks) - abs(reverse_block_index)
        
        message_block = message_blocks[num_of_block]
        message_block = [bytes([i]) for i in message_block]

        if reverse_block_index == -1:# If it is the last block, add random data to the end of it, else the previous block
            last_block = RANDOM_DATA
        else:
            last_block = xor2bytes(intermediary, message_blocks[num_of_block+1])
            last_block = [bytes([i]) for i in last_block]

        # Use the skip
        skips = allSolutions[str(num_of_block)] if str(num_of_block) in allSolutions else None

        try:
            _, intermediary, solutions4block = __fetch_intermediary_for_block(
                num_of_block=num_of_block,
                last_block=last_block,
                solutions=skips
            )
        except Exception as e:
            raise e

        # The block has finished, save the skips and the intermediary
        allSolutions[str(num_of_block)] = solutions4block
        intermediaries[num_of_block] = intermediary
        __save_skips(allSolutions)

    return intermediaries

def prepareMessage(message: str, intermediaries: dict):
    '''
    XORs each block of the message with the respective block of the intermediary.
    Returns the result as bytes.
    '''

    message_blocks = __splitIntoBlocks(message)

    XORed_message = []
    for index, msg_block in enumerate(message_blocks):
        inter = intermediaries[index]
        XORed_message.append(xor2bytes(msg_block, inter))
    
    ending = b''.join(RANDOM_DATA)
    XORed_message.append(ending)
    XORed_message = b''.join(XORed_message)
    return XORed_message


