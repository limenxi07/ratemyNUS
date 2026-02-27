from app.database import SessionLocal
from app.models import Module
from app.sentiment import analyze_all_modules
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_sentiment_data():
    """
    Clear sentiment_data from all modules.
    Keeps modules and comments intact.
    For re-running sentiment analysis without re-scraping.
    """
    db = SessionLocal()
    
    modules = db.query(Module).all()
    
    for module in modules:
        module.sentiment_data = None
        module.has_sufficient_reviews = False
    
    db.commit()
    db.close()
    
    logger.info(f"✅ Cleared sentiment data from {len(modules)} modules")

def run_sentiment_analysis():
    logger.info("Starting sentiment analysis for all modules...")
    
    db = SessionLocal()
    results = analyze_all_modules(db)
    db.close()
    
    logger.info(f"\n{'='*60}\nSENTIMENT ANALYSIS COMPLETE\n{'='*60}")
    logger.info(f"✅ Success: {results['success']}")
    logger.info(f"⚠️  Insufficient data (≤3 reviews): {results['insufficient_data']}")
    logger.info(f"❌ Failed: {results['failed']}")
    logger.info(f"{'='*60}\n")

if __name__ == "__main__":
    confirm = input("Clear and regenerate all sentiment data? (yes/no): ")
    if confirm.lower() == 'yes':
        clear_sentiment_data()
        run_sentiment_analysis()
    else:
        logger.info("Aborted.")