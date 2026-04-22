from fastapi import APIRouter

cat_router = APIRouter()



@cat_router.get("/get_all")
async def get_all_categories():
    pass

@cat_router.post("/create")
async def create_category():
    pass