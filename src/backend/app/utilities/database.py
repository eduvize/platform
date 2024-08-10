from typing import Any, List, Optional, Set

from sqlalchemy import inspect
from sqlalchemy.orm import selectinload


def recursive_load_options(
    model: Any, 
    path: Optional[str] = None, 
    load_all: bool = False, 
    visited_models: Optional[Set] = None, 
    base_load: Optional[any] = None
) -> List[Any]:
    options = []
    
    if visited_models is None:
        visited_models = set()
        
    visited_models.add(model)
    
    def get_relationship_keys(model):
        relationships = inspect(model).relationships
        return relationships.keys()
    
    relationships = get_relationship_keys(model)
    
    def make_join(load):
        if base_load:
            return base_load.selectinload(load)
        return selectinload(load)
    
    applicable_relationships = [
        relationship
        for relationship in relationships
        if getattr(model, relationship).property.mapper.class_ not in visited_models
    ]
    
    print(f"{model} applicable relationships: {applicable_relationships}")
    
    if path:
        print(f"Path: {path}")
        segments = path.split(".")
        
        for segment in segments:
            if segment == "*":
                print(f"Recurse through all relationships of {model}")
                addl = recursive_load_options(model, visited_models=visited_models, load_all=True, base_load=base_load)
                options.extend(addl)
            else:
                submodel = getattr(model, segment)
                submodel_type = submodel.property.mapper.class_
                submodel_relationships = get_relationship_keys(submodel_type)
                
                base_load = make_join(submodel)
                
                options.extend([
                    make_join(t)
                    for t in [
                        getattr(submodel_type, key)
                        for key in submodel_relationships
                        if getattr(submodel_type, key).property.mapper.class_ not in visited_models
                    ]
                ])
                
                model = submodel_type
    elif load_all and any(applicable_relationships):
        options.extend([
            make_join(t)
            for t in [
                getattr(model, key)
                for key in applicable_relationships
                if getattr(model, key).property.mapper.class_ not in visited_models
            ]
        ])
        
        for relationship in applicable_relationships:
            submodel_attr = getattr(model, relationship)
            submodel = submodel_attr.property.mapper.class_
            load = make_join(submodel_attr)
            options.extend(recursive_load_options(submodel, visited_models=visited_models, base_load=load, load_all=True))

    return options