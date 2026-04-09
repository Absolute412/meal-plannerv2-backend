from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
from datetime import date

from src.database import get_db
from src.models.database_models import Meal, User
from src.models.schemas import MealCreate, MealUpdate, MealOut
from src.models.meal_type import MealType
from src.services import meal_service
from src.utils.dependencies import get_current_user

router = APIRouter(prefix="/meals", tags=["Meals"])

"""Get all meals (all or by date)"""
@router.get("/", response_model=List[MealOut])
def get_meals(
    meal_date: Optional[date] = None, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    query = (
        db.query(Meal)
        .options(selectinload(Meal.ingredients))
        .filter(Meal.user_id == current_user.id)
    )
    if meal_date:
        query = query.filter(Meal.meal_date == meal_date)
    
    meals = query.all()
    # Capitalize meal_type to match enum
    for meal in meals:
        meal.meal_type = meal.meal_type.capitalize()
    
    return meals

"""Get meals for the week of a given date"""
@router.get("/week", response_model=List[MealOut])
def get_meals_by_week(
    meal_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    meals = meal_service.get_meals_by_week(db, current_user.id, meal_date)

    for meal in meals:
        meal.meal_type = meal.meal_type.capitalize()

    return meals

"""Get meals by ID (only if it belongs to a user)"""
@router.get("/{meal_id}", response_model=MealOut)
def get_meal_by_id(
    meal_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_meal = (
        db.query(Meal)
        .options(selectinload(Meal.ingredients))
        .filter(Meal.id == meal_id, Meal.user_id == current_user.id)
        .first()
    )
    if db_meal:
        return db_meal
    raise HTTPException(status_code=404, detail="Meal not found")

"""Create a meal"""
@router.post("/", response_model=MealOut)
def create_meal(
    meal: MealCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Ensure meal_type is stored consistently
    meal.meal_type = MealType(meal.meal_type.capitalize())
    return meal_service.create_meal(db, meal, current_user.id)

"""Update meal (only if it belongs to a user)"""
@router.put("/{meal_id}", response_model=MealOut)
def update_meal(
    meal_id: int, 
    meal: MealUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # keep meal_type consistent
    if meal.meal_type is not None:
        meal.meal_type = MealType(meal.meal_type.capitalize())

    updated = meal_service.update_meal(db, meal_id, meal, current_user.id)

    if not updated:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    return updated

"""Delete meal by id (only if it belongs to a user)"""
@router.delete("/{meal_id}", status_code=204)
def delete_meal(
    meal_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    db_meal = db.query(Meal).filter(Meal.id == meal_id, Meal.user_id == current_user.id).first()
    if not db_meal:
        raise HTTPException(status_code=404, detail="Meal not found")
    db.delete(db_meal)
    db.commit()
