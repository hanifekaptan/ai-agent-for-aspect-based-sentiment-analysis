from fastapi import FastAPI
from app.api import analyze as analyze_module
from app.api import health as health_module


def router(app: FastAPI):
    app.include_router(analyze_module.router)
    app.include_router(health_module.router)


__all__ = ['router']
