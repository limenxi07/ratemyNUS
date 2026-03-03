import sys
from app.database import SessionLocal
from app.models import Module, Comment
from app.pipeline import fetch_module_metadata, upsert_module, replace_module_comments, update_module_comment_count
from app.scraper import scrape_module_reviews
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
    Clear and re-run scraping and sentiment analysis for a single module.
    Useful for testing during development.
    """
    db = SessionLocal()
    
    logger.info(f"\n{'='*60}")
    logger.info(f"FULL RE-SCRAPE AND ANALYSIS: {module_code}")
    logger.info(f"{'='*60}\n")
    
    # Step 1: Fetch and upsert module metadata
    logger.info(f"📡 Fetching module metadata from NUSMods API...")
    metadata = fetch_module_metadata(module_code)
    
    if not metadata:
        logger.error(f"❌ Failed to fetch metadata for {module_code}")
        db.close()
        return
    
    module = upsert_module(db, metadata)
    logger.info(f"✅ Module metadata updated")
    
    # Step 2: Delete all existing comments
    logger.info(f"\n🗑️  Deleting all existing comments for {module_code}...")
    deleted_count = db.query(Comment).filter(Comment.module_id == module.id).delete()
    db.commit()
    logger.info(f"✅ Deleted {deleted_count} old comments")
    
    # Step 3: Re-scrape comments from Disqus
    logger.info(f"\n🕷️  Re-scraping comments from Disqus...")
    comments, error = scrape_module_reviews(module_code)
    
    if error:
        logger.error(f"❌ Scraping failed: {error}")
        db.close()
        return
    
    if not comments:
        logger.warning(f"⚠️  No comments found for {module_code}")
        update_module_comment_count(db, module.id, 0)
        db.close()
        return
    
    logger.info(f"✅ Scraped {len(comments)} comments")
    
    # Step 4: Insert new comments into database
    logger.info(f"\n💾 Storing comments in database...")
    replace_module_comments(db, module.id, comments)
    update_module_comment_count(db, module.id, len(comments))
    logger.info(f"✅ Stored {len(comments)} comments")
    
    # Step 5: Clear existing sentiment data
    logger.info(f"\n🗑️  Clearing existing sentiment data...")
    module.sentiment_data = None
    module.has_sufficient_reviews = False
    db.commit()
    logger.info(f"✅ Sentiment data cleared")
    
    # Step 6: Run sentiment analysis
    logger.info(f"\n🤖 Running sentiment analysis...")
    success = analyze_module_sentiment(db, module.id)
    
    if success:
        logger.info(f"\n{'='*60}")
        logger.info(f"✅ SUCCESS - Complete re-scrape and analysis finished")
        logger.info(f"{'='*60}")
        
        # Show results
        db.refresh(module)
        if module.sentiment_data:
            logger.info(f"\n📊 Results preview:")
            if module.sentiment_data.get('insufficient_data'):
                logger.info(f"  ⚠️  Insufficient data (≤3 reviews)")
                logger.info(f"  📝 Showing {len(module.sentiment_data.get('raw_comments', []))} raw comments")
            else:
                logger.info(f"  📚 Workload: {module.sentiment_data.get('workload', 'N/A')}/5.0")
                logger.info(f"  🧠 Difficulty: {module.sentiment_data.get('difficulty', 'N/A')}/5.0")
                logger.info(f"  💡 Usefulness: {module.sentiment_data.get('usefulness', 'N/A')}/5.0")
                logger.info(f"  😊 Enjoyability: {module.sentiment_data.get('enjoyability', 'N/A')}/5.0")
                logger.info(f"  ⭐ Average: {module.sentiment_data.get('average', 'N/A')}/5.0")
                logger.info(f"  📝 Summary: {module.sentiment_data.get('summary', 'N/A')[:80]}...")
                
                top_comments = module.sentiment_data.get('top_comments', [])
                logger.info(f"  🗣️  Top comments: {len(top_comments)} selected")
        
        logger.info(f"\n💾 Total comments in database: {len(comments)}")
        logger.info(f"✅ Module ready for production\n")
    else:
        logger.error(f"\n{'='*60}")
        logger.error(f"❌ FAILED - Sentiment analysis failed")
        logger.error(f"{'='*60}\n")
    
    db.close()

if __name__ == "__main__":
    # Default to CS1101S, but allow command line argument
    module_code = sys.argv[1] if len(sys.argv) > 1 else "CS1101S"
    test_single_module(module_code)