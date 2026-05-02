import os
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent.parent
PROBLEMS_DIR = BASE_DIR / "app" / "data" / "problems"


def get_problem_meta(problem_id: str) -> dict:
    problem_path = PROBLEMS_DIR / problem_id
    meta_file = problem_path / "meta.json"
    
    if not meta_file.exists():
        return {}
    
    with open(meta_file, "r", encoding="utf-8") as f:
        return json.load(f)


def get_problem_statement(problem_id: str, language: str) -> dict:
    problem_path = PROBLEMS_DIR / problem_id
    statement_file = problem_path / language / "statement.md"
    
    if not statement_file.exists():
        return {"title": "", "content": ""}
    
    with open(statement_file, "r", encoding="utf-8") as f:
        content = f.read()
    
    title = ""
    if content.startswith("#"):
        first_line = content.split("\n")[0]
        title = first_line.replace("#", "").strip()
    
    return {"title": title, "content": content}


def get_test_cases(problem_id: str) -> list:
    problem_path = PROBLEMS_DIR / problem_id
    tests_dir = problem_path / "tests"
    
    if not tests_dir.exists():
        return []
    
    test_cases = []
    for in_file in sorted(tests_dir.glob("*.in")):
        out_file = in_file.with_suffix(".out")
        
        if not out_file.exists():
            continue
        
        with open(in_file, "r", encoding="utf-8") as f:
            input_data = f.read()
        
        with open(out_file, "r", encoding="utf-8") as f:
            expected_output = f.read()
        
        test_order = int(in_file.stem)
        is_sample = test_order <= 3
        
        test_cases.append({
            "test_order": test_order,
            "input_data": input_data,
            "expected_output": expected_output,
            "is_sample": is_sample
        })
    
    return test_cases


def list_all_problems() -> list:
    if not PROBLEMS_DIR.exists():
        return []
    
    problems = []
    for problem_dir in PROBLEMS_DIR.iterdir():
        if problem_dir.is_dir():
            meta = get_problem_meta(problem_dir.name)
            if meta:
                problems.append({
                    "problem_id": problem_dir.name,
                    "meta": meta
                })
    
    return problems


def sync_problems_to_db(db):
    from app.models.models import Problem, TestCase, ProblemTranslation
    
    problems_data = list_all_problems()
    
    for problem_data in problems_data:
        problem_id = problem_data["problem_id"]
        meta = problem_data["meta"]
        
        existing = db.query(Problem).filter(Problem.title == problem_id).first()
        
        if existing:
            existing.difficulty = meta.get("difficulty", "easy")
            existing.time_limit = meta.get("time_limit", 1.0)
            existing.memory_limit = meta.get("memory_limit", 256)
            existing.category = ",".join(meta.get("tags", []))
            existing.is_published = True
        else:
            problem = Problem(
                title=problem_id,
                difficulty=meta.get("difficulty", "easy"),
                time_limit=meta.get("time_limit", 1.0),
                memory_limit=meta.get("memory_limit", 256),
                category=",".join(meta.get("tags", [])),
                is_published=True
            )
            db.add(problem)
            db.flush()
            
            for lang in ["ru", "en", "tj"]:
                statement_data = get_problem_statement(problem_id, lang)
                if statement_data["content"]:
                    translation = ProblemTranslation(
                        problem_id=problem.id,
                        language=lang,
                        title=statement_data["title"],
                        statement=statement_data["content"]
                    )
                    db.add(translation)
            
            test_cases = get_test_cases(problem_id)
            for tc in test_cases:
                test_case = TestCase(
                    problem_id=problem.id,
                    test_order=tc["test_order"],
                    input_data=tc["input_data"],
                    expected_output=tc["expected_output"],
                    is_sample=tc["is_sample"]
                )
                db.add(test_case)
    
    db.commit()
