from pydantic import BaseModel, Field


class LoginIn(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    password: str = Field(min_length=6, max_length=128)

class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    roles: list[str] = []

