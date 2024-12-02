import time

from fastapi import APIRouter
from redis import Redis

from src.model import User, Message
from src.repository import UserRepository
from redis import Redis
from src.logic import generate_token

redis = Redis()
userRepo = UserRepository(redis)
router = APIRouter()

@router.post('/create_session')
def create_session(username: str, pub_key: str = ''):
    if len(userRepo.select(lambda user: user.username == username)) != 0:
        return {'ok': 0, 'message': 'Username has taken'}
    try:
        us_token = generate_token(32)
        user = User(username=username, token=us_token, public_key=pub_key)
        return {'ok': userRepo.add(user), 'token': us_token}
    except Exception as e:
        return {'ok': 0, 'message': e}


@router.post('/find_user')
def find_user(token: str, username: str):
    if len(userRepo.select(lambda user: user.token == token)) == 0:
        return {'ok': 0, 'message': 'Invalid token'}
    result = [(user.username, user.public_key) for user in userRepo.select(lambda user: username in user.username)]
    return {'ok': True, 'result': result}


@router.post('/send_message')
def send_message(token: str, to_username: str, text: str):
    from_user = userRepo.select(lambda user: user.token == token)
    if len(from_user) == 0:
        return {'ok': 0, 'message': 'Invalid token'}

    to_user = userRepo.select(lambda user: user.username == to_username)
    if len(to_user) != 1:
        return {'ok': 0, 'message': 'something went wrong'}

    fu: User = from_user[0]
    tu: User = to_user[0]

    msg = Message(timestamp=int(time.time()), from_username=fu.username, text=text)

    tu.messages.append(msg)

    userRepo.update(tu.id, tu)

    return {'ok': 1}


@router.post('/get_updates')
def get_updates(token: str):
    from_user = userRepo.select(lambda user: user.token == token)
    if len(from_user) == 0:
        return {'ok': 0, 'message': 'Invalid token'}
    user = from_user[0]
    result = [{'timestamp': msg.timestamp, 'username': msg.from_username, 'text': msg.text} for msg in user.messages]
    user.messages = []
    userRepo.update(user.id, user)
    return {'ok': 1, 'result': result}
