from fastapi import APIRouter, Depends
from app.services import AutocompleteService
from app.routing.middleware import token_validator

router = APIRouter(
    prefix="/autocomplete",
    dependencies=[
        Depends(token_validator),
    ]
)

@router.get("/programming-languages")
async def get_autocomplete_options(
    disciplines: str, 
    query: str, 
    autocomplete_service: AutocompleteService = Depends(AutocompleteService)
):
    """
    Retrieves a list of programming languages for use in an autocomplete field
    """
    discipline_list = disciplines.split(",")
    return autocomplete_service.get_programming_languages(discipline_list, query)
    
@router.get("/libraries")
async def get_library_options(
    subjects: str, 
    languages: str, 
    query: str, 
    autocomplete_service: AutocompleteService = Depends(AutocompleteService)
):
    """
    Retrieves a list of libraries for use in an autocomplete field
    """
    subject_list = subjects.split(",")
    language_list = languages.split(",")
    
    return autocomplete_service.get_libraries(
        subjects=subject_list, 
        languages=language_list, 
        query=query
    )

@router.get("/educational-institutions")
async def get_educational_institution_options(
    query: str, 
    autocomplete_service: AutocompleteService = Depends(AutocompleteService)
):
    """
    Retrieves a list of educational institutions for use in an autocomplete field
    """
    return autocomplete_service.get_educational_institutions(
        query=query
    )

@router.get("/educational-focuses")
async def get_educational_focus_options(
    school_name: str, 
    query: str, 
    autocomplete_service: AutocompleteService = Depends(AutocompleteService)
):
    """
    Retrieves a list of educational focuses for use in an autocomplete field
    """
    return autocomplete_service.get_educational_focuses(
        school_name=school_name, 
        query=query
    )