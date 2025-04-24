import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import SessionLocal, Usuario, get_password_hash

def test_create_user():
    db = SessionLocal()
    try:
        # Crear un nuevo usuario
        nuevo_usuario = Usuario(
            nombre="Test User",
            email="testuser@example.com",
            hashed_password=get_password_hash("testpassword")
        )
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        print(f"Usuario creado con ID: {nuevo_usuario.id}")
    finally:
        db.close()

if __name__ == "__main__":
    test_create_user()
