from core.authentication.utils import *
from models.authentication import *
from config.mongodb import client
from fastapi import Response,Request,HTTPException

import random
import uuid
class Authentication:

    async def signin(user:Signin,response: Response):
        user = await client.spacefarm.users.find_one({"email":user.email,"password":await get_hash_password(user.password)})
        if not user:
            raise HTTPException(status_code=409,detail="Incorrect login or password")
        if  user["activ"]:
            token = await create_access_token({"email":user['email'],"data":"dev"})
            response.set_cookie(key="access_token", value=token)
            return {"access_token":token}
        else:
            raise HTTPException(status_code=429,detail="Your account is not activated")

    async def signup(user:Signup,request:Request):
        print(user)
        if await client.spacefarm.users.find_one({"email":user.email}):
            raise HTTPException(status_code=409,detail="The user is already registered in the system")
        user = dict(user)
        activation_code = random.randint(000000,999999)
        user['code'] = {"value":activation_code,"exp":int(datetime.now().timestamp())}
        user['password'] = await get_hash_password(user['password'])
        user['_id'] = str(uuid.uuid4())
        user['activ'] = False
        client.spacefarm.users.insert_one(user)
        return 

    async def verify(request:Request):
        verify = await get_info_on_session_token(request)
        if not verify:
            raise HTTPException(status_code=403)
        #return "dev"
        return {"user":{"email":verify['email']}}
        return


    async def activation_code(user:Code):
        user  = await client.spacefarm.users.find_one({"phone":user.phone,"code.vlue":user.code})
        #if int(datetime.now().timestamp()) - user['code']['exp'] <:
        if user:
            client.spacefarm.users.update_one({"phone":user.phone},{"$set":{'code':{},"activ":True}})
        else:
            #Отправить сообщение
            raise HTTPException(status_code="Invalid activation code, try again.")
        return