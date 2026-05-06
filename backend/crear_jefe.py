from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import hash_password

db = SessionLocal()

# Verificar si ya existe
existente = db.query(User).filter(User.email == "jefe@barentz.com").first()
if existente:
    print(f"Usuario ya existe: {existente.email} | activo={existente.is_active}")
else:
    jefe = User(
        nombre="Administrador",
        email="jefe@barentz.com",
        hashed_password=hash_password("Barentz2024"),
        rol="jefe",
    )
    db.add(jefe)
    db.commit()
    print("Usuario jefe creado exitosamente")

db.close()
