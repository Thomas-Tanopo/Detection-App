import os
import json
from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "frontend", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

def from_json(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return []
    return value or []

templates.env.filters["from_json"] = from_json
