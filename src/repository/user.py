from redis import Redis

from src.model import User


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
        print(r)
        if self.get(user.username) is not None:
            return False
        return self.__redis.set(f'user:{user.username}', user.model_dump_json())

    def update(self, user: User) -> bool:
        return self.__redis.set(f'user:{user.username}', user.model_dump_json())

    def get_users(self, template: str, func=lambda _: True) -> list[User]:
        keys = [key for key in self.__redis.scan_iter(template)]
        data = [self.__redis.get(k) for k in keys]
        data = [User.model_validate_json(k) for k in data]
        data = [k for k in data if func(k)]
        return data
