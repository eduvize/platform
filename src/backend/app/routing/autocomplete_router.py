from fastapi import APIRouter, Depends
from app.services.autocomplete_service import AutocompleteService
from app.routing.middleware.token_middleware import token_extractor

router = APIRouter(
    prefix="/autocomplete",
    dependencies=[
        Depends(token_extractor),
    ]
)

@router.get("/programming-languages")
async def get_autocomplete_options(query: str, autocomplete_service: AutocompleteService = Depends(AutocompleteService)):
    """
    Retrieves a list of programming languages for use in an autocomplete field
    """
    return autocomplete_service.get_programming_languages(query)
    
@router.get("/libraries")
async def get_library_options(subjects: str, query: str, autocomplete_service: AutocompleteService = Depends(AutocompleteService)):
    """
    Retrieves a list of libraries for use in an autocomplete field
    """
    subject_list = subjects.split(",")
    return autocomplete_service.get_libraries(subject_list, query)

@router.get("/educational-institutions")
async def get_educational_institution_options(query: str, autocomplete_service: AutocompleteService = Depends(AutocompleteService)):
    """
    Retrieves a list of educational institutions for use in an autocomplete field
    """
    return autocomplete_service.get_educational_institutions(query)