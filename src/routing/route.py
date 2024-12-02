import time
from http.client import HTTPException

from fastapi import APIRouter, HTTPException
from redis import Redis

from src.logic import generate_token, decrypt_token
from src.model import User, Message
from src.repository import UserRepository

redis = Redis(host='localhost', port=6379, db=0)
userRepo = UserRepository(redis)
router = APIRouter()


def validate_token(token: str) -> dict:
    userdata = decrypt_token(token)
    if userdata is None:
        raise HTTPException(status_code=418, detail='Invalid token')
    return userdata
@router.post('/create_session')
async def create_session(username: str, pub_key: str = ''):
    token = generate_token(username)

    user = User(username=username, token=token, public_key=pub_key)

    if not await userRepo.add(user):
        raise HTTPException(status_code=418, detail='Username has taken')

    return {'token': token}

@router.post('/find_user')
def find_user(token: str, username: str):
    userdata = validate_token(token)
    users = userRepo.get_users(template='user:*', func=lambda user: username in user.username)
    return {'result': [(u.username, u.public_key) for u in users]}


@router.post('/send_message')
async def send_message(token: str, to_username: str, text: str):
    userdata = validate_token(token)
    user = await userRepo.get(to_username)
    user.messages.append(Message(timestamp=int(time.time()), from_username=userdata['username'], text=text))
    return {'ok': await userRepo.update(user)}

@router.post('/get_updates')
async def get_updates(token: str):
    userdata = validate_token(token)
    user = await userRepo.get(userdata['username'])
    msgs = [{'timestamp': msg.timestamp, 'username': msg.from_username, 'text': msg.text} for msg in user.messages]
    user.messages = []
    res = await userRepo.update(user)
    if not res:
        return {'ok': 0}
    return {'ok': 1, 'result': msgs}
