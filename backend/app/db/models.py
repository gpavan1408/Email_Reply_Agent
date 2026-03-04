"""
Database models using SQLAlchemy ORM.

Each class = one database table.
Each attribute = one column.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.db.database import Base


# ── Enums ─────────────────────────────────────────────────────

class EmailProvider(str, enum.Enum):
    """Which email service the email came from"""
    GMAIL = "gmail"
    OUTLOOK = "outlook"


class EmailIntent(str, enum.Enum):
    """What type of email this is (AI classifies this)"""
    RECRUITER_INQUIRY = "recruiter_inquiry"
    VISA_QUESTION = "visa_question"
    INTERVIEW_REQUEST = "interview_request"
    PROJECT_COLLABORATION = "project_collaboration"
    OTHER = "other"


class DraftStatus(str, enum.Enum):
    """Lifecycle of a draft reply"""
    PENDING = "pending"        # AI just created it, waiting for human review
    APPROVED = "approved"      # Human approved, ready to send
    SENT = "sent"              # Email was sent successfully
    REJECTED = "rejected"      # Human rejected, won't send


# ── Tables ────────────────────────────────────────────────────

class Email(Base):
    """
    Stores incoming emails from Gmail/Outlook.
    One row = one email received.
    """
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    
    # Email metadata
    provider = Column(Enum(EmailProvider), nullable=False)  # gmail or outlook
    message_id = Column(String(255), unique=True, nullable=False, index=True)  # unique ID from provider
    thread_id = Column(String(255), nullable=True)  # conversation thread
    
    # Email content
    sender = Column(String(255), nullable=False, index=True)
    recipient = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    
    # AI classification
    intent = Column(Enum(EmailIntent), nullable=True)  # AI classifies this
    
    # Timestamps
    received_at = Column(DateTime, nullable=False)  # when email arrived
    created_at = Column(DateTime, default=func.now(), nullable=False)  # when we saved it to DB
    
    # Relationships
    drafts = relationship("Draft", back_populates="email", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Email(id={self.id}, from={self.sender}, subject='{self.subject[:30]}...')>"


class Draft(Base):
    """
    Stores AI-generated reply drafts.
    One email can have multiple drafts (if human rejects and asks AI to try again).
    """
    __tablename__ = "drafts"

    id = Column(Integer, primary_key=True, index=True)
    
    # Which email this is replying to
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=False, index=True)
    
    # Draft content
    subject = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    
    # AI metadata
    model_used = Column(String(100), nullable=False)  # e.g., "gpt-4o"
    confidence_score = Column(Integer, nullable=True)  # 0-100, how confident AI is
    
    # Status tracking
    status = Column(Enum(DraftStatus), default=DraftStatus.PENDING, nullable=False, index=True)
    
    # Human feedback
    edited = Column(Boolean, default=False)  # Did human edit the draft?
    rejection_reason = Column(Text, nullable=True)  # If rejected, why?
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    sent_at = Column(DateTime, nullable=True)  # when email was actually sent
    
    # Relationships
    email = relationship("Email", back_populates="drafts")
    
    def __repr__(self):
        return f"<Draft(id={self.id}, email_id={self.email_id}, status={self.status})>"


class UserContext(Base):
    """
    Stores your personal information for AI to use when generating replies.
    
    Only ONE row should exist in this table.
    AI reads this to personalize drafts.
    """
    __tablename__ = "user_context"

    id = Column(Integer, primary_key=True)
    
    # Personal info
    name = Column(String(255), nullable=False)
    visa_status = Column(String(100), nullable=False)  # e.g., "OPT STEM"
    skills = Column(Text, nullable=False)  # comma-separated
    experience_years = Column(Integer, nullable=False)
    target_roles = Column(Text, nullable=False)  # comma-separated
    
    # Links
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<UserContext(name={self.name}, visa_status={self.visa_status})>"


class AuditLog(Base):
    """
    Tracks every action for compliance and debugging.
    
    Examples:
    - Email received from sender@example.com
    - Draft created for email #5
    - Draft approved by user
    - Email sent successfully
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    
    # What happened
    action = Column(String(100), nullable=False, index=True)  # e.g., "email_received", "draft_created"
    details = Column(Text, nullable=True)  # JSON with extra info
    
    # Context
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=True)
    draft_id = Column(Integer, ForeignKey("drafts.id"), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action})>"