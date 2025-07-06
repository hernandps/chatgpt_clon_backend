from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import database
import models
from database import engine, Base
from schemas import UserCreate
from auth import hash_password
from fastapi import HTTPException, status
from schemas import UserLogin, Token
from auth import verify_password, create_access_token
from auth import get_current_user
from models import User as DBUser  # para tipado opcional
from database import get_db
from fastapi import Security
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer
from schemas import MessageCreate, MessageOut
from models import Message
from typing import List
from fastapi.middleware.cors import CORSMiddleware



security_scheme = HTTPBearer()

app = FastAPI()

# Permitir solicitudes desde frontend
origins = [
    "http://localhost:3000",  # si usas el puerto 3000
    "http://localhost:3001",  # tu frontend actual
    "https://chatgpt-clon-frontend.onrender.com",  # si lo subes a producción también
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)


# Dependencia para obtener una sesión de base de datos


@app.get("/")
def root(db: Session = Depends(get_db)):
    return {"message": "Conexión a base de datos exitosa"}


@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el email ya existe
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado"
        )

    # Crear nuevo usuario
    hashed_pw = hash_password(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_pw,role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Usuario creado correctamente", "user_id": new_user.id}

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
def read_me(
    current_user: DBUser = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Security(security_scheme)
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }


@app.post("/messages", response_model=MessageOut)
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Security(security_scheme)
):
    new_message = Message(
        user_id=current_user.id,
        content=message.content
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

@app.get("/messages", response_model=List[MessageOut])
def get_messages(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Security(security_scheme)
):
    return db.query(Message).filter(Message.user_id == current_user.id).order_by(Message.timestamp).all()