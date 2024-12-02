import string
import random

def generate_token(length: int) -> str:
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))