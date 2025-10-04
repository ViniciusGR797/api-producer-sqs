from fastapi import APIRouter, status
from controllers.messages import MessageController
from schemas.messages import MessageSchema
from schemas.transactions import TransactionSchema

router = APIRouter()

@router.post(
    "/send", 
    response_model=MessageSchema, 
    status_code=status.HTTP_201_CREATED
)
async def send_transaction(data: TransactionSchema):
    return await MessageController.send(data.model_dump())