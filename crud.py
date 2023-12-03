from sqlalchemy.orm import Session
from database import User

# Create a new user

# Retrieve a user by email
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Update user's OTP by email
def update_user_otp(db: Session, email: str, new_otp: str):
    user = get_user_by_email(db, email)
    if user:
        user.otp = new_otp
        db.commit()
    return user

# Delete a user by email
def delete_user_by_email(db: Session, email: str):
    user = get_user_by_email(db, email)
    if user:
        db.delete(user)
        db.commit()
        return user
