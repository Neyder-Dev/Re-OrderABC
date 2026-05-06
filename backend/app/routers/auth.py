from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password,
    create_access_token, get_current_user, require_jefe
)
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        User.email == data.email,
        User.is_active == True
    ).first()

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    token = create_access_token({"sub": user.email, "rol": user.rol})
    return TokenResponse(access_token=token, usuario=user)


@router.post("/usuarios", response_model=UserResponse, dependencies=[Depends(require_jefe)])
def crear_usuario(data: UserCreate, db: Session = Depends(get_db)):
    existente = db.query(User).filter(User.email == data.email).first()
    if existente:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    if data.rol not in ["jefe", "operario"]:
        raise HTTPException(status_code=400, detail="Rol inválido. Use 'jefe' u 'operario'")

    user = User(
        nombre=data.nombre,
        email=data.email,
        hashed_password=hash_password(data.password),
        rol=data.rol,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.get("/usuarios", response_model=list[UserResponse], dependencies=[Depends(require_jefe)])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(User).all()