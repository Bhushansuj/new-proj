from pydantic import BaseModel

class Client(BaseModel):
    hostname: str
    ip: str
    status: str
