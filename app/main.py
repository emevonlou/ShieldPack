from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routes.passwords import router as passwords_router

app = FastAPI(
    title="ShieldPack",
    description="Detector de vazamento de dados com foco em privacidade",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(passwords_router, prefix="/api")

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def read_root():
    return FileResponse("app/static/index.html")
