from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from router import winrenboard,authentication
app = FastAPI()

app.include_router(winrenboard.router)
app.include_router(authentication.router)

@app.middleware("http")
async def add_process(request: Request, call_next):
#try:
        response = await call_next(request)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    #except: 
      #  return Response(status_code=409)
  
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
