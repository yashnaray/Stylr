from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from db import Base

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, default="")
    category = Column(String, index=True, default="")
    subcategory = Column(String, index=True, default="")
    article_type = Column(String, index=True, default="")
    base_colour = Column(String, index=True, default="")
    season = Column(String, index=True, default="")
    usage = Column(String, index=True, default="")
    image_url = Column(String, default="")
    price = Column(Float, nullable=True)
    interactions = relationship("Interaction", back_populates="item")

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    item_id = Column(Integer, ForeignKey("items.id"), index=True)
    viewed = Column(Boolean, default=False)
    liked = Column(Boolean, default=False)
    ts = Column(DateTime, default=datetime.utcnow, index=True)

    item = relationship("Item", back_populates="interactions")
