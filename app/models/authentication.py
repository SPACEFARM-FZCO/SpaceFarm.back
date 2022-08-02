from pydantic import BaseModel
from typing import Optional

class Signin(BaseModel):
    email:str
    password:str


class Signup(Signin):
    name:str
    phone:str


class Code(BaseModel):
    code:str
    phone:str