class UserController:
    @staticmethod
    async def login(data: dict):
        return {"access_token": "token"}