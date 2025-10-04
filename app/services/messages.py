import boto3
from schemas.messages import MessageSchema
from utils.config import Config


class MessageService:
    @staticmethod
    def send_to_queue(
        message: MessageSchema,
        queue_url: str = Config.SQS_MAIN_QUEUE,
        message_group_id: str = "default-group"
    ):
        try:
            sqs_client = boto3.client("sqs", region_name=Config.REGION)
            sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=message.model_dump_json(),
                MessageGroupId=message_group_id,
                DeduplicationId=message.message_id
            )
            return None
        except Exception as e:
            return f"Error sending message to SQS: {str(e)}"
