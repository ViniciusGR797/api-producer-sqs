from fastapi import APIRouter
from controllers.users import UserController
from schemas.users import AccessTokenSchema, UserLoginSchema

router = APIRouter()


@router.post(
    "/login",
    response_model=AccessTokenSchema,
    responses={
        200: {"description": "Successful login"},
        400: {"description": "Invalid request"},
        401: {"description": "Invalid credentials"},
        500: {"description": "Internal server error"}
    },
    summary="User login",
    tags=["Users"]
)
async def login(data: UserLoginSchema):
    return await UserController.login(data.model_dump())
