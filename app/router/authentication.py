from requests import request
from config import server
from config.mongodb import client
from core.authentication.main import Authentication
from fastapi import APIRouter, Response,  Request
from models.authentication import *
router = APIRouter(prefix=server.Server_config.prefix,
                   responses=server.Server_config.responses,
                   tags=['authentication'])


@router.post("/auth/login")
async def signin(user:Signin,response: Response):
    return await Authentication.signin(user,response)
 
@router.get("/auth/user")
async def signin(request:Request):
    return await Authentication.verify(request)


@router.post("/auth/reg")
async def signin(user:Signup,response: Response):
    return await Authentication.signup(user,request)

@router.post("/auth/code")
async def activation_code(user:Code,response: Response):
    print(user)
    return user

