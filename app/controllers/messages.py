import json
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
from services.messages import MessageService
from schemas.messages import MessageSchema, QueueStatusSchema
from schemas.transactions import TransactionSchema
from utils.validate import validate


class MessageController:
    @staticmethod
    async def send(data: dict, queue_name: str):
        transaction, err = validate(TransactionSchema, data)
        if err:
            raise HTTPException(status_code=422, detail=err)

        message = MessageSchema(
            message_id=uuid4(),
            timestamp=datetime.now(timezone.utc),
            source="transactions_api",
            type="transaction_created",
            payload=transaction
        )
        message_group_id = "default-group"

        sqs_client, err = MessageService.get_sqs_client()
        if err:
            raise HTTPException(status_code=500, detail=err)

        queue_url, err = MessageService.get_queue_url(sqs_client, queue_name)
        if err:
            raise HTTPException(status_code=500, detail=err)

        err = MessageService.send_to_queue(
            sqs_client, message, queue_url, message_group_id)
        if err:
            raise HTTPException(status_code=500, detail=err)

        return message

    @staticmethod
    async def get_status(queue_name: str):
        sqs_client, err = MessageService.get_sqs_client()
        if err:
            raise HTTPException(status_code=500, detail=err)

        queue_url, err = MessageService.get_queue_url(sqs_client, queue_name)
        if err:
            raise HTTPException(status_code=500, detail=err)

        attrs, err = MessageService.get_queue_attributes(
            sqs_client,
            queue_url,
            [
                "ApproximateNumberOfMessages",
                "ApproximateNumberOfMessagesNotVisible",
                "ApproximateNumberOfMessagesDelayed"
            ]
        )
        if err:
            raise HTTPException(status_code=500, detail=err)

        messages_in_dlq = 0
        dlq_url, err = MessageService.get_dlq_url(sqs_client, queue_url)
        if err:
            raise HTTPException(status_code=500, detail=err)
        if dlq_url:
            dlq_attrs, err = MessageService.get_queue_attributes(
                sqs_client,
                dlq_url,
                ["ApproximateNumberOfMessages"]
            )
            if err:
                raise HTTPException(status_code=500, detail=err)
            messages_in_dlq = dlq_attrs.get("ApproximateNumberOfMessages", 0)

        return QueueStatusSchema(
            queue_name=queue_name,
            messages_available=attrs.get(
                "ApproximateNumberOfMessages", 0),
            messages_in_flight=attrs.get(
                "ApproximateNumberOfMessagesNotVisible", 0),
            messages_delayed=attrs.get(
                "ApproximateNumberOfMessagesDelayed", 0),
            messages_in_dlq=messages_in_dlq
        )

    @staticmethod
    async def reprocess_dlq(queue_name: str):
        sqs_client, err = MessageService.get_sqs_client()
        if err:
            raise HTTPException(status_code=500, detail=err)

        queue_url, err = MessageService.get_queue_url(sqs_client, queue_name)
        if err:
            raise HTTPException(status_code=500, detail=err)

        dlq_url, err = MessageService.get_dlq_url(sqs_client, queue_url)
        if err:
            raise HTTPException(status_code=500, detail=err)

        while True:
            messages, err = MessageService.get_messages(sqs_client, dlq_url)
            if err:
                raise HTTPException(status_code=500, detail=err)
            if not messages:
                break

            for msg in messages:
                body_dict = json.loads(msg["Body"])
                body = MessageSchema(**body_dict)
                message_group_id = "default-group"

                err = MessageService.send_to_queue(
                    sqs_client, body, queue_url, message_group_id)
                if err:
                    raise HTTPException(status_code=500, detail=err)

                err = MessageService.delete_message(
                    sqs_client, dlq_url, msg["ReceiptHandle"])
                if err:
                    raise HTTPException(status_code=500, detail=err)

        return {"message": "Reprocessing completed"}
