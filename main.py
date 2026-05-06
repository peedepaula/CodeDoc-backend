from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from routers import usuario_router, documentacao_router
from fastapi.staticfiles import StaticFiles

app = FastAPI()

origins = [
    'http://localhost:5173',
    'http://192.168.0.103:5173',
    'https://codedoc-d.pages.dev'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(usuario_router.router)
app.include_router(documentacao_router.router)

app.mount("/static", StaticFiles(directory="static"), name="static")

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