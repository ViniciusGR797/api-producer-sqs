from uuid import uuid4
from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional
from schemas.transactions import TransactionSchema


class MetadataSchema(BaseModel):
    retries: int = Field(
        0,
        description="Número de tentativas de processamento da mensagem"
    )
    trace_id: Optional[str] = Field(
        default_factory=lambda: str(uuid4()),
        description="ID de rastreamento para logs e tracing"
    )


class MessageSchema(BaseModel):
    message_id: UUID4 = Field(
        ...,
        description="Identificador único global da mensagem (UUID)"
    )
    timestamp: datetime = Field(
        ...,
        description="Data e hora de criação da mensagem (UTC)"
    )
    source: str = Field(
        ...,
        description="Origem da mensagem, exemplo: 'transactions_api'"
    )
    type: str = Field(
        ...,
        description="Tipo de evento, exemplo: 'transaction_created'"
    )
    payload: TransactionSchema = Field(
        ...,
        description="Dados principais da mensagem (transação)"
    )
    metadata: MetadataSchema = Field(
        default_factory=MetadataSchema,
        description="Metadados da mensagem"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "123e4567-e89b-12d3-a456-426614174000",
                "timestamp": "2025-10-04T12:00:00Z",
                "source": "transactions_api",
                "type": "transaction_created",
                "payload": {
                    "transaction_id": "txn-908765",
                    "payer_id": "user-12345",
                    "receiver_id": "user-67890",
                    "amount": 250.75,
                    "currency": "BRL",
                    "description": "Donation to project X"
                },
                "metadata": {
                    "retries": 0,
                    "trace_id": "5bcb9f08-7dce-474e-aea5-7445ac1a174e"
                }
            }
        }


class QueueStatusSchema(BaseModel):
    queue_name: str = Field(
        ...,
        description="Nome da fila SQS consultada"
    )
    messages_available: int = Field(
        ...,
        description="Número aproximado de mensagens disponíveis na fila"
    )
    messages_in_flight: int = Field(
        ...,
        description="Número aproximado de mensagens em processamento na fila"
    )
    messages_delayed: int = Field(
        ...,
        description="Número aproximado de mensagens com delay na fila"
    )
    messages_in_dlq: int = Field(
        ...,
        description="Número aproximado de mensagens na fila morta associada"
    )

    class Config:
        schema_extra = {
            "example": {
                "queue_name": "main_queue",
                "messages_available": 15,
                "messages_in_flight": 2,
                "messages_delayed": 0,
                "messages_in_dlq": 3
            }
        }
