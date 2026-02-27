from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Module, Comment
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ratemyNUS API")

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "ratemyNUS API"}


@app.get("/api/modules")
def get_all_modules():
    """Get all modules (code, name, comment_count, units only)"""
    db = next(get_db())
    
    modules = db.query(Module).all()
    
    return [
        {
            "code": m.code,
            "name": m.name,
            "comment_count": m.last_comment_count,
            "units": m.units,
            "semesters": m.semesters_available,
            "sentiment_data": m.sentiment_data,
        }
        for m in modules
    ]


@app.get("/api/modules/{code}")
def get_module(code: str):
    """Get one module with metadata (no individual comments fetched)"""
    db = next(get_db())
    
    # Case-insensitive search
    module = db.query(Module).filter(Module.code.ilike(code)).first()
    
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    return {
        "code": module.code,
        "name": module.name,
        "description": module.description,
        "url": module.url,
        "units": module.units,
        "semesters": module.semesters_available,
        "comment_count": module.last_comment_count,
        "has_sufficient_reviews": module.has_sufficient_reviews,
        "sentiment_data": module.sentiment_data,
    }


@app.get("/api/search")
def search_modules(q: str):
    """Search modules by code or name"""
    db = next(get_db())
    
    # Search by code OR name (case-insensitive, partial match)
    modules = db.query(Module).filter(
        (Module.code.ilike(f"%{q}%")) | (Module.name.ilike(f"%{q}%"))
    ).limit(10).all()
    
    return [
        {
            "code": m.code,
            "name": m.name,
            "comment_count": m.last_comment_count,
            "units": m.units,
            "semesters": m.semesters_available
        }
        for m in modules
    ]