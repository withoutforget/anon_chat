from redis import Redis
from src.model import User

class UserRepository:
    __redis:Redis

    def __init__(self, redis:Redis):
        self.__redis = redis
        self.__redis.set('user:last_id', 0)

    def add(self, user:User):
        last_id = int(self.__redis.get('user:last_id'))
        user.id = last_id
        res = self.__redis.set(f'user:{last_id}', value = user.model_dump_json())
        self.__redis.set('user:last_id', last_id + 1)
        return res

    def select(self, key = None):
        last_id = int(self.__redis.get('user:last_id'))
        res = []
        for i in range(0, last_id):
            user = self.__redis.get(f'user:{i}')
            if user is None:
                continue
            user = User.model_validate_json(user)
            if key is not None and key(user):
                res.append(user)
        return res

    def update(self, idx:int, new_user:User):
        res = self.__redis.set(f'user:{idx}', value = new_user.model_dump_json())
        return res