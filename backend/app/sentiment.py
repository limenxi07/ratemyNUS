import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from typing import Dict
from sqlalchemy.orm import Session
from app.models import Module, Comment
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Configure Gemini
MODEL_TYPE = 'gemini-2.5-flash-lite' # Find alternative models @ https://ai.google.dev/gemini-api/docs/models
MAX_TOKENS = 5000

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def analyze_module_sentiment(db: Session, module_id: int) -> bool:
    """
    Analyze sentiment for a module using Gemini API.
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
    
    # Prepare comments for Gemini
    comments_text = "\n\n---\n\n".join([
        f"Comment {i+1} (Upvotes: {c.upvotes}, Date: {c.posted_date}):\n{c.text}"
        for i, c in enumerate(comments)
    ])
    
    # Construct prompt
    prompt = f"""You are analyzing student reviews for the NUS module "{module.code} - {module.name}".

Below are {len(comments)} student reviews from NUSMods. Analyze them and provide a comprehensive summary in JSON format. Use British English spelling and phrasing. The tone can be slightly informal, as if advising a friend, but still be clear, concise and instructional.

IMPORTANT: If no advice is provided for any sub-category (e.g. if the midterm or practical is never mentioned), OMIT that field from the JSON entirely. Only include advice sections that are actually mentioned in the reviews. For each advice sub-category, synthesise the common themes across reviews into a concise summary that future students can easily understand and act on. Do NOT just copy-paste individual comments. The advice should provide actionable insights based on the reviews. Maximum length of each advice sub-category: 50 words.

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
  "reasoning": "<a brief explanation of how you arrived at the scores, mentioning key themes from the reviews. each score should have its own concise one-sentence justification>",
  "advice": {{
    "general": "<synthesise general advice for future students, only if mentioned in reviews>",
    "midterm": "<synthesise specific advice for midterm exam from different reviews (only if mentioned in reviews)>",
    "final": "<similar to above (only if mentioned)>",
    "practical": "<similar to above (only if mentioned)>",
    "assignments": "<similar to above (only if mentioned)>",
    "tutorial": "<similar to above (only if mentioned)>",
    "recitation": "<similar to above (only if mentioned)>"
  }},
  "top_comments": [
    {{
      "upvotes": <number>,
      "date": "<ISO date>",
      "author": "<if mentioned, otherwise null>"
    }},
    (select 3 most helpful/representative comments, without including full text)
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
        # Call Gemini API
        response = client.models.generate_content(
            model=MODEL_TYPE,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=MAX_TOKENS,
                response_mime_type="application/json",
                candidate_count=1,
            )
        )
        
        # Extract JSON from response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])
        
        # Parse JSON
        try:
            sentiment_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Likely because Gemini's response exceeded max tokens and got cut off, resulting in invalid JSON
            # For now, do a manual fix
            logger.error(f"FAILED: First parse attempt for {module.code}: {e}")
            logger.error(f"Response was: {response_text[:500]}")
            missing_braces = response_text.count('{') - response_text.count('}')
            response_text = response_text + ('}' * missing_braces)
            sentiment_data = json.loads(response_text)
        
        # Calculate average score
        # NOTE: Because workload/difficulty are negative vs usefulness/enjoyability are positive, take inverse score for workload/difficulty to calculate average sentiment score
        average_score = (
            (5 - sentiment_data.get("workload", 3)) +
            (5 - sentiment_data.get("difficulty", 3)) +
            sentiment_data.get("usefulness", 3) +
            sentiment_data.get("enjoyability", 3)) / 4
        # round up the average score to the nearest 0.5 increment
        average_score = round(average_score * 2) / 2
        sentiment_data["average"] = average_score
        
        # Update JSON data with full text for top comments
        # Retrieve full text from comment database
        top_comments = []
        for ref in sentiment_data.get("top_comments", []):
            # Find matching comment by upvotes, date, and author
            for c in comments:
                date_match = (
                    c.posted_date and 
                    ref.get("date") and 
                    c.posted_date.isoformat() == ref["date"]
                )
                upvote_match = c.upvotes == ref.get("upvotes", -1)
                author_match = getattr(c, 'author', 'Anonymous') == ref.get("author", "")
                
                # Match if at least 2 out of 3 criteria match (in case of slight discrepancies)
                matches = sum([date_match, upvote_match, author_match])
                
                if matches >= 2:
                    top_comments.append({
                        "text": c.text,
                        "upvotes": c.upvotes,
                        "date": c.posted_date.isoformat() if c.posted_date else None,
                        "author": getattr(c, 'author', 'Anonymous')
                    })
                    break  # Found match, move to next reference
        sentiment_data["top_comments"] = top_comments
        
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