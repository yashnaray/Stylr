from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base

class UserInfo(Base):
    __tablename__ = "user_information"
    username = Column(String, primary_key=True, unique=True)
    gender = Column(String, nullable=True)
    interactions = relationship("Interaction", back_populates="user_info")


class ItemInfo(Base):
    __tablename__ = "catalog"
    item_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    category = Column(String, index=True)
    subcategory = Column(String, index=True)
    article_type = Column(String, index=True)
    base_colour = Column(String, index=True)
    season = Column(String, index=True)
    usage = Column(String, index=True)
    image_url = Column(String)
    price = Column(Float, nullable=True)
    tags = Column(String, nullable=True)
    interactions = relationship("Interaction", back_populates="item_info")

class Interaction(Base):
    __tablename__ = "myaccount_interactions"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("user_information.username"))
    item_id = Column(Integer, ForeignKey("catalog.item_id"))
    viewed = Column(Boolean, default=False)
    liked = Column(Boolean, default=False)
    ts = Column(DateTime, default=datetime.utcnow, index=True)
    user_info = relationship("UserInfo", back_populates="interactions")
    item_info = relationship("ItemInfo", back_populates="interactions")
