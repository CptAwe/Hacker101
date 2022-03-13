from base64 import b64encode
from settings import CBC_BLOCKSIZE, ORIGINAL_PAYLOAD, TARGET
from help import replace_chars, xor2bytes, make_request

def byte_flip(custom_id: str = None, return_raw = False):

    if custom_id:
        if len(custom_id) != 1:
            raise ValueError("Only a custom id of length 1 is supported")
    else:
        custom_id = "1"

    data_of_interest_enc = []
    for block in range(5, 9+1):
        data_of_interest_enc.append(
            ORIGINAL_PAYLOAD[CBC_BLOCKSIZE*block : CBC_BLOCKSIZE*(block+1)] # Blocks #5 - #9
        )

    # Modify the new IV to be valid (`****block #5****` XOR  `$FLAG$", "id": "` => `{"id":"1", "i":"`)
    data_of_interest_enc[0] = xor2bytes(
        data_of_interest_enc[0],
        b'$FLAG$", "id": "'
    )
    data_of_interest_enc[0] = xor2bytes(
        data_of_interest_enc[0],
        b'{"id":"%s", "i":"'%(custom_id.encode('utf-8'))
    )

    # Prepare the new payload for sending
    modified_payload = b''.join(data_of_interest_enc)
    modified_payload = b64encode(modified_payload)
    modified_payload = modified_payload.decode('utf-8')
    modified_payload = replace_chars(modified_payload, reverse=True)

    result = make_request(TARGET, modified_payload, True)
    if return_raw:
        return result

    result = result.text.split('\n')[0]
    result = result[result.index('^FLAG^'): ]
    
    return result
