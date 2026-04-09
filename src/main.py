from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.routes import meals, auth, recipes, groceries
from src.database import engine
from src.models.database_models import Base
import os

if os.getenv("ENV") == "local": 
    Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meals.router)
app.include_router(recipes.router)
app.include_router(groceries.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Welcome to Meal API"}

@app.get("/health")
def health():
    return {"status": "ok"}
