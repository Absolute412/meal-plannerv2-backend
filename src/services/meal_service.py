from sqlalchemy.orm import Session, selectinload
from datetime import date, timedelta
from src.models import database_models as models
from src.models.schemas import MealCreate, MealUpdate

def create_meal(db: Session, meal: MealCreate, user_id: int):
    db_meal = models.Meal(
        title=meal.title,
        meal_type=meal.meal_type,
        meal_date=meal.meal_date or date.today(),
        user_id=user_id
    )
    db.add(db_meal)
    db.commit()
    db.refresh(db_meal)

    # save ingredients
    if meal.ingredients:
        for ing in meal.ingredients:
            name = (ing.name or "").strip()
            if not name:
                continue
            db.add(models.Ingredient(
                meal_id = db_meal.id,
                name = name,
                measure = (ing.measure or "").strip()
            ))
        db.commit()
        db.refresh(db_meal)

    return db_meal

def update_meal(db: Session, meal_id: int, meal: MealUpdate, user_id: int):
    db_meal = (
        db.query(models.Meal)
        .filter(models.Meal.id == meal_id, models.Meal.user_id == user_id)
        .first()
    )
    if not db_meal:
        return None
    
    if meal.title is not None:
        db_meal.title = meal.title
    if meal.meal_type is not None:
        db_meal.meal_type = meal.meal_type
    if meal.meal_date is not None:
        db_meal.meal_date = meal.meal_date
    
    # replace ingredients if provided
    if meal.ingredients is not None:
        # delete existing ingredients
        db.query(models.Ingredient).filter(
            models.Ingredient.meal_id == db_meal.id
        ).delete()

        # insert new ones
        for ing in meal.ingredients:
            name = (ing.name or "").strip()
            if not name:
                continue
            db.add(models.Ingredient(
                meal_id=db_meal.id,
                name=name,
                measure=(ing.measure or "").strip()
            ))

    db.commit()
    db.refresh(db_meal)
    return db_meal

def get_meals_by_date(db: Session, user_id: int, meal_date: date):
    return (
        db.query(models.Meal)
        .options(selectinload(models.Meal.ingredients))
        .filter(models.Meal.user_id == user_id)
        .filter(models.Meal.meal_date == meal_date)
        .all()
    )

def get_meals_by_week(db: Session, user_id: int, selected_date: date):
    start_of_week = selected_date - timedelta(days=selected_date.weekday())
    end_of_week =  start_of_week + timedelta(days=6)

    return (
        db.query(models.Meal)
        .options(selectinload(models.Meal.ingredients))
        .filter(models.Meal.user_id == user_id)
        .filter(models.Meal.meal_date >= start_of_week)
        .filter(models.Meal.meal_date <= end_of_week)
        .all()
    )
