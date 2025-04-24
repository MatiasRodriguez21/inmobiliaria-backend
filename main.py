from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta

# Configuración de la base de datos SQLite
# Define la URL de conexión a la base de datos SQLite y configura el motor de SQLAlchemy
SQLALCHEMY_DATABASE_URL = "sqlite:///./inmobiliaria.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# Crea una clase SessionLocal para manejar las sesiones de la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base para los modelos declarativos de SQLAlchemy
Base = declarative_base()

# Modelos de la base de datos
# Define la tabla "usuarios" con sus columnas y relaciones
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    reservas = relationship("Reserva", back_populates="usuario")

# Define la tabla "propiedades" con sus columnas y relaciones
class Propiedad(Base):
    __tablename__ = "propiedades"
    id = Column(Integer, primary_key=True, index=True)
    direccion = Column(String, index=True)
    descripcion = Column(String)
    precio = Column(Integer)

    reservas = relationship("Reserva", back_populates="propiedad")

# Define la tabla "reservas" con sus columnas y relaciones
class Reserva(Base):
    __tablename__ = "reservas"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    propiedad_id = Column(Integer, ForeignKey("propiedades.id"))
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)

    usuario = relationship("Usuario", back_populates="reservas")
    propiedad = relationship("Propiedad", back_populates="reservas")

# Crear tablas
# Crea todas las tablas definidas en la base de datos
Base.metadata.create_all(bind=engine)

# Esquemas Pydantic
# Define los esquemas para validación y serialización de datos con Pydantic
class ReservaBase(BaseModel):
    fecha_inicio: datetime
    fecha_fin: datetime

class ReservaCreate(ReservaBase):
    usuario_id: int
    propiedad_id: int

class ReservaOut(ReservaBase):
    id: int
    usuario_id: int
    propiedad_id: int

    class Config:
        from_attributes = True  # Cambiado de orm_mode para compatibilidad con Pydantic v2

class PropiedadBase(BaseModel):
    direccion: str
    descripcion: str
    precio: int

class PropiedadCreate(PropiedadBase):
    pass

class PropiedadOut(PropiedadBase):
    id: int

    class Config:
        from_attributes = True  # Cambiado de orm_mode para compatibilidad con Pydantic v2

class UsuarioBase(BaseModel):
    nombre: str
    email: str

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioOut(UsuarioBase):
    id: int

    class Config:
        from_attributes = True  # Cambiado de orm_mode para compatibilidad con Pydantic v2

# Seguridad y autenticación
# Configuración para la generación y verificación de tokens JWT y manejo de contraseñas
SECRET_KEY = "secretkey1234567890"  # Cambiar por un valor seguro en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Bienvenido a la API REST de gestión inmobiliaria. Visita /docs para la documentación interactiva."}

# Función para hashear la contraseña
def get_password_hash(password):
    return pwd_context.hash(password)

# Función para verificar la contraseña
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Función para obtener un usuario por email
def get_user(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

# Función para autenticar un usuario
def authenticate_user(db: Session, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

# Función para crear un token de acceso JWT
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Dependencia para obtener el usuario actual a partir del token
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(lambda: SessionLocal())):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(db, email=email)
    if user is None:
        raise credentials_exception
    return user

# Dependencia para obtener la sesión de la base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rutas para autenticación
# Endpoint para obtener el token de acceso mediante usuario y contraseña
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Usuario o contraseña incorrectos")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.email}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

# Rutas para usuarios
# Endpoint para crear un nuevo usuario
@app.post("/usuarios/", response_model=UsuarioOut)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_user = get_user(db, email=usuario.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    hashed_password = get_password_hash(usuario.password)
    db_usuario = Usuario(nombre=usuario.nombre, email=usuario.email, hashed_password=hashed_password)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

# Endpoint para listar usuarios
@app.get("/usuarios/", response_model=List[UsuarioOut])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usuarios = db.query(Usuario).offset(skip).limit(limit).all()
    return usuarios

# Rutas para propiedades
# Endpoint para crear una nueva propiedad (requiere autenticación)
@app.post("/propiedades/", response_model=PropiedadOut)
def crear_propiedad(propiedad: PropiedadCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    db_propiedad = Propiedad(**propiedad.dict())
    db.add(db_propiedad)
    db.commit()
    db.refresh(db_propiedad)
    return db_propiedad

# Endpoint para listar propiedades
@app.get("/propiedades/", response_model=List[PropiedadOut])
def listar_propiedades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    propiedades = db.query(Propiedad).offset(skip).limit(limit).all()
    return propiedades

# Rutas para reservas
# Endpoint para crear una nueva reserva (requiere autenticación)
@app.post("/reservas/", response_model=ReservaOut)
def crear_reserva(reserva: ReservaCreate, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    db_reserva = Reserva(**reserva.dict())
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    return db_reserva

# Endpoint para listar reservas (requiere autenticación)
@app.get("/reservas/", response_model=List[ReservaOut])
def listar_reservas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    reservas = db.query(Reserva).offset(skip).limit(limit).all()
    return reservas
