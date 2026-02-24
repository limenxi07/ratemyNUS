from app.database import SessionLocal
from app.models import Module
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

if __name__ == "__main__":
    confirm = input("Clear all sentiment data? (yes/no): ")
    if confirm.lower() == 'yes':
        clear_sentiment_data()
        logger.info("You can now re-run: python run_sentiment_analysis.py")
    else:
        logger.info("Aborted.")