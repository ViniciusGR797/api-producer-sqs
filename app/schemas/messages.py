from uuid import uuid4
from pydantic import BaseModel, Field, UUID4, PositiveFloat
from datetime import datetime
from typing import Optional
from schemas.transactions import TransactionSchema

class MetadataSchema(BaseModel):
    retries: int = Field(0, description="Número de tentativas de processamento da mensagem")
    trace_id: Optional[str] = Field(uuid4(), description="ID de rastreamento para logs e tracing")

class MessageSchema(BaseModel):
    """
    Representa a mensagem completa enviada ao SQS, com controle de idempotência.
    """
    message_id: UUID4 = Field(..., description="Identificador único global da mensagem (UUID)")
    timestamp: datetime = Field(..., description="Data e hora de criação da mensagem (UTC)")
    source: str = Field(..., description="Origem da mensagem, exemplo: 'transactions_api'")
    type: str = Field(..., description="Tipo de evento, exemplo: 'transaction_created'")
    payload: TransactionSchema = Field(..., description="Dados principais da mensagem (transação)")
    metadata: MetadataSchema = Field(default_factory=MetadataSchema, description="Metadados da mensagem")

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
                    "description": "Doação para projeto X"
                },
                "metadata": {
                    "retries": 0,
                    "trace_id": "abc123xyz456"
                }
            }
        }