import json
from fastapi import Depends
from ai.prompts import AssertionPrompt
from app.routing.contracts import AssertionResult
from app.services import UserService
from common.cache import get_key, set_key

class ValidationService:
    user_service: UserService
    
    def __init__(self, user_service: UserService = Depends(UserService)):
        self.user_service = user_service
    
    async def perform_assertion(self, statement: str) -> AssertionResult:
        prompt = AssertionPrompt()
        
        cache_key = _get_cache_key(statement)
        existing_result = get_key(cache_key)
        
        if existing_result:
            return AssertionResult(**json.loads(existing_result))
        
        assertion, reason = prompt.get_assertion(statement=statement)
        
        result = AssertionResult(
            assertion=assertion, 
            reason=reason
        )
        
        set_key(cache_key, result.model_dump_json())
        
        return result
        
def _get_cache_key(statement: str) -> str:
    return f"assertion_{statement}"