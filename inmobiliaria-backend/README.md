# Inmobiliaria API REST

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.95.0-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## Descripción

API REST desarrollada con **FastAPI** para la gestión de inmboliaria, que permite administrar usuarios, propiedades y reservas de manera eficiente y segura.

Cuenta con autenticación basada en JWT y utiliza **SQLite** como base de datos ligera para facilitar el desarrollo y despliegue.

---

## Características principales

- Gestión completa de usuarios con registro y autenticación.
- CRUD para propiedades y reservas.
- Documentación interactiva automática con Swagger UI.
- Base de datos SQLite integrada y fácil de usar.
- Código modular y escalable.

---

## Tecnologías

- Python 3.8+
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Passlib (para hashing de contraseñas)
- Python-JOSE (para JWT)

---

## Instalación

1. Clonar el repositorio:

```bash
git clone <URL_DE_TU_REPOSITORIO>
cd inmobiliaria-backend
```

2. Crear y activar un entorno virtual (opcional pero recomendado):

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

---

## Uso

1. Ejecutar el servidor:

```bash
uvicorn main:app --reload
```

2. Acceder a la documentación interactiva:

[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

3. Desde la documentación puedes:

- Crear usuarios.
- Obtener token JWT para autenticación.
- Crear, listar y gestionar propiedades.
- Crear, listar y gestionar reservas.

---

## Scripts de prueba

- `test_save_user.py`: crea un usuario de prueba.
- `test_list_users.py`: lista usuarios existentes.
- `test_list_properties.py`: lista propiedades existentes.

---

## Notas

- El archivo `inmobiliaria.db` no está incluido en el repositorio y se genera automáticamente.
- Para crear propiedades y reservas es necesario autenticarse con un token JWT válido.
- El archivo `.gitignore` está configurado para ignorar archivos temporales y la base de datos.

---

## Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo LICENSE para más detalles.

---

## Contacto

Para dudas o sugerencias, puedes contactarme.

---

> Proyecto de ejemplo para aprender a crear APIs REST modernas y seguras con FastAPI y SQLite.
