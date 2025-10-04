from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from utils.config import Config
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
        queue_url = Config.SQS_MAIN_QUEUE
        message_group_id = "default-group"

        error = MessageService.send_to_queue(
            message, queue_url, message_group_id)
        if error:
            raise HTTPException(status_code=500, detail=error)

        return message

    @staticmethod
    async def get_status(queue_name: str):
        # status_data, error = MessageService.get_queue_status(queue_name)
        # if error:
        #     raise HTTPException(status_code=500, detail=error)
        return queue_name
