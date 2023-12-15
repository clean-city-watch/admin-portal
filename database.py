from sqlalchemy import UniqueConstraint, create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean,LargeBinary,Text,Float, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from decouple import config


DATABASE_URL = config('DATABASE_URL')

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


class Community(Base):
    __tablename__ = "Community"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    city = Column(Text)

    _table_args_ = (
        UniqueConstraint("name", "city", name="community_name_city_unique"),
    )


class Organization(Base):
    __tablename__ = "Organization"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False)
    type = Column(Text)
    email = Column(Text, nullable=False, unique=True)
    phone_number = Column(Text)
    address_line_1 = Column(Text)
    address_line_2 = Column(Text)
    city = Column(Text, nullable=False)
    postal_code = Column(Text)
    country_code = Column(Text)
    state_code = Column(Text)
    logo = Column(Text, nullable=False)


class UserCommunity(Base):
    __tablename__ = "UserCommunity"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    community_id = Column(Integer, ForeignKey("Community.id", ondelete="CASCADE"), nullable=False)


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    organization_id = Column(Integer, ForeignKey("Organization.id", ondelete="SET NULL", onupdate="CASCADE"))


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(Text)
    last_name = Column(Text)
    phone_number = Column(Text)
    address_line_1 = Column(Text)
    address_line_2 = Column(Text)
    avatar = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    content = Column(Text)
    image_url = Column(Text, nullable=False)
    city = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    published = Column(Boolean, default=False)
    status_id = Column(Integer, ForeignKey("statuses.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)


class Status(Base):
    __tablename__ = "statuses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Text, nullable=False, unique=True)


class Upvote(Base):
    __tablename__ = "upvotes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserFeedback(Base):
    __tablename__ = "user_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    feedback = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)


class GreenCoin(Base):
    __tablename__ = "green_coins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    coins = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
