from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Module, Comment
from typing import List
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ratemyNUS API")

# CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        os.getenv("FRONTEND_URL")
    ],
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
    """
    Search modules by code or name
    Prioritizes exact code matches, then partial code matches, then name matches.
    """
    db = next(get_db())
    
    if not q or len(q.strip()) == 0:
        return []
    
    q_upper = q.upper().strip()
    
    # Search with prioritization:
    # 1. Exact code match
    # 2. Code starts with query
    # 3. Code contains query
    # 4. Name contains query
    
    modules = db.query(Module).filter(
        (Module.code.ilike(f"%{q}%")) | (Module.name.ilike(f"%{q}%"))
    ).all()
    
    # Sort by relevance
    def get_search_priority(module):
        code = module.code.upper()
        name = module.name.upper()
        
        # Exact match (highest priority)
        if code == q_upper:
            return 0
        
        # Starts with query (code)
        if code.startswith(q_upper):
            return 1
        
        # Contains query (code)
        if q_upper in code:
            return 2
        
        # Starts with query (name)
        if name.startswith(q_upper):
            return 3
        
        # Contains query (name)
        if q_upper in name:
            return 4
        
        # Shouldn't happen, but fallback
        return 5
    
    # Sort by priority, then alphabetically by code
    sorted_modules = sorted(modules, key=lambda m: (get_search_priority(m), m.code))
    
    # Limit to top 10 results
    return [
        {
            "code": m.code,
            "name": m.name,
            "comment_count": m.last_comment_count,
            "units": m.units,
            "semesters": m.semesters_available
        }
        for m in sorted_modules[:10]
    ]