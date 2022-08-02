from config.authentication import Authentication

from datetime import datetime,timedelta
from fastapi import Request

import hashlib
import jwt

async def get_hash_password(password:str):
    hash_password = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), Authentication.SECRET_KEY_PASSWORD,100000)
    return str(Authentication.SECRET_KEY_PASSWORD) + str(hash_password)

async def create_access_token(data: dict):
    data.update({"exp": datetime.now() + timedelta(hours=1280000) })
    encoded_jwt = jwt.encode(data, Authentication.SECRET_KEY_AUTH, algorithm=Authentication.ALGORITHM)
    return encoded_jwt 


async def get_info_on_session_token(request: Request):
    try:    
        if 'authorization' in request.headers:
            token = request.headers['authorization'].replace("Bearer ","")
        else:
            if 'access_token' in request.cookies:
                token = request.cookies['access_token']
            else:
                return False
        #проверять по базе
        payload = jwt.decode(str(token), Authentication.SECRET_KEY_AUTH, algorithms=[Authentication.ALGORITHM])
        return payload
    except:
        return False