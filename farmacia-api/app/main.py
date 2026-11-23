# app/main.py
from fastapi import FastAPI

app = FastAPI(title="API de Farmacia", version="1.0.0")


@app.get("/")
def raiz() -> dict:
    return {"api": "farmacias", "docs": "/docs"}