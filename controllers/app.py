from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from msprbloc4.models.db  import  SessionLocal, init_db
from msprbloc4.models.models import ClientModel
app = FastAPI(
    title="Client Service",
    description="Microservice de gestion des clients avec PostgreSQL",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ClientCreate(BaseModel):
    name: str
    email: str

class ClientRead(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        orm_mode = True


@app.post("/clients", response_model=ClientRead, status_code=201)
def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    # Vérifier si l'email existe déjà
    existing_client = db.query(ClientModel).filter(ClientModel.email == client.email).first()
    if existing_client:
        raise HTTPException(status_code=400, detail="Un client avec cet email existe déjà.")

    new_client = ClientModel(name=client.name, email=client.email)
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client

@app.get("/clients", response_model=List[ClientRead])
def get_clients(db: Session = Depends(get_db)):
    clients = db.query(ClientModel).all()
    return clients

@app.get("/clients/{client_id}", response_model=ClientRead)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable.")
    return client

@app.put("/clients/{client_id}", response_model=ClientRead)
def update_client(client_id: int, updated: ClientCreate, db: Session = Depends(get_db)):
    client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable.")

    if db.query(ClientModel).filter(ClientModel.email == updated.email, ClientModel.id != client_id).first():
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé par un autre client.")

    client.name = updated.name
    client.email = updated.email
    db.commit()
    db.refresh(client)
    return client

@app.delete("/clients/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = db.query(ClientModel).filter(ClientModel.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable.")
    db.delete(client)
    db.commit()
    return
@app.get("/db-status")
def db_status(db: Session = Depends(get_db)):
    try:
        result = db.execute("SELECT 1")
        return {"connected": True, "result": [row for row in result]}
    except Exception as e:
        return {"connected": False, "error": str(e)}