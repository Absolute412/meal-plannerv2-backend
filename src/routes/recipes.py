from fastapi import APIRouter, HTTPException
import httpx

router = APIRouter(prefix="/recipes", tags=["recipes"])

BASE_URL = "https://www.themealdb.com/api/json/v1/1"
TIMEOUT = httpx.Timeout(5.0)

@router.get("/search")
async def search_recipes(q: str):
    url = f"{BASE_URL}/search.php?s={q}"

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            res = await client.get(url)
            res.raise_for_status()
            data = res.json()
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="Upstream service unavailable")
    except httpx.RequestError:
        raise HTTPException(status_code=502 , detail="Upstream service unavailable")

    return data.get("meals") or []

@router.get("/{id}")
async def get_recipe(id: str):
    url = f"{BASE_URL}/lookup.php?i={id}"

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            res = await client.get(url)
            res.raise_for_status()
            data = res.json()
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="Upstream service unavailable")
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Upstream service unavailable")

    meals = data.get("meals")
    
    if not meals:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    meal = meals[0]
    ingredients = []

    for i in range(1, 21):
        ingredient = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")

        if ingredient and ingredient.strip():
            ingredients.append({
                "name": ingredient,
                "measure": measure.strip() if measure else ""
            })

    meal["ingredients"] = ingredients
    return meal