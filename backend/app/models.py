from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone, timedelta

# Default Singapore timezone (UTC+8)
SGT = timezone(timedelta(hours=8))

def now_sgt() -> datetime:
    return datetime.now(SGT)

class Module(Base):
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(200), index=True, nullable=False)
    units = Column(Integer)
    description = Column(Text)
    url = Column(String(500))
    is_su_option = Column(Boolean, default=False)
    semesters_available = Column(JSON)  # ["Sem 1", "Sem 2", "ST1", "ST2"]
    
    # Aggregated sentiment analysis results
    sentiment_data = Column(JSON)  # {workload: 4.2, difficulty: 3.8, summary: "...", advice: "..."}
    last_analyzed = Column(DateTime)
    last_comment_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=now_sgt)
    updated_at = Column(DateTime, default=now_sgt, onupdate=now_sgt)
    
    # Relationship
    comments = relationship("Comment", back_populates="module", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    text = Column(Text, nullable=False)
    posted_date = Column(DateTime)
    upvotes = Column(Integer, default=0)
    scraped_at = Column(DateTime, default=now_sgt)
    
    # Relationship
    module = relationship("Module", back_populates="comments")