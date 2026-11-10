from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import relationship
from app.database import Base


class Feedback(Base):
    __tablename__ = "feedback"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_feedback_rating_range"),
    )

    id = Column(Integer, primary_key=True, index=True)
    audience_member_id = Column(
        Integer, ForeignKey("audience_members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    campaign_id = Column(
        Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    rating = Column(Integer, nullable=False)   # 1–5 enforced by CHECK constraint
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    audience_member = relationship("AudienceMember", back_populates="feedbacks")
    campaign = relationship("Campaign", back_populates="feedbacks")

    def __repr__(self) -> str:
        return f"<Feedback id={self.id} rating={self.rating}>"
