from sqlalchemy import func
from sqlalchemy.orm import Session
from database import User,Users,Post,UserFeedback,Upvote

# Create a new user

# Retrieve a user by email
def get_user_by_email(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).first()

def get_admin_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Update user's OTP by email
def update_user_otp(db: Session, email: str, new_otp: str):
    user = get_user_by_email(db, email)
    if user:
        user.otp = new_otp
        db.commit()
    return user

# Delete a user by email
def delete_admin_user_by_email(db: Session, email: str):
    user = get_admin_user_by_email(db, email)
    if user:
        db.delete(user)
        db.commit()
        return user
    
# Delete a user by email
def delete_user_by_email(db: Session, email: str):
    user = get_user_by_email(db, email)
    if user:
        db.delete(user)
        db.commit()
        return user
    
def get_posts_by_city(db: Session):
    posts_by_city = (
        db.query(Post.city, func.count(Post.id))
        .group_by(Post.city)
        .all()
    )
    return posts_by_city


def get_average_rating(db: Session):
    average_rating = db.query(func.avg(UserFeedback.rating)).scalar()
    return average_rating


def get_most_active_users(db: Session):
    most_active_users = (
        db.query(Users.email, func.count(Post.id))
        .join(Post, Users.id == Post.author_id)
        .group_by(Users.email)
        .order_by(func.count(Post.id).desc())
        .limit(5)
        .all()
    )
    return most_active_users

def get_upvotes_per_post(db: Session):
    upvotes_per_post = (
        db.query(Post.id, Post.title, func.count(Upvote.id))
        .outerjoin(Upvote, Post.id == Upvote.post_id)
        .group_by(Post.id, Post.title)
        .all()
    )
    return upvotes_per_post

