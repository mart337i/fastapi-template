from pydantic import BaseModel

class User(BaseModel):
    hostname: str
    username: str
    password: str