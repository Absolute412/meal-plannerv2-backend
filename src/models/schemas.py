from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional
from src.models.meal_type import MealType
from datetime import date, timedelta
import re

# Ingredient Schema
class Ingredient(BaseModel):
    name: str
    measure: Optional[str] = ""

# Meal Schemas
class MealBase(BaseModel):
    title: str
    meal_type: MealType
    meal_date: Optional[date] = None
    ingredients: list[Ingredient] | None = None

    @field_validator("title")
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError("Meal title cannot be empty")
        return v

class MealCreate(MealBase):
    @field_validator("meal_date")
    def validate_meal_date_not_past(cls, v):
        if v is None:
            return v
        
        today = date.today()
        max_date = today + timedelta(days=360)

        if v < today:
            raise ValueError("Meal date cannot be in the past")
        if v > max_date:
            raise ValueError("Meal date cannot be more than 360 days in the future.")
        return v

class MealUpdate(BaseModel):
    title: Optional[str] = None
    meal_type: Optional[MealType] = None
    meal_date: Optional[date] = None
    ingredients: list[Ingredient] | None = None

class MealOut(MealBase):
    id: int

    model_config = {
        "from_attributes": True
    }

# User Schemas
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("email")
    def normalize_email(cls, v):
        return v.strip().lower()
    
    @field_validator("username")
    def normalize_username(cls, v):
        return v.strip().lower()

    @field_validator("password")    
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: Optional[str]
    greeting: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

# User Profile
class ProfileUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None

    @field_validator("username")
    def validate_username(cls, v):
        if v is None:
            return v
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Username cannot be empty")
        return v

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")    
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        return v

# Grocery Schemas
class GroceryBase(BaseModel):
    name: str
    measure: Optional[str] = ""

class GroceryCreate(GroceryBase):
    pass

class GroceryOut(GroceryBase):
    id: int

    model_config = {
        "from_attributes": True
    }
