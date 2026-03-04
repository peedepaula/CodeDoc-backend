from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from controller import usuario_controller

app = FastAPI()

origins = [
    'http://localhost:5173'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(usuario_controller.router)

@app.get("/")
def main():
    return {"mensagem": "servidor CodeDoc rodando!"}

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0",  port=8000)













# ¨¨¨¨ @p ¨¨¨¨
#    _____
#  /       \
# | /\   /\ |
#  \\/   \//
#   \  _  /
#    \___/ 
#     | |
#    /   \