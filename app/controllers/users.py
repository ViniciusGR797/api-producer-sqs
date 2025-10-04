from fastapi import HTTPException
from schemas.users import UserLoginSchema
from utils.config import Config
from utils.validate import validate
from security.password import compare_pwd, encrypt_pwd
from security.token import create_token


class UserController:
    @staticmethod
    async def login(data: dict):
        credentials, error = validate(UserLoginSchema, data)
        if error:
            raise HTTPException(status_code=422, detail=error)

        email = credentials.email
        password = credentials.pwd

        valid_email = Config.APP_USER_EMAIL
        hash_pwd = encrypt_pwd(Config.APP_USER_PASSWORD)

        if not valid_email or not hash_pwd:
            raise HTTPException(
                status_code=500,
                detail="Server configuration error")

        if email != valid_email or not compare_pwd(password, hash_pwd):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_token()
        return {'access_token': access_token}
