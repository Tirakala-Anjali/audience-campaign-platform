from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship
from app.database import Base


class AudienceMember(Base):
    __tablename__ = "audience_members"

    id = Column(Integer, primary_key=True, index=True)

    # Core identity
    name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    phone = Column(String(30), nullable=True)

    # Demographic fields (Task 4 spec)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    occupation = Column(String(100), nullable=True)
    department = Column(String(100), nullable=True)
    organization = Column(String(150), nullable=True)

    # Communication preferences
    preferred_language = Column(String(10), nullable=False, default="en")
    preferred_channel = Column(String(20), nullable=True)   # email | sms | whatsapp | push

    # Consent
    consent_status = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    messages = relationship("Message", back_populates="audience_member")
    feedbacks = relationship("Feedback", back_populates="audience_member")

    def __repr__(self) -> str:
        return f"<AudienceMember id={self.id} email={self.email!r}>"
