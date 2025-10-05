from fastapi import APIRouter, status, Depends
from middlewares.auth import auth_middleware
from controllers.messages import MessageController
from schemas.messages import MessageSchema, QueueStatusSchema
from schemas.transactions import TransactionSchema

router = APIRouter()


@router.post(
    "/send",
    response_model=MessageSchema,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth_middleware)]
)
async def send_transaction(data: TransactionSchema):
    return await MessageController.send(data.model_dump())


@router.get(
    "/status/{queue_name}",
    response_model=QueueStatusSchema,
    dependencies=[Depends(auth_middleware)]
)
async def get_status(queue_name: str):
    return await MessageController.get_status(queue_name)
