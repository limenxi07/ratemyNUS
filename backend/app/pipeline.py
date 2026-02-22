import httpx
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert
from app.database import SessionLocal
from app.models import Module, Comment
from app.scraper import scrape_module_reviews
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NUSMODS_API_BASE = "https://api.nusmods.com/v2/2024-2025/modules"
MODULE_CODES = [
    "GEA1000", "CS1010", "CS1101S", "CS2030S", "CS2040S", 
    "CS2100", "MA1521", "MA1522", "ST2334", "IS1108", 
    "IS2218", "CS1231S", "CS2106", "CS2103"
]


# ============================================================================
# API CLIENT
# ============================================================================

def fetch_module_metadata(module_code: str) -> Optional[Dict]:
    """Fetch module metadata from NUSMods API."""
    url = f"{NUSMODS_API_BASE}/{module_code}.json"
    
    try:
        response = httpx.get(url, timeout=10.0)
        
        if response.status_code == 404:
            logger.warning(f"Module {module_code} not found in API")
            return None
        
        if response.status_code != 200:
            logger.error(f"API returned {response.status_code} for {module_code}")
            return None
        
        data = response.json()
        semesters = [str(s["semester"]) for s in data.get("semesterData", []) if "semester" in s]
        metadata = {
            "code": data.get("moduleCode"),
            "name": data.get("title"),
            "description": data.get("description", ""),
            "units": int(data.get("moduleCredit", 0)),
            "semesters_available": semesters,
            "url": f"https://nusmods.com/courses/{module_code}"
        }
        
        logger.info(f"Fetched metadata for {module_code}")
        return metadata
        
    except Exception as e:
        logger.error(f"Error fetching API for {module_code}: {e}")
        return None


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def upsert_module(db: Session, metadata: Dict) -> Module:
    """Insert or update module in database."""
    stmt = insert(Module).values(
        code=metadata["code"],
        name=metadata["name"],
        description=metadata["description"],
        units=metadata["units"],
        semesters_available=metadata["semesters_available"],
        url=metadata["url"]
    ).on_conflict_do_update(
        index_elements=["code"],
        set_={
            "name": metadata["name"],
            "description": metadata["description"],
            "units": metadata["units"],
            "semesters_available": metadata["semesters_available"],
            "url": metadata["url"]
        }
    ).returning(Module)
    
    result = db.execute(stmt)
    db.commit()
    
    module = result.scalar_one()
    logger.info(f"Upserted module {metadata['code']}")
    return module


def replace_module_comments(db: Session, module_id: int, comments: List[Dict]):
    """
    Delete old comments and insert new ones for a module.
    """
    # Delete old
    deleted = db.query(Comment).filter(Comment.module_id == module_id).delete()
    logger.info(f"Deleted {deleted} old comments for module_id {module_id}")
    
    # Insert new
    if comments:
        comment_objects = [
            Comment(
                module_id=module_id,
                text=c["text"],
                posted_date=c["posted_date"],
                upvotes=c.get("upvotes", 0)
            )
            for c in comments
        ]
        db.add_all(comment_objects)
    
    # Set sufficient review flag
    module = db.query(Module).filter(Module.id == module_id).first()
    if module:
        module.has_sufficient_reviews = len(comments) > 3
        db.commit()
        logger.info(f"Inserted {len(comments)} new comments")


def update_module_comment_count(db: Session, module_id: int, count: int):
    """Update the last_comment_count for a module."""
    module = db.query(Module).filter(Module.id == module_id).first()
    if module:
        module.last_comment_count = count
        db.commit()


# ============================================================================
# ORCHESTRATION
# ============================================================================

def process_module(module_code: str, db: Session) -> bool:
    """
    Complete pipeline for one module.
    Returns True if success, False if failed.
    """
    logger.info(f"\n{'='*60}\nProcessing {module_code}\n{'='*60}")
    
    try:
        # Step 1: Fetch metadata
        metadata = fetch_module_metadata(module_code)
        if not metadata:
            logger.error(f"Failed to fetch metadata for {module_code}")
            return False
        
        # Step 2: Upsert module
        module = upsert_module(db, metadata)
        
        # Step 3: Scrape comments
        comments, error = scrape_module_reviews(module_code)
        
        if error == "not_found":
            logger.warning(f"{module_code} reviews not found")
            update_module_comment_count(db, module.id, 0)
            return True
        
        if error == "scrape_failed":
            logger.error(f"Failed to scrape {module_code}")
            return False
        
        if error == "no_reviews":
            logger.info(f"{module_code} has no reviews")
            update_module_comment_count(db, module.id, 0)
            return True
        
        # Step 4: Replace comments
        replace_module_comments(db, module.id, comments)
        update_module_comment_count(db, module.id, len(comments))
        
        logger.info(f"✅ {module_code} complete ({len(comments)} comments)")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error processing {module_code}: {e}")
        db.rollback()
        return False


def main():
    """Run the full pipeline for all modules."""
    db = SessionLocal()
    
    success_count = 0
    failed_modules = []
    
    for module_code in MODULE_CODES:
        if process_module(module_code, db):
            success_count += 1
        else:
            failed_modules.append(module_code)
    
    db.close()
    
    # Summary
    logger.info(f"\n{'='*60}\nPIPELINE COMPLETE\n{'='*60}")
    logger.info(f"✅ Success: {success_count}/{len(MODULE_CODES)}")
    logger.info(f"❌ Failed: {len(failed_modules)}/{len(MODULE_CODES)}")
    
    if failed_modules:
        logger.info(f"Failed modules: {', '.join(failed_modules)}")


if __name__ == "__main__":
    main()