from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.exc import IntegrityError

from src.database import get_db
from src.models.database_models import Grocery, User, Meal, Ingredient
from src.models.schemas import GroceryCreate, GroceryOut
from src.utils.dependencies import get_current_user

from datetime import date

router = APIRouter(prefix="/groceries", tags=["groceries"])

@router.get("", response_model=list[GroceryOut])
def list_groceries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(Grocery)
        .filter(Grocery.user_id == current_user.id)
        .order_by(Grocery.id.desc())
        .all()
    )

@router.get("/preview", response_model=list[GroceryCreate])
def preview_groceries(
    start: date,
    end: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if start > end:
        raise HTTPException(status_code=400, detail="start must be before or equal to end")
    
    meals = (
        db.query(Meal)
        .options(selectinload(Meal.ingredients))
        .filter(Meal.user_id == current_user.id)
        .filter(Meal.meal_date >= start)
        .filter(Meal.meal_date <= end)
        .all()
    )

    # collect + dedupe by (name, measure)
    seen = set()
    preview = []

    for meal in meals:
        for ing in (meal.ingredients or []):
            name = (ing.name or "").strip()
            measure = (ing.measure or "").strip()
            if not name:
                continue

            key = (name.lower(), measure.lower())
            if key in seen:
                continue

            seen.add(key)
            preview.append({"name": name, "measure": measure})

    return preview

@router.post("/bulk")
def add_groceries(
    items: list[GroceryCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    added = []
    skipped = []

    # get all existing groceries ONCE
    existing_items = db.query(Grocery).filter(
        Grocery.user_id == current_user.id
    ).all()

    existing_set = {
        (g.name.lower().strip(), (g.measure or "").lower().strip())
        for g in existing_items
    }

    # prepare new items
    new_objects = []

    for item in items:
        name = (item.name or "").strip()
        measure = (item.measure or "").strip()

        if not name:
            skipped.append({"name": name, "measure": measure, "reason": "empty_name"})
            continue

        key = (name.lower(), measure.lower())

        if key in existing_set:
            skipped.append({"name": name, "measure": measure, "reason": "duplicate"})
            continue

        existing_set.add(key)  # prevent duplicates within same request

        new_objects.append(
            Grocery(
                name=name,
                measure=measure,
                user_id=current_user.id
            )
        )

    # bulk insert (FAST)
    if new_objects:
        db.add_all(new_objects)
        db.commit()
        added = new_objects

    return {
        "message": "Groceries processed",
        "items_added": jsonable_encoder(added),
        "items_skipped": skipped,
        "added_count": len(added),
        "skipped_count": len(skipped),
    }

@router.delete("/{item_id}")
def delete_grocery(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    grocery = (
        db.query(Grocery)
        .filter(Grocery.id == item_id, Grocery.user_id == current_user.id)
        .first()
    )
    if not grocery:
        raise HTTPException(status_code=404, detail="Grocery item not found")

    db.delete(grocery)
    db.commit()
    return {"message": "Grocery deleted", "deleted_id": item_id}

@router.delete("")
def clear_groceries(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    deleted = (
        db.query(Grocery)
        .filter(Grocery.user_id == current_user.id)
        .delete(synchronize_session=False)
    )
    db.commit()
    return {"message": "Groceries cleared", "deleted": deleted}
