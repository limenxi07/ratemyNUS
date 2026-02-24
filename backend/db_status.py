from app.database import SessionLocal
from app.models import Module, Comment
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_status():
    """
    Display current database status.
    """
    db = SessionLocal()
    
    # Count modules
    total_modules = db.query(Module).count()
    modules_with_sentiment = db.query(Module).filter(Module.sentiment_data.isnot(None)).count()
    modules_sufficient_reviews = db.query(Module).filter(Module.has_sufficient_reviews == True).count()
    
    # Count comments
    total_comments = db.query(Comment).count()
    
    # Module breakdown
    modules = db.query(Module).all()
    
    db.close()
    
    # Display
    print("\n" + "="*60)
    print("DATABASE STATUS")
    print("="*60)
    print(f"\n📊 OVERVIEW:")
    print(f"  Total modules: {total_modules}")
    print(f"  Total comments: {total_comments}")
    print(f"  Modules with sentiment data: {modules_with_sentiment}/{total_modules}")
    print(f"  Modules with sufficient reviews (>3): {modules_sufficient_reviews}")
    
    print(f"\n📝 MODULE DETAILS:")
    for m in modules:
        status = "✅" if m.sentiment_data else "❌"
        reviews = "⚠️ " if not m.has_sufficient_reviews and m.sentiment_data else ""
        print(f"  {status} {m.code:10} - {m.last_comment_count:3} reviews {reviews}")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    check_status()