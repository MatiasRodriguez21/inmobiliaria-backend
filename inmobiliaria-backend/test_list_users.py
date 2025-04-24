import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import SessionLocal, Usuario

def test_list_users():
    db = SessionLocal()
    try:
        usuarios = db.query(Usuario).all()
        for usuario in usuarios:
            print(f"ID: {usuario.id}, Nombre: {usuario.nombre}, Email: {usuario.email}")
    finally:
        db.close()

if __name__ == "__main__":
    test_list_users()
