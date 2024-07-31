from fastapi import APIRouter
from . import api_router

router = APIRouter(prefix="/users")

@router.api_route("/me")
async def get_me():
    return {"username": "fakecurrentuser"}