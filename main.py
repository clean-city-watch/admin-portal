import string
from fastapi import Depends, FastAPI, Form, HTTPException
from sqlalchemy import create_engine
from crud import delete_user_by_email, get_user_by_email
from database import SessionLocal, User
from pydantic import BaseModel
from email_validator import validate_email, EmailNotValidError
from sqlalchemy.orm import Session
import secrets
import smtplib
from email.message import EmailMessage
from decouple import config
from sqlalchemy.orm import Session
from fastapi import Header


class TokenSchema(BaseModel):
    token: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



app = FastAPI()
# create_tables()
EMAIL_SERVER =  config('EMAIL_SERVER')
EMAIL_PORT =  config('EMAIL_PORT')

EMAIL_SENDER = config('EMAIL_SENDER')
EMAIL_PASSWORD = config('EMAIL_PASSWORD')



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
    

@app.get("/")
def read_root():
    return {"Hello": "World"}

class EmailSchema(BaseModel):
    email: str

class SendOTPResponse(BaseModel):
    message: str

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