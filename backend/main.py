import os
import sys

# Prepend project root to sys.path to avoid import conflicts with third-party 'backend' package
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.database import engine
from backend.models.invoice import Base
from backend.routers import invoice, auth

# Create database tables automatically if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ScrapK Ventures Invoice API",
    description="Backend calculation engine for ScrapK Ventures B2B Invoice Generator",
    version="1.0.0"
)

# CORS Setup: Allow local frontend configurations to make requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Router
app.include_router(invoice.router, prefix="/api", tags=["Invoice"])
app.include_router(auth.router, prefix="/api", tags=["Auth"])

# Serve logo and static assets from frontend/
frontend_dir = os.path.join(project_root, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")

@app.get("/")
def home():
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "ScrapK Ventures B2B Invoice API is online. Frontend not found."}

@app.get("/invoice")
@app.get("/invoice.html")
def invoice_view():
    invoice_path = os.path.join(frontend_dir, "invoice.html")
    if os.path.exists(invoice_path):
        return FileResponse(invoice_path)
    return {"message": "Invoice viewer page not found."}

@app.get("/login")
@app.get("/login.html")
def login_view():
    login_path = os.path.join(frontend_dir, "login.html")
    if os.path.exists(login_path):
        return FileResponse(login_path)
    return {"message": "Login page not found."}