import motor.motor_asyncio
url = "mongodb://kxlgpBrqQy:0XRH6rvwGA@157.241.44.9/?authSource=admin&readPreference=primary&directConnection=true&ssl=false"
client = motor.motor_asyncio.AsyncIOMotorClient(url)