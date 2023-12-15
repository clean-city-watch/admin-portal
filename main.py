import string
from fastapi import Depends, FastAPI, Form, HTTPException,status
from sqlalchemy import create_engine
from crud import delete_admin_user_by_email, delete_user_by_email, get_admin_user_by_email, get_average_rating, get_most_active_users, get_posts_by_city, get_upvotes_per_post, get_user_by_email
from database import SessionLocal, User,Users,Community
from pydantic import BaseModel
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.orm import Session
import secrets
import smtplib
from email.message import EmailMessage
from decouple import config
from sqlalchemy.orm import Session
from fastapi import Header

from typing import List
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



app = FastAPI()

#------------------------- EMAIL SERVER CREDENTIALS  ------------------------------------------------------

EMAIL_SERVER =  config('EMAIL_SERVER')
EMAIL_PORT =  config('EMAIL_PORT')

EMAIL_SENDER = config('EMAIL_SENDER')
EMAIL_PASSWORD = config('EMAIL_PASSWORD')


#------------------------- ADMIN-USER ---------------------------------------------------------------------
class EmailSchema(BaseModel):
    email: str

class SendOTPResponse(BaseModel):
    message: str

class UserResponse(BaseModel):
    email: str
    role: str

class TokenSchema(BaseModel):
    token: str

#----------------------------------------Functions --------------------------------------------------------------------

def send_email(email, subject, message):
    try:
        # Create an email message
        print("In Send_Email.")
        msg = EmailMessage()        
        msg.set_content(message)     
        msg["Subject"] = subject   
        msg["From"] = EMAIL_SENDER
        msg["To"] = email
        
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT)          
        server.starttls()
        print("Connected  successfully...")
        # Login to Gmail account
        print(EMAIL_SENDER, EMAIL_PASSWORD)
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        print("Logged In successfully...")
        # Send the email
        server.send_message(msg)    
        print("Email sent successfully...")
        # Close the connection
        server.quit()
       
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send email")
    

#----------------------- API ENDPOINTS FOR ADMIN-USER MANAGEMENT -----------------------------------------------------------
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/send-otp/", response_model=SendOTPResponse)
async def send_otp(
    email: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):
    email = email
    print(email)

    try:
        validate_email(email)
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    otp = secrets.randbelow(10000)
    otp = f"{otp:04d}"
    print(otp)
    # Generate a 30-character token
    token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(30))
    # Encode the token as bytes
    token_bytes = token.encode('utf-8')
    print(token_bytes)
    user = User(email=email, otp=otp, role=role, token=token_bytes)
    message = f"Your OTP is: {otp}"
    subject = "OTP for login"
    
    send_email(email, subject, message)
    db.add(user)
    db.commit()
    print("User added in the DB")

    return {"message": "OTP sent successfully"}



@app.post("/verify-otp/")
async def verify_otp(email: str = Form(...), otp: str = Form(...), db: Session = Depends(get_db)):
    try:
        validate_email(email)
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail="Invalid email address")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if otp == user.otp:
        return {"message": "OTP verified successfully", "token": user.token.decode('utf-8')}

    raise HTTPException(status_code=400, detail="Invalid OTP")


# Assign a role to a user
@app.put("/assign-role/")
async def assign_role(email: str, role: str, db: Session = Depends(get_db)):
    # Check if the provided role is valid
    if role not in ["admin", "moderator"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = get_admin_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role
    db.commit()

    return {"message": f"Role '{role}' assigned to the user with email '{email}' successfully"}

# List existing admin users
@app.get("/list-admin-users/", response_model=List[UserResponse])
async def list_admin_users(db: Session = Depends(get_db)):
    admin_users = db.query(User).filter(User.role == "admin").all()

    # Convert the list of User objects to a list of dictionaries
    admin_users_data = [{"email": user.email, "role": user.role} for user in admin_users]

    return admin_users_data

# Delete a admin-user
@app.delete("/delete-admin-user/")
async def delete_user_api(email: str, db: Session = Depends(get_db)):
    user = delete_admin_user_by_email(db, email)
    
    if user:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")


#--------------------------------- CRUD Operations for USERS ---------------------------#


class UserCreate(BaseModel):
    email: str
    password: str
  

# Dependency to get the current user (admin or moderator)
def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")), db: Session = Depends(lambda: SessionLocal())):
    user = db.query(User).filter(User.token == token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user

# Create a new user API
@app.post("/create-user/", response_model=dict)
async def create_user(
    email: str = Form(...),
    password: str = Form(...),
    # current_user: Users = Depends(get_current_user),
    db: Session = Depends(lambda: SessionLocal())
):
    # Check if the current user is an admin or moderator
    # if current_user.role not in ["admin", "moderator"]:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")

    # Create a new user
    new_user = Users(
        email=email,
        password=password,
        timestamp=datetime.now()
    )

    # Add the user to the database
    db.add(new_user)
    db.commit()

    return {"message": "User created successfully", "user": new_user}

# Get all users
@app.get("/get-all-users/")
async def get_all_users(db: Session = Depends(get_db)):
    users = db.query(Users).all()
    
    return users


@app.get("/get-user/")
async def get_user_api(email: str, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email)
    
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


#---------------------------------- Analytics APIs ------------------------------------------------------


class CommunityResponse(BaseModel):
    id: int
    name: str
    city: str

    class Config:
        orm_mode = True

class CommunityCreate(BaseModel):
    name: str
    city: str

@app.post("/communities/", response_model=CommunityResponse)
def create_community(community: CommunityCreate, db: Session = Depends(get_db)):
    db_community = Community(**community.dict())
    db.add(db_community)
    db.commit()
    db.refresh(db_community)
    return db_community


@app.get("/analytics/communities/", response_model=List[CommunityResponse])
def read_all_communities(db: Session = Depends(get_db)):
    communities = db.query(Community).all()
    print(communities)
    return communities

@app.get("/analytics/posts_by_city")
def analytics_posts_by_city(db: Session = Depends(get_db)):
    posts_by_city = get_posts_by_city(db)
    return [{"city": city, "total_posts": total} for city, total in posts_by_city]


@app.get("/analytics/average_rating")
def analytics_average_rating(db: Session = Depends(get_db)):
    average_rating = get_average_rating(db)
    return {"average_rating": average_rating}


@app.get("/analytics/most_active_users")
def analytics_most_active_users(db: Session = Depends(get_db)):
    most_active_users = get_most_active_users(db)
    return [{"user_email": user_email, "total_posts": total} for user_email, total in most_active_users]


@app.get("/analytics/upvotes_per_post")
def analytics_upvotes_per_post(db: Session = Depends(get_db)):
    upvotes_per_post = get_upvotes_per_post(db)
    return [{"post_id": post_id, "post_title": post_title, "total_upvotes": total_upvotes} for post_id, post_title, total_upvotes in upvotes_per_post]