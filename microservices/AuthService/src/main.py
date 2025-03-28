from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from microservices.AuthService.src.config import settings
from api import routers

app = FastAPI(title="Auth Service")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Access-Control-Allow-Headers",
        "Content-Type",
        "Authorization",
        "Access-Control-Allow-Origin",
        "Set-Cookie",
        "cache-control",
    ],
)

for router in routers:
    app.include_router(routers)

if __name__ == "__main__":
    uvicorn.run(
        app,
        port=settings.SERVICE_PORT,
        workers=settings.WORKERS,
        reload=settings.DEV_MODE,
    )
