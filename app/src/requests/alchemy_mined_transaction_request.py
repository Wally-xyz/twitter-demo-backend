from pydantic import BaseModel


class AlchemyFullTransaction(BaseModel):
    hash: str


class AlchemyMinedTransaction(BaseModel):
    app: str
    network: str
    webhookType: str
    timestamp: str
    fullTransaction: AlchemyFullTransaction
