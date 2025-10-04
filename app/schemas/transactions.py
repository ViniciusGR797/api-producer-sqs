from pydantic import BaseModel, Field, PositiveFloat
from typing import Optional

class TransactionSchema(BaseModel):
    transaction_id: str = Field(..., description="Identificador único da transação gerado pela API")
    payer_id: str = Field(..., description="Identificador do usuário pagador")
    receiver_id: str = Field(..., description="Identificador do usuário recebedor")
    amount: PositiveFloat = Field(..., description="Valor da transação (positivo)")
    currency: str = Field(..., description="Moeda da transação, exemplo: 'BRL', 'USD'")
    description: Optional[str] = Field(None, description="Descrição opcional da transação")

    class Config:
        json_schema_extra = {
            "example": {
                "transaction_id": "txn-908765",
                "payer_id": "user-12345",
                "receiver_id": "user-67890",
                "amount": 250.75,
                "currency": "BRL",
                "description": "Doação para projeto X"
            }
        }