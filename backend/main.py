from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Integer, String, select, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column, Session
from typing import Generator, Literal
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
import time
import logging

# --- CONFIGURACIÓN DE LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN DE SEGURIDAD ---
SECRET_KEY = os.getenv("SECRET_KEY", "una_clave_muy_secreta_123")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- APP FASTAPI ---
app = FastAPI(
    title="API de Demostración Didáctica",
    description="Backend con FastAPI + JWT + CI/CD",
    version="1.1.0"
)

Base = declarative_base()

# --- MODELOS DE BASE DE DATOS ---
class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

# --- ESQUEMAS PYDANTIC ---
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ItemCreate(BaseModel):
    name: str
    status: Literal["Pendiente", "En progreso", "Completado"]

class ItemUpdate(BaseModel):
    name: str | None = None
    status: Literal["Pendiente", "En progreso", "Completado"] | None = None

class ItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    status: str

# --- CONFIGURACIÓN DE BASE DE DATOS ---
def build_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        if database_url.startswith("mysql://"):
            return database_url.replace("mysql://", "mysql+pymysql://", 1)
        return database_url

    def require_env(name: str) -> str:
        value = os.getenv(name)
        if not value:
            raise RuntimeError(f"Missing required environment variable: {name}")
        return value

    db_user = require_env("DB_USER")
    db_password = require_env("DB_PASSWORD")
    db_host = require_env("DB_HOST")
    db_port = require_env("DB_PORT")
    db_name = require_env("DB_NAME")
    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(build_database_url(), pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# --- DEPENDENCIA DE DB (Definida antes de ser usada en Auth) ---
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- LÓGICA DE SEGURIDAD (Usa get_db) ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar el token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def seed_data(db: Session) -> None:
    existing = db.execute(select(Item)).scalars().first()
    if existing: return
    db.add_all([
        Item(name="Módulo CI/CD", status="Completado"),
        Item(name="Módulo Docker", status="En progreso"),
        Item(name="Módulo Despliegue", status="Pendiente"),
    ])
    db.commit()

# --- MIDDLEWARE & STARTUP ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup() -> None:
    max_retries = 10
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Intento {attempt}/{max_retries}: Conectando a la DB...")
            Base.metadata.create_all(bind=engine)
            with SessionLocal() as session:
                session.execute(select(1))
                seed_data(session)
            logger.info("✓ Conexión exitosa")
            break
        except Exception as e:
            if attempt == max_retries: raise
            time.sleep(5)

# --- RUTAS ---
@app.get("/")
async def root():
    return {"status": "online", "message": "Backend FastAPI Protegido con JWT"}

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    hashed = get_password_hash(user_data.password)
    user = User(username=user_data.username, hashed_password=hashed)
    db.add(user)
    db.commit()
    return {"message": "Usuario creado exitosamente"}

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales incorrectas")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/data")
async def get_data(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = db.execute(select(Item)).scalars().all()
    return {
        "items": [ItemOut.model_validate(item).model_dump() for item in items],
        "user_active": current_user.username
    }

@app.get("/api/items", response_model=list[ItemOut])
async def list_items(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    items = db.execute(select(Item)).scalars().all()
    return [ItemOut.model_validate(item) for item in items]

@app.post("/api/items", response_model=ItemOut, status_code=201)
async def create_item(payload: ItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = Item(name=payload.name, status=payload.status)
    db.add(item)
    db.commit()
    db.refresh(item)
    return ItemOut.model_validate(item)

@app.put("/api/items/{item_id}", response_model=ItemOut)
async def update_item(item_id: int, payload: ItemUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.get(Item, item_id)
    if not item: raise HTTPException(status_code=404, detail="Item not found")
    if payload.name is not None: item.name = payload.name
    if payload.status is not None: item.status = payload.status
    db.commit()
    db.refresh(item)
    return ItemOut.model_validate(item)

@app.delete("/api/items/{item_id}", status_code=204)
async def delete_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    item = db.get(Item, item_id)
    if not item: raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return None

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)