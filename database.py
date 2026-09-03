import json
import os
from typing import List, Dict

DB_FILE = "projects.json"

def load_projects() -> List[Dict]:
    if not os.path.exists(DB_FILE) or os.stat(DB_FILE).st_size == 0:
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_project(project_data: dict):
    projects = load_projects()
    projects.append(project_data)
    with open(DB_FILE, "w") as f:
        json.dump(projects, f, indent=2)

def delete_project(name: str) -> bool:
    projects = load_projects()
    filtered = [p for p in projects if p["project_name"].lower() != name.lower()]
    if len(filtered) < len(projects):
        with open(DB_FILE, "w") as f:
            json.dump(filtered, f, indent=2)
        return True
    return False