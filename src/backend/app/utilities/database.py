from typing import Any, List

def set_none_for_unavailable_relationships(model: Any, inclusion_paths: List[str]) -> Any:
    for path in inclusion_paths:
        segments = path.split(".")
        submodel = model
        
        for segment in segments:
            if segment == "*":
                break
            
            submodel = getattr(submodel, segment)
            
            if submodel is None:
                break
        
        if submodel is None:
            setattr(model, segments[-1], None)
        
    return model