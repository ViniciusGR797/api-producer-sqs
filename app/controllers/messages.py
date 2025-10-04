from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from services.messages import MessageService
from schemas.messages import MessageSchema
from schemas.transactions import TransactionSchema
from utils.validate import validate

class MessageController:
    @staticmethod
    async def send(data: dict):
        transaction, error = validate(TransactionSchema, data)
        if error:
            raise HTTPException(status_code=422, detail=error)        

        message = MessageSchema(
            message_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            source="transactions_api",
            type="transaction_created",
            payload=transaction
        )

        error = MessageService.send_to_queue(message)
        if error:
            raise HTTPException(status_code=500, detail=error)

        return message