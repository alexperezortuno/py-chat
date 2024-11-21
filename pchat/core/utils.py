import random
import string

def generate_random_string(length) -> str:
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def messages_income(msg: dict) -> str:
    if msg['type'] in ['REGISTER', 'MESSAGE', 'CHANNELS', 'JOIN', 'LEAVE', 'CREATE_CHANNEL', 'CHANNEL_CREATED']:
        return msg['type']
    return 'UNKNOWN'
