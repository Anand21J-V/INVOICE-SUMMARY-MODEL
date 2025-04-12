# Function to clean empty fields
def clean_empty_fields(data):
    if isinstance(data, dict):
        return {k: clean_empty_fields(v) for k, v in data.items() if v not in ("", [], {}, None)}
    elif isinstance(data, list):
        return [clean_empty_fields(v) for v in data if v not in ("", [], {}, None)]
    return data





