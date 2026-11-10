from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Spec fields (Task 6)
    campaign_type = Column(String(50), nullable=True)        # awareness | promotional | emergency …
    objective = Column(String(255), nullable=True)
    channels = Column(JSON, nullable=True)                   # ["email","sms","whatsapp"]
    priority = Column(String(20), nullable=False, default="medium")  # low | medium | high | emergency
    creator_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)

    # Status & schedule
    status = Column(String(20), nullable=False, default="draft", index=True)
    start_at = Column(DateTime(timezone=True), nullable=True)
    end_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    creator = relationship("User", foreign_keys=[creator_id])
    messages = relationship("Message", back_populates="campaign")
    feedbacks = relationship("Feedback", back_populates="campaign")

    def __repr__(self) -> str:
        return f"<Campaign id={self.id} name={self.name!r} status={self.status!r}>"
