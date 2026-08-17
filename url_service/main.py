from fastapi import FastAPI
from url_service.url_routes import router

app = FastAPI()

app.include_router(router)