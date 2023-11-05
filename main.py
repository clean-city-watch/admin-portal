import string
from fastapi import Depends, FastAPI, Form, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from crud import delete_user_by_email, get_user_by_email
from database import SessionLocal, User, create_tables, Base
from pydantic import BaseModel
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.orm import Session
import secrets
from database import Base
import smtplib
from email.message import EmailMessage
from pydantic import BaseModel



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from fastapi import Depends, FastAPI, Form, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from email_validator import validate_email, EmailNotValidError
import smtplib
from email.message import EmailMessage
import os
import secrets

app = FastAPI()
create_tables()
SMTP_SERVER = "smtp.gmail.com"  # Gmail's SMTP server
SMTP_PORT = 587  # Port for TLS

# Your Gmail account details
EMAIL_SENDER = "your-email"
EMAIL_PASSWORD = "your-password"

def send_email(email, subject, message):
    try:
        # Create an email message
        
        msg = EmailMessage()        
        msg.set_content(message)     
        msg["Subject"] = subject   
        msg["From"] = EMAIL_SENDER
        msg["To"] = email
        
        # Connect to Gmail's SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)          
        server.starttls()
        # Login to your Gmail account
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        # Send the email
        server.send_message(msg)    
        # Close the connection
        server.quit()
        print("Email sent successfully...")
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to send email")
    

@app.get("/")
def read_root():
    return {"Hello": "World"}

class EmailSchema(BaseModel):
    email: str

class SendOTPResponse(BaseModel):
    message: str
    token: str  # Include the token in the response

@app.post("/send-otp/", response_model=SendOTPResponse)
async def send_otp(
    email_data: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db)
):
    email = email_data
    print(email)

    try:
        validate_email(email)
    except EmailNotValidError as e:
        raise HTTPException(status_code=400, detail="Invalid email address")
    
    otp = secrets.randbelow(10000)
    otp = f"{otp:04d}"
    
    # Generate a 30-character token
    token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(30))
    # Encode the token as bytes
    token_bytes = token.encode('utf-8')
    user = User(email=email, otp=otp, role=role, token=token_bytes)  # Update the User object with the token
    db.add(user)
    db.commit()
    print("User added in the DB")
    
    message = f"Your OTP is: {otp}"
    subject = "OTP for login"
    send_email(email, subject, message)

    return {"message": "OTP sent successfully", "token": token}


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
        return {"message": "OTP verified successfully"}

    raise HTTPException(status_code=400, detail="Invalid OTP")


#--------------- CRUD Operations Route for USER ---------------------------#


@app.get("/get-user/")
async def get_user_api(email: str, db: Session = Depends(get_db)):
    user = get_user_by_email(db, email)
    
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")



# Delete a user
@app.delete("/delete-user/")
async def delete_user_api(email: str, db: Session = Depends(get_db)):
    user = delete_user_by_email(db, email)
    
    if user:
        return {"message": "User deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="User not found")