from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean,LargeBinary 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime


DATABASE_URL = "postgresql://ccwdb_dev1:SpeedMarsTrainRecordBoth49@89.233.105.216:5460/ccwdb"


schema_name = "your_schema_name"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "admin_user"
    # __table_args__ = {'schema': schema_name}
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    otp = Column(String)
    role = Column(String) 
    token = Column(LargeBinary)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    

def create_tables():
    Base.metadata.create_all(bind=engine)
