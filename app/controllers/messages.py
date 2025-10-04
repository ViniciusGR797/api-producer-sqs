from uuid import uuid4
from datetime import datetime
from fastapi import HTTPException
from schemas.messages import MessageSchema
from schemas.transactions import TransactionSchema
from utils.config import Config
from utils.validate import validate
from security.password import compare_pwd, encrypt_pwd
from security.token import create_token

class MessageController:
    @staticmethod
    async def send(data: dict):
        transaction, error = validate(TransactionSchema, data)
        if error:
            raise HTTPException(status_code=422, detail=error)        

        message = MessageSchema(
            message_id=uuid4(),
            timestamp=datetime.utcnow(),
            source="transactions_api",
            type="transaction_created",
            payload=transaction
        )

        # aqui você enviaria a message ao SQS
        # sqs.send_message(...)

        return message