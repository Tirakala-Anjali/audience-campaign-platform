from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(
        Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True
    )
    audience_member_id = Column(
        Integer, ForeignKey("audience_members.id", ondelete="CASCADE"), nullable=False, index=True
    )
    template_id = Column(
        Integer, ForeignKey("templates.id", ondelete="SET NULL"), nullable=True, index=True
    )
    channel = Column(String(20), nullable=False)
    # Allowed values: pending | sent | delivered | failed | bounced
    status = Column(String(20), nullable=False, default="pending", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="messages")
    audience_member = relationship("AudienceMember", back_populates="messages")
    template = relationship("Template", back_populates="messages")
    delivery_logs = relationship("DeliveryLog", back_populates="message")

    def __repr__(self) -> str:
        return f"<Message id={self.id} status={self.status!r} channel={self.channel!r}>"
