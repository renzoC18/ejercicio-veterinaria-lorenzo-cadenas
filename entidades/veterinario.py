# veterinario_module.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from abc import ABC, abstractmethod
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# ===================================================
# MODELO (SRP)
# ===================================================
class Veterinario(BaseModel):
    id: str
    email: str
    age: int
    is_admin: bool


# ===================================================
# REPOSITORIO (OCP + ISP)
# ===================================================
class VeterinarioRepository(ABC):
    """Interfaz para acceso a datos de veterinarios."""

    @abstractmethod
    def create(self, vet: Veterinario): ...
    
    @abstractmethod
    def update(self, vet: Veterinario): ...
    
    @abstractmethod
    def get_all(self) -> list[Veterinario]: ...
    
    @abstractmethod
    def get_by_id(self, vet_id: str) -> Veterinario | None: ...


# ===================================================
# IMPLEMENTACIÓN CONCRETA MySQL (Cumple OCP)
# ===================================================
class MySQLVeterinarioRepository(VeterinarioRepository):
    def __init__(self, host, user, password, database):
        self.config = {
            "host": host,
            "user": user,
            "password": password,
            "database": database
        }

    def _get_connection(self):
        return mysql.connector.connect(**self.config)

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
        rows = cursor.fetchall()
        conn.close()
        return [Veterinario(id=r[0], email=r[1], age=r[2], is_admin=r[3]) for r in rows]

    def get_by_id(self, vet_id: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM veterinarios WHERE id = %s", (vet_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Veterinario(id=row[0], email=row[1], age=row[2], is_admin=row[3])
        return None


# ===================================================
# SERVICIO (Cumple DIP)
# ===================================================
class VeterinarioService:
    """Lógica de negocio (no depende de implementación concreta)."""
    def __init__(self, repository: VeterinarioRepository):
        self.repository = repository

    def create_veterinario(self, vet: Veterinario):
        self.repository.create(vet)
        return vet

    def update_veterinario(self, vet: Veterinario):
        if not self.repository.get_by_id(vet.id):
            raise HTTPException(status_code=404, detail="Veterinario no encontrado")
        self.repository.update(vet)
        return vet

    def get_all_veterinarios(self):
        return self.repository.get_all()

    def get_veterinario_by_id(self, vet_id: str):
        vet = self.repository.get_by_id(vet_id)
        if not vet:
            raise HTTPException(status_code=404, detail="Veterinario no encontrado")
        return vet


# ===================================================
# INICIALIZADOR DE BASE DE DATOS (SRP)
# ===================================================
def initialize_database(host, user, password, database):
    conn = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
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


# ===================================================
# ROUTER (Inyección de dependencias - DIP)
# ===================================================
router_veterinario = APIRouter(prefix="/veterinario")

# Crea la base de datos y el repositorio una sola vez
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

initialize_database(**DB_CONFIG)

repository = MySQLVeterinarioRepository(**DB_CONFIG)
service = VeterinarioService(repository)


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
