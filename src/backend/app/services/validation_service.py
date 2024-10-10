import json
from fastapi import Depends
from ai.prompts import AssertionPrompt
from .user_service import UserService
from common.cache import get_key, set_key
from domain.dto.ai.assertion_result import AssertionResultDto

class ValidationService:
    user_service: UserService
    
    def __init__(self, user_service: UserService = Depends(UserService)):
        self.user_service = user_service
    
    async def perform_assertion(self, statement: str) -> AssertionResultDto:
        prompt = AssertionPrompt()
        
        cache_key = _get_cache_key(statement)
        existing_result = await get_key(cache_key)
        
        if existing_result:
            return AssertionResultDto(**json.loads(existing_result))
        
        assertion, reason = prompt.get_assertion(statement=statement)
        
        result = AssertionResultDto(
            assertion=assertion, 
            reason=reason
        )
        
        await set_key(cache_key, result.model_dump_json())
        
        return result
        
def _get_cache_key(statement: str) -> str:
    return f"assertion_{statement}"