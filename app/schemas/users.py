from pydantic import BaseModel, EmailStr, Field

class UserLoginSchema(BaseModel):
    email: str
    pwd: str

class AccessTokenSchema(BaseModel):
    access_token: str = Field(..., description="JWT token gerado")
