from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Any


class UserLoginSchema(BaseModel):
    email: EmailStr
    pwd: str

    @field_validator("pwd")
    def validate_password(cls, v: Any) -> str:
        if not isinstance(v, str):
            raise ValueError("Password must be a string")
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v


class AccessTokenSchema(BaseModel):
    access_token: str = Field(..., description="JWT token gerado")
