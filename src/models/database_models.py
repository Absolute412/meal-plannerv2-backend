from sqlalchemy import ForeignKey, UniqueConstraint
from src.database import Base 
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Date, String
from datetime import date

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    meals: Mapped[list["Meal"]] = relationship("Meal", back_populates="user")
    groceries: Mapped[list["Grocery"]] = relationship("Grocery", back_populates="user")

class Meal(Base):
    __tablename__ = "meals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    meal_type: Mapped[str] = mapped_column(String, nullable=False)  # breakfast/lunch/dinner/snack
    meal_date: Mapped[date] = mapped_column(Date, default=date.today)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="meals")
    ingredients: Mapped[list["Ingredient"]] = relationship(
        "Ingredient",
        back_populates="meal",
        cascade="all, delete-orphan"
    )

class Ingredient(Base):
    __tablename__ = "meal_ingredients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    meal_id: Mapped[int] = mapped_column(ForeignKey("meals.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    measure: Mapped[str | None] = mapped_column(String, nullable=True)

    meal: Mapped["Meal"] = relationship("Meal", back_populates="ingredients")

class Grocery(Base):
    __tablename__ = "groceries"
    __table_args__ = (
        UniqueConstraint("user_id", "name", "measure", name="uq_grocery_user_name_measure"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    measure: Mapped[str | None] = mapped_column(String, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="groceries")
