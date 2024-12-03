from redis import Redis

from src.model import User

EXP_TIME = 10

class UserRepository:
    __redis:Redis

    def __init__(self, redis:Redis):
        self.__redis = redis

    def get(self, username: str) -> User | None:
        res = self.__redis.get(f'user:{username}')
        if res is None:
            return None
        return User.model_validate_json(res)

    def add(self, user: User) -> bool:
        r = self.get(user.username)
        if self.get(user.username) is not None:
            return False
        return self.__redis.set(f'user:{user.username}', user.model_dump_json(), ex=EXP_TIME)

    def update(self, user: User) -> bool:
        return self.__redis.set(f'user:{user.username}', user.model_dump_json(), ex=EXP_TIME)

    def update_timeout(self, username: str, token: str) -> bool:
        user = self.__redis.get(f'user:{username}')
        if user is None: return False
        user = User.model_validate_json(user)
        user.token = token
        return self.__redis.set(name=f'user:{username}', value=user.model_dump_json(), ex=EXP_TIME)

    def get_timeout(self, username: str) -> int:
        time = self.__redis.expiretime(f'user:{username}')
        if time == -2:
            return 0
        return time

    def get_users(self, template: str, func=lambda _: True) -> list[User]:

        keys = [key for key in self.__redis.scan_iter(template)]
        data = [self.__redis.get(k) for k in keys]
        data = [User.model_validate_json(k) for k in data]
        data = [k for k in data if func(k)]
        return data
