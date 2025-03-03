from sqlalchemy import Column, Integer, String, BigInteger
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    gender = Column(String(1), nullable=False)  # 'M' or 'F'
    city = Column(String, nullable=True)
    interest_bitmask = Column(BigInteger, nullable=False)
