import random
import string


def generate_random_string(length) -> str:
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def messages_income(msg: dict) -> str:
    if msg['type'] in ['MESSAGE', 'CHANNELS', 'JOIN', 'JOIN_SUCCESS', 'LEAVE', 'CREATE_CHANNEL', 'CHANNEL_CREATED',
                       'CHANNEL_ERROR']:
        return msg['type']
    return 'UNKNOWN'
