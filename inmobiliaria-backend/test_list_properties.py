import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import SessionLocal, Propiedad

def listar_propiedades():
    db = SessionLocal()
    try:
        propiedades = db.query(Propiedad).all()
        for p in propiedades:
            print(f"ID: {p.id}, Dirección: {p.direccion}, Descripción: {p.descripcion}, Precio: {p.precio}")
    finally:
        db.close()

if __name__ == "__main__":
    listar_propiedades()
