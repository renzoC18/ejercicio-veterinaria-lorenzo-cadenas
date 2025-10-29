from fastapi import APIRouter
from pydantic import BaseModel
import mysql.connector
from dotenv import load_dotenv
import os
load_dotenv()

router_veterinario = APIRouter(prefix="/veterinario")

class Veterinario(BaseModel):
    id: str
    email: str
    age: int
    is_admin: bool

class VetBD:
    def __init__(self, host = "localhost", user = "root", password = "", database = "veterinaria_DB"):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
            }
            
        self._crear_tabla()

    def _get_connection(self):
        return mysql.connector.connect(**self.config)
    
    def _crear_tabla(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS veterinarios (
                id VARCHAR(50) PRIMARY KEY,
                email VARCHAR(100),
                age INT,
                is_admin BOOLEAN
            )
        """)
        conn.commit()
        conn.close()

    def create(self, vet: Veterinario):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO veterinarios (id, email, age, is_admin)
            VALUES (%s, %s, %s, %s)
        """, (vet.id, vet.email, vet.age, vet.is_admin))
        conn.commit()
        conn.close()

    def update(self, vet: Veterinario):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE veterinarios
            SET email = %s, age = %s, is_admin = %s
            WHERE id = %s
        """, (vet.email, vet.age, vet.is_admin, vet.id))
        conn.commit()
        conn.close()

    def get_all(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM veterinarios")
        row = cursor.fetchall()
        conn.close()
        return [Veterinario(id=r[0], email=r[1], age=r[2], is_admin=r[3]) for r in row]
    
    def get_by_id(self, vet_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM veterinarios WHERE id = %s", (vet_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Veterinario(id=row[0], email=row[1], age=row[2], is_admin=row[3])
        return HTTPException(status_code=404, detail="Veterinario no encontrado")

class VeterinarioService:
    def __init__(self, DB: VetBD):
        self.bd = DB

    def create_veterinario(self, vet: Veterinario):
        self.bd.create(vet)
        return vet

    def update_veterinario(self, vet: Veterinario):
        self.bd.update(vet)
        return vet

    def get_all_veterinarios(self):
        return self.bd.get_all()

    def get_veterinario_by_id(self, vet_id: str):
        return self.bd.get_by_id(vet_id)

DB = VetBD(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

@router_veterinario.post("/create")
async def create_veterinario(vet: Veterinario):
    return service.create_veterinario(vet)

@router_veterinario.post("/update")
async def update_veterinario(vet: Veterinario):
    return service.update_veterinario(vet)

@router_veterinario.get("/all")
async def get_all_veterinarios():
    return service.get_all_veterinarios()

@router_veterinario.get("/{vet_id}")
async def get_veterinario(vet_id: str):
    return service.get_veterinario_by_id(vet_id)
