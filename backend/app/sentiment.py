import anthropic
import json
import os
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from app.models import Module, Comment
import logging

logger = logging.getLogger(__name__)
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-haiku-4-20250514"
MAX_TOKENS = 2000


def analyze_module_sentiment(db: Session, module_id: int) -> bool:
    """
    Analyze sentiment for a module using Claude API.
    Returns True if successful, False otherwise.
    """
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        logger.error(f"Module ID {module_id} not found")
        return False
    
    comments = db.query(Comment).filter(Comment.module_id == module_id).all()
    
    # Handle ≤3 reviews case (insufficient data)
    if len(comments) <= 3:
        logger.info(f"{module.code} has ≤3 reviews, storing raw comments")
        module.sentiment_data = {
            "insufficient_data": True,
            "raw_comments": [
                {
                    "text": c.text,
                    "upvotes": c.upvotes,
                    "date": c.posted_date.isoformat() if c.posted_date else None
                }
                for c in comments
            ]
        }
        module.has_sufficient_reviews = False
        db.commit()
        return True
    
    # Prepare comments for Claude
    comments_text = "\n\n---\n\n".join([
        f"Comment {i+1} (Upvotes: {c.upvotes}, Date: {c.posted_date}):\n{c.text}"
        for i, c in enumerate(comments)
    ])
    
    # Construct prompt
    prompt = f"""You are analyzing student reviews for the NUS module "{module.code} - {module.name}".

Below are {len(comments)} student reviews from NUSMods. Analyze them and provide a comprehensive summary in JSON format.

REVIEWS:
{comments_text}

TASK:
Return ONLY valid JSON (no markdown, no preamble) with this structure:
{{
  "workload": <float 1-5, where 1=very light, 5=very heavy>,
  "difficulty": <float 1-5, where 1=very easy, 5=very hard>,
  "usefulness": <float 1-5, where 1=not useful, 5=extremely useful>,
  "enjoyability": <float 1-5, where 1=not enjoyable, 5=very enjoyable>,
  "summary": "<one concise sentence capturing overall student sentiment>",
  "advice": {{
    "general": "<synthesise general advice for future students>",
    "midterm": "<synthesise specific advice for midterm exam from different reviews (only if mentioned in reviews)>",
    "final": "<similar to above (only if mentioned)>",
    "practical": "<similar to above (only if mentioned)>",
    "assignments": "<similar to above (only if mentioned)>",
    "tutorial": "<similar to above (only if mentioned)>",
    "recitation": "<similar to above (only if mentioned)>"
  }},
  "top_comments": [
    {{
      "text": "<most representative comment text>",
      "upvotes": <number>,
      "date": "<ISO date>",
      "author": "<if mentioned, otherwise null>"
    }},
    (select 3 most helpful/representative comments)
  ]
}}

RULES:
- Scores should reflect the AVERAGE sentiment, not extremes
- Scores should be in whole numbers where possible, but can be in decimals (strictly 0.5 increments) to more accurately represent small differences between modules
- Advice sections: only include if students actually mention that exam type
- Summary should be a concise synthesis of overall sentiment, not just a generic statement. It should be one paragraph, maximum 100 words.
- Advice should synthesise common themes across reviews, not just copy-paste individual comments. For example, if multiple students mention that the midterm is very difficult and covers obscure topics, the midterm advice could be: "The midterm is challenging, with questions that cover difficult topics such as [...] (fill this in). It's recommended to review lecture materials thoroughly and practice with past year papers to identify these tricky areas."
- Advice should be presented in a way that future students can easily understand and act on, rather than just being a collection of quotes. It should provide actionable insights. Each advice section should be 1-3 sentences summarising the key points from the reviews. No more than 50 words per advice section.
- Top comments: choose diverse perspectives (not all positive or all negative), and ensure they are representative of the overall sentiment. If no clear "most helpful" comments, just select a few that capture common themes.
- Top comments should only be posted in the last 3 years to ensure relevance. If there are more recent comments claiming a change in module structure/content, prioritize those instead.
- Return ONLY the JSON object, nothing else"""

    try:
        # Call Claude API
        message = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract JSON from response
        response_text = message.content[0].text.strip()
        
        # Parse JSON
        sentiment_data = json.loads(response_text)
        
        # Store in database
        module.sentiment_data = sentiment_data
        module.has_sufficient_reviews = True
        db.commit()
        
        logger.info(f"✅ Successfully analyzed {module.code}")
        return True
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON for {module.code}: {e}")
        logger.error(f"Response was: {response_text[:500]}")
        return False
    except Exception as e:
        logger.error(f"Error analyzing {module.code}: {e}")
        return False


def analyze_all_modules(db: Session) -> Dict[str, int]:
    """
    Analyze all modules in database.
    Returns dict with success/failure counts.
    """
    modules = db.query(Module).all()
    
    results = {
        "success": 0,
        "failed": 0,
        "insufficient_data": 0
    }
    
    for module in modules:
        logger.info(f"\n{'='*60}\nAnalyzing {module.code}\n{'='*60}")
        
        # Check if already has sentiment data
        if module.sentiment_data:
            logger.info(f"{module.code} already has sentiment data, skipping")
            results["success"] += 1
            continue
        
        # Check comment count
        comment_count = db.query(Comment).filter(Comment.module_id == module.id).count()
        if comment_count == 0:
            logger.info(f"{module.code} has no comments, skipping")
            continue
        
        # Analyze
        success = analyze_module_sentiment(db, module.id)
        
        if success:
            if module.has_sufficient_reviews:
                results["success"] += 1
            else:
                results["insufficient_data"] += 1
        else:
            results["failed"] += 1
    
    return results