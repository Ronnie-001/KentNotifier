from app.database.dbconn import Base
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

class Data(Base):
    __tablename__ = "monitored_users"
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    base_timetable = Column(String)   
    latest_timetable = Column(String)
    user_cookies = Column(JSONB)
    created_at = Column(Date)
    updated_at = Column(Date)
