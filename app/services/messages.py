import json
import boto3
from schemas.messages import MessageSchema
from utils.config import Config


class MessageService:
    @staticmethod
    def send_to_queue(
        message: MessageSchema,
        queue_url: str,
        message_group_id: str
    ):
        try:
            sqs_client = boto3.client("sqs", region_name=Config.REGION)
            sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=message.model_dump_json(),
                MessageGroupId=message_group_id,
                MessageDeduplicationId=str(message.message_id)
            )
            return None
        except Exception as e:
            return f"Error sending message to SQS: {str(e)}"


    @staticmethod
    def get_queue_status(queue_name: str):
        try:
            sqs_client = boto3.client("sqs", region_name=Config.REGION)
            queue_url = sqs_client.get_queue_url(QueueName=queue_name)["QueueUrl"]

            attrs = sqs_client.get_queue_attributes(
                QueueUrl=queue_url,
                AttributeNames=[
                    "ApproximateNumberOfMessages",
                    "ApproximateNumberOfMessagesNotVisible",
                    "ApproximateNumberOfMessagesDelayed",
                    "RedrivePolicy"
                ]
            )["Attributes"]

            messages_in_dlq = 0
            redrive_policy = attrs.get("RedrivePolicy")
            if redrive_policy:
                dlq_arn = json.loads(redrive_policy).get("deadLetterTargetArn")
                if dlq_arn:
                    dlq_name = dlq_arn.split(":")[-1]
                    dlq_url = sqs_client.get_queue_url(QueueName=dlq_name)["QueueUrl"]
                    dlq_attrs = sqs_client.get_queue_attributes(
                        QueueUrl=dlq_url,
                        AttributeNames=["ApproximateNumberOfMessages"]
                    )["Attributes"]
                    messages_in_dlq = int(dlq_attrs.get("ApproximateNumberOfMessages", 0))

            return {
                "queue_name": queue_name,
                "messages_available": int(attrs.get("ApproximateNumberOfMessages", 0)),
                "messages_in_flight": int(attrs.get("ApproximateNumberOfMessagesNotVisible", 0)),
                "messages_delayed": int(attrs.get("ApproximateNumberOfMessagesDelayed", 0)),
                "messages_in_dlq": messages_in_dlq
            }, None
        except Exception as e:
            return None, f"Error getting SQS queue status: {str(e)}"