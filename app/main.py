from fastapi import FastAPI
from app.api.routers import router
from app.core.logging import init_logging

init_logging()

app = FastAPI(title='Aspectify ABSA Demo')
router(app)
