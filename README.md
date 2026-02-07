# Supplier-Consumer Backend

Learning project: building a complete backend for supplier–consumer platform using FastAPI, PostgreSQL, and JWT auth.

In cmd:
venv\Scripts\activate.bat - activate venv

Then to test:
uvicorn app.main:app --reload

for updating or creating schema: alembic upgrade head

for changes: alembic revision --autogenerate -m "..."
