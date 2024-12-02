from redis import Redis

from src.model import User


class UserRepository:
    __redis:Redis

    def __init__(self, redis:Redis):
        self.__redis = redis

    async def get(self, username: str) -> User | None:
        res = await self.__redis.get(f'user:{username}')
        if res is None:
            return None
        return User.model_validate_json(res)

    async def add(self, user: User) -> bool:
        if self.get(user.username) is not None:
            return False
        return await self.__redis.set(f'user:{user.username}', user.model_dump_json())

    async def update(self, user: User) -> bool:
        return await self.__redis.set(f'user:{user.username}', user.model_dump_json())

    def get_users(self, template: str, func=lambda _: True) -> list[User]:
        return [User.model_validate_json(key) for key in self.__redis.scan_iter(template) if
                func(User.model_validate_json(key))]
