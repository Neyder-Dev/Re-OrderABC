from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

db = SessionLocal()

# Verificar si ya existe
import os

ADMIN_EMAIL    = os.environ.get("ADMIN_EMAIL", "admin@reordena.com")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin2024!")

existente = db.query(User).filter(User.email == ADMIN_EMAIL).first()
if existente:
    print(f"Usuario ya existe: {existente.email} | activo={existente.is_active}")
else:
    jefe = User(
        nombre="Administrador",
        email=ADMIN_EMAIL,
        hashed_password=hash_password(ADMIN_PASSWORD),
        rol="jefe",
    )
    db.add(jefe)
    db.commit()
    print("Usuario jefe creado exitosamente")

db.close()
