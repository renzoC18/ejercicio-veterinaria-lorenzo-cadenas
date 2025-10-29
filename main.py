from fastapi import FastAPI
from pydantic import BaseModel
from entidades.veterinario import router_veterinario as router_vet
from entidades.cliente import router_cliente as router_user

app = FastAPI()
app.include_router(router_vet)
#app.include_router(router_user)

@app.get("/")
async def root():
    return {"message": "Sistema de Veterinarios y Clientes"}
