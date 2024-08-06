from fastapi import APIRouter, Depends
from config import get_dashboard_endpoint
from .responses import raise_bad_request, redirect_ui
from app.utilities.endpoints import get_public_ui_endpoint
from app.services.user_onboarding_service import UserOnboardingService, VerificationExpiredError

router = APIRouter(
    prefix="/onboarding",
)

@router.get("/verify")
async def verify_user(code: str, user_onboarding_service: UserOnboardingService = Depends(UserOnboardingService)):
    try:
        await user_onboarding_service.verify_user(code)
        
        # If successful, redirect them to the dashboard
        dashboard_endpoint = get_dashboard_endpoint()
        return redirect_ui(dashboard_endpoint)
    except ValueError as e:
        raise_bad_request(str(e))
    except VerificationExpiredError as e:
        raise_bad_request(str(e))