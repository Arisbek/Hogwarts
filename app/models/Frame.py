from sqlalchemy import Column, Integer, String, JSON, Text
from db import Base

class Frame(Base):
    __tablename__ = 'frames'

    # Use the frame name as the primary key
    name = Column(String(255), primary_key=True, index=True)
    # Base64 or URL data for the reference image
    image_src = Column(Text, nullable=False)
    # JSON blob storing transform: { scale, x, y }
    transform = Column(JSON, nullable=False)
    # JSON array of group objects (each with squares array inside)
    groups = Column(JSON, nullable=False)
    # Original image natural dimensions for scaling
    image_width = Column(Integer, nullable=False)
    image_height = Column(Integer, nullable=False)