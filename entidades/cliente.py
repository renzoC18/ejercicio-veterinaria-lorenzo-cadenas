from fastapi import APIRouter
from pydantic import BaseModel
router_cliente = APIRouter()
class Cliente(BaseModel):
    id: str
    email: str
    age: int
    is_admin: bool

@router_cliente.post("/cliente")
async def save_user(user: Cliente):
    return user

@router_cliente.get("/cliente/{user_id}")
async def get_user(user_id: str):
    return {"user_id": user_id, "message": "Detalles del cliente"}

