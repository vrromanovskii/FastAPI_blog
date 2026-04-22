from sqlalchemy import Column, String, Text, UUID, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.database.database import Base
import uuid

class Publication(Base):
    __tablename__ = "publications"

    publication_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="publications")

class DeletedPublication(Base):
    __tablename__ = "deleted_publications"

    publication_id = Column(UUID(as_uuid=True), primary_key=True)
    title = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    deleted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    author_id = Column(Integer, nullable=False)