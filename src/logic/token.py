import time

import jwt

JWT_KEY = 'ABCD'


def generate_token(username: str) -> str:
    curr_time = int(time.time())
    exp_time = 5 * 60 * 1000
    payload = {
        'username': username,
        'timestamp': curr_time,
        'exp': curr_time + exp_time
    }
    res = jwt.encode(payload=payload, key=JWT_KEY, algorithm='HS256')
    return res


def decrypt_token(token: str) -> dict | None:
    try:
        res: dict = jwt.decode(token, key=JWT_KEY, algorithms=['HS256'])
        return res
    except Exception as e:
        return None
