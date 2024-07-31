from . import api_router

@api_router.api_route("/users/me")
async def get_me():
    return {"username": "fakecurrentuser"}