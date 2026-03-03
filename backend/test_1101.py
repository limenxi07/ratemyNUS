import sys
from app.database import SessionLocal
from app.models import Module
from app.sentiment import analyze_module_sentiment
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
MOD = "CS1101S"  # Default module code for testing

def test_single_module(module_code: str = MOD):
    """
    Clear and re-run sentiment analysis for a single module.
    Useful for testing during development.
    """
    db = SessionLocal()
    
    # Find the module
    module = db.query(Module).filter(Module.code == module_code).first()
    
    if not module:
        logger.error(f"❌ Module {module_code} not found in database")
        logger.info("Available modules:")
        all_modules = db.query(Module).all()
        for m in all_modules:
            logger.info(f"  - {m.code}")
        db.close()
        return
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing sentiment analysis for {module_code}")
    logger.info(f"{'='*60}\n")
    
    # Clear existing sentiment data
    logger.info(f"🗑️  Clearing existing sentiment data...")
    module.sentiment_data = None
    module.has_sufficient_reviews = False
    db.commit()
    
    # Check comment count
    from app.models import Comment
    comment_count = db.query(Comment).filter(Comment.module_id == module.id).count()
    logger.info(f"📊 Module has {comment_count} comments in database")
    
    if comment_count == 0:
        logger.warning(f"⚠️  No comments found. Run pipeline first to scrape comments.")
        db.close()
        return
    
    # Run sentiment analysis
    logger.info(f"🤖 Running sentiment analysis...\n")
    success = analyze_module_sentiment(db, module.id)
    
    if success:
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ SUCCESS - Sentiment analysis complete for {module_code}")
        logger.info(f"{'='*60}")
        
        # Show results
        db.refresh(module)
        if module.sentiment_data:
            logger.info(f"\nResults preview:")
            if module.sentiment_data.get('insufficient_data'):
                logger.info(f"  - Insufficient data (≤3 reviews)")
            else:
                logger.info(f"  - Workload: {module.sentiment_data.get('workload', 'N/A')}")
                logger.info(f"  - Difficulty: {module.sentiment_data.get('difficulty', 'N/A')}")
                logger.info(f"  - Average: {module.sentiment_data.get('average', 'N/A')}")
                logger.info(f"  - Summary: {module.sentiment_data.get('summary', 'N/A')[:80]}...")
    else:
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ FAILED - Sentiment analysis failed for {module_code}")
        logger.error(f"{'='*60}")
    
    db.close()

if __name__ == "__main__":
    # Default to CS1101S, but allow command line argument
    module_code = sys.argv[1] if len(sys.argv) > 1 else "CS1101S"
    test_single_module(module_code)