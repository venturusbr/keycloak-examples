from pydantic import BaseModel


class GoAroundMessage(BaseModel):
    message: str

class UserLogin(BaseModel):
    username: str
    password: str

class ClientCredentials(BaseModel):
    client_id: str
    client_secret: str