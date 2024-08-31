def pydantic_inline_ref_schema(schema):
    # Check if $defs is in the schema
    if '$defs' not in schema:
        return schema

    defs = schema['$defs']

    def resolve_ref(ref):
        # Remove leading '#/$defs/' and resolve reference
        ref_name = ref.split('/')[-1]
        return defs.get(ref_name, {})

    def _inline_refs(sub_schema):
        if isinstance(sub_schema, dict):
            new_schema = {}
            for key, value in sub_schema.items():
                if key == '$ref':
                    # Replace $ref with the actual definition
                    resolved = resolve_ref(value)
                    new_schema.update(_inline_refs(resolved))
                else:
                    new_schema[key] = _inline_refs(value)
            return new_schema
        elif isinstance(sub_schema, list):
            return [_inline_refs(item) for item in sub_schema]
        else:
            return sub_schema

    # Inline the refs in the top-level schema
    inlined_schema = _inline_refs(schema)

    # Remove the $defs section from the schema
    if '$defs' in inlined_schema:
        del inlined_schema['$defs']

    return inlined_schema