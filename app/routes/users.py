from fastapi import APIRouter
from controllers.users import UserController
from schemas.users import AccessTokenSchema, UserLoginSchema

router = APIRouter()

@router.post("/login", response_model=AccessTokenSchema,
             responses={
                 200: {"description": "Login bem-sucedido"},
                 400: {"description": "Requisição inválida"},
                 401: {"description": "Credenciais inválidas"},
                 500: {"description": "Erro interno"}
             },
             summary="Login do usuário",
             tags=["Users"])
async def login(data: UserLoginSchema):
    return await UserController.login(data.dict())
