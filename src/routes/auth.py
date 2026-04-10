from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.database_models import User
from src.models.schemas import UserCreate, UserResponse, ProfileUpdate, PasswordUpdate
from src.utils.dependencies import get_current_user
from src.utils.security import hash_password, verify_password
from src.utils.jwt import create_access_token
from sqlalchemy import or_
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):

    #  Normalize first
    email = user.email.strip().lower()
    username = user.username.strip().lower()

    # Validate empty after stripping
    if not email or not username:
        raise HTTPException(status_code=400, detail="Email and username cannot be empty")

    # Check duplicate using normalized values
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = db.query(User).filter(User.username == username).first()
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Hash password
    hashed_pw = hash_password(user.password)

    # Create user object
    new_user = User(
        email=email,
        username=username,
        hashed_password=hashed_pw
    )

    # Save to DB
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return user(without password)
    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session =Depends(get_db)):
    """
    Logs in  a user and returns JWT
    form_data.username → email
    form_data.password → plain password
    """
    # Find user by email or username
    identifier = form_data.username.strip().lower()

    user = db.query(User).filter(
        or_(
            User.email == identifier,
            User.username == identifier
        )
    ).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Verify password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT
    token = create_access_token({"sub": str(user.id)})

    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    # Determine time based greeting
    now_hour = datetime.now().hour

    if 5 <= now_hour < 12:
        greeting = "Good morning"
    elif 12 <= now_hour < 18:
        greeting = "Good afternoon"
    else: 
        greeting = "Good evening"

    # Attach greeting to the user response
    user_data = UserResponse.model_validate(current_user).model_dump()
    user_data["greeting"] = f"{greeting}, {current_user.username}"

    return user_data

@router.put("/me/profile", response_model=UserResponse)
def update_profile(
    updates: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not updates.email and not updates.username:
        raise HTTPException(status_code=400, detail="No changes provided")

    # Update email
    if updates.email:
        existing_email = db.query(User).filter(User.email == updates.email).first()
        if existing_email and existing_email.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = updates.email.strip().lower()

    # Update username
    if updates.username:
        clean = updates.username.strip()
        if not clean:
            raise HTTPException(status_code=400, detail="Username cannot be empty")
        
        formatted_username = clean.lower()
        existing_username = db.query(User).filter(User.username == formatted_username).first()
        if existing_username and existing_username.id != current_user.id:
            raise HTTPException(status_code=400, detail="Username already in use")
        current_user.username = formatted_username

    db.commit()
    db.refresh(current_user)

    return current_user

@router.put("/me/password")
def update_password(
    data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    # Verify current password
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    if data.current_password.strip() == data.new_password.strip():
        raise HTTPException(status_code=400, detail="New password must be different")
    
    # Hash new password
    new_hashed_password = hash_password(data.new_password)
    current_user.hashed_password = new_hashed_password

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return {"message": "Password updated successfully"}
