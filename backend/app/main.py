from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from concurrent.futures import ThreadPoolExecutor
from app.database import SessionLocal
from app.models import Module, Comment
from app.pipeline import main as run_pipeline, MODULE_CODES, process_module
import asyncio
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
executor = ThreadPoolExecutor(max_workers=1)

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

@app.get("/api/run-pipeline")
async def trigger_pipeline():
    """
    Endpoint triggered by Vercel Cron.
    Runs the scraping and analysis pipeline.
    """
    # Run pipeline in background to avoid timeout
    loop = asyncio.get_event_loop()
    
    def run_in_thread():
        try:
            run_pipeline()
            return {"status": "success", "message": "Pipeline completed"}
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            return {"status": "error", "message": str(e)}
    
    # Start pipeline but don't wait for completion (runs in background)
    future = loop.run_in_executor(executor, run_in_thread)
    
    return {
        "status": "started",
        "message": "Pipeline started in background. Check logs for progress.",
        "scheduled_time": "Daily at 3:00 AM SGT"
    }

@app.get("/api/pipeline-status")
def pipeline_status():
    """
    Check which modules need attention.
    For debugging and testing purposes.
    """
    db = SessionLocal()
    
    all_modules = db.query(Module).all()
    
    status = {
        "needs_sentiment": [],
        "needs_update": [],
        "up_to_date": []
    }
    
    for module in all_modules:
        comment_count = db.query(Comment).filter(Comment.module_id == module.id).count()
        
        info = {
            "code": module.code,
            "comments": comment_count,
            "has_sentiment": bool(module.sentiment_data)
        }
        
        if comment_count > 0 and not module.sentiment_data:
            status["needs_sentiment"].append(info)
        elif comment_count != module.last_comment_count:
            status["needs_update"].append(info)
        else:
            status["up_to_date"].append(info)
    
    db.close()
    return status

@app.get("/api/populate-database")
async def populate_database():
    """
    Manually trigger database population.
    Run this ONCE after creating tables.
    Takes 5-10 minutes.
    """
    loop = asyncio.get_event_loop()

    # Run in separate thread to allow sync Playwright
    def run_population():
        db = SessionLocal()
        results = {"success": [], "failed": [], "errors": {}}
        
        for module_code in MODULE_CODES:
            try:
                logger.info(f"Processing {module_code}...")
                success = process_module(module_code, db)
                
                if success:
                    results["success"].append(module_code)
                    logger.info(f"✅ {module_code}")
                else:
                    results["failed"].append(module_code)
                    results["errors"][module_code] = "process_module returned False"
            except Exception as e:
                results["failed"].append(module_code)
                results["errors"][module_code] = str(e)
                logger.error(f"❌ {module_code}: {e}")
        
        db.close()
        return results
    
    # Run in thread pool
    results = await loop.run_in_executor(executor, run_population)
    
    return {
        "status": "complete",
        "processed": len(results["success"]) + len(results["failed"]),
        "successful": results["success"],
        "failed": results["failed"],
        "errors": results["errors"]
    }

@app.get("/api/populate-chunk/{start}/{end}")
async def populate_chunk(start: int, end: int):
    """
    Populate modules in chunks to avoid timeout.
    Example: /api/populate-chunk/0/3
    """
    loop = asyncio.get_event_loop()
    
    def run_chunk():
        db = SessionLocal()
        chunk = MODULE_CODES[start:end]
        results = {"success": [], "failed": [], "errors": {}, "chunk": f"{start}-{end}"}
        
        for module_code in chunk:
            try:
                success = process_module(module_code, db)
                if success:
                    results["success"].append(module_code)
                else:
                    results["failed"].append(module_code)
                    results["errors"][module_code] = "Failed"
            except Exception as e:
                results["failed"].append(module_code)
                results["errors"][module_code] = str(e)
        
        db.close()
        return results
    
    results = await loop.run_in_executor(executor, run_chunk)
    return results