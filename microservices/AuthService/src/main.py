from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import routers
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Auth Service")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1"],
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
    app.include_router(router)

