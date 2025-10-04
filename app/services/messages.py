import json
import boto3
from schemas.messages import MessageSchema
from utils.config import Config

class MessageService:
    @staticmethod
    def send_to_queue(message: MessageSchema, queue_url: str = Config.SQS_MAIN_QUEUE):
        try:
            sqs_client = boto3.client("sqs", region_name=Config.AWS_REGION)
            sqs_client.send_message(
                QueueUrl=queue_url,
                MessageBody=message.model_dump_json()
            )
            return None
        except Exception as e:
            return f"Erro ao enviar mensagem para SQS: {str(e)}"
