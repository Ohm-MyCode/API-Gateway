from fastapi import FastAPI
from auth_service.auth_routes import router

app = FastAPI()

app.include_router(router)