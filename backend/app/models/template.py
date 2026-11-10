from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, func
from sqlalchemy.orm import relationship
from app.database import Base


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)

    # Spec fields (Task 6)
    category = Column(String(50), nullable=True)             # promotional | newsletter | alert …
    channel = Column(String(20), nullable=False, index=True) # email | sms | push | whatsapp
    language = Column(String(10), nullable=False, default="en")
    subject = Column(String(255), nullable=True)             # for email channel
    content = Column(Text, nullable=False)
    placeholders = Column(JSON, nullable=True)               # ["name","company","date"]
    tags = Column(JSON, nullable=True)                       # ["welcome","promo"]

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    messages = relationship("Message", back_populates="template")

    def __repr__(self) -> str:
        return f"<Template id={self.id} name={self.name!r} channel={self.channel!r}>"
