import re
import os

with open(r'c:\Users\ionut\Desktop\Project\SPA_System\backend\main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Create directories
os.makedirs(r'c:\Users\ionut\Desktop\Project\SPA_System\backend\routers', exist_ok=True)

# 1. Extract Schemas (BaseModel classes)
schema_code = "from pydantic import BaseModel\nfrom typing import List, Optional\n\n"
schemas_match = re.finditer(r'(class \w+\(BaseModel\):[\s\S]*?)(?=class \w+\(BaseModel\)|@app|def verify_token|$)', content)
schemas = []
for match in schemas_match:
    cls_text = match.group(1).strip()
    if cls_text and 'class' in cls_text:
        schemas.append(cls_text)
        content = content.replace(cls_text, "")

schema_code += "\n\n".join(schemas)
with open(r'c:\Users\ionut\Desktop\Project\SPA_System\backend\schemas.py', 'w', encoding='utf-8') as f:
    f.write(schema_code)

# 2. Extract Routes
routers = {
    'students': [],
    'courses': [],
    'upload': [],
    'stats': [],
    'grades': []
}

routes_match = re.finditer(r'(@app\.(get|post|put|delete)\("([^"]+)"\)[\s\S]*?)(?=@app|$)', content)
for match in routes_match:
    full_route = match.group(1)
    path = match.group(3)
    
    # Change @app to @router
    route_code = full_route.replace('@app.', '@router.')
    
    if '/api/students' in path:
        routers['students'].append(route_code)
    elif '/api/courses' in path:
        routers['courses'].append(route_code)
    elif 'upload' in path or 'confirm' in path:
        routers['upload'].append(route_code)
    elif '/api/stats' in path:
        routers['stats'].append(route_code)
    elif '/api/grades' in path:
        routers['grades'].append(route_code)
    else:
        # keep in main.py (e.g. read_root)
        continue
    
    content = content.replace(full_route, "")

router_imports = """from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
import pandas as pd
import io
from fastapi import Header

def verify_token(authorization: str = Header(None)):
    if authorization != "Bearer sse-staff-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

router = APIRouter()

"""

for router_name, routes in routers.items():
    if not routes: continue
    code = router_imports + "\n\n".join(routes)
    with open(rf'c:\Users\ionut\Desktop\Project\SPA_System\backend\routers\{router_name}.py', 'w', encoding='utf-8') as f:
        f.write(code)

# 3. Rewrite main.py
new_main = content
new_main = new_main.replace("import models", "import models\nfrom routers import students, courses, upload, stats, grades")
new_main = new_main.replace('app = FastAPI(title="Study Progress Analysis API")', 
'''app = FastAPI(title="Study Progress Analysis API")
app.include_router(students.router, tags=["students"])
app.include_router(courses.router, tags=["courses"])
app.include_router(upload.router, tags=["upload"])
app.include_router(stats.router, tags=["stats"])
app.include_router(grades.router, tags=["grades"])
''')

with open(r'c:\Users\ionut\Desktop\Project\SPA_System\backend\main.py', 'w', encoding='utf-8') as f:
    f.write(new_main)
