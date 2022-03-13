from base64 import b64encode
from settings import CBC_BLOCKSIZE, ORIGINAL_PAYLOAD, TARGET
from help import replace_chars, xor2bytes, make_request

def byte_flip():

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
        b'{"id":"1", "i":"'
    )

    # Prepare the new payload for sending
    modified_payload = b''.join(data_of_interest_enc)
    modified_payload = b64encode(modified_payload)
    modified_payload = modified_payload.decode('utf-8')
    modified_payload = replace_chars(modified_payload, reverse=True)

    result = make_request(TARGET, modified_payload, True).text
    result = result.split('\n')[0]
    result = result[result.index('^FLAG^'): ]
    
    return result
