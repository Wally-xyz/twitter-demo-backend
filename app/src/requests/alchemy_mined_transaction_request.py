from pydantic import BaseModel


class AlchemyFullTransaction(BaseModel):
    hash: str
    gas: str
    gasPrice: str
    nonce: str


class AlchemyMinedTransaction(BaseModel):
    app: str
    network: str
    webhookType: str
    timestamp: str
    fullTransaction: AlchemyFullTransaction
