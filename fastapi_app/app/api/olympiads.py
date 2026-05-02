from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.models.models import Problem, ProblemTranslation, TestCase, ProblemSolve, User, Contest, ContestParticipation
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/problems")
async def get_problems(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    difficulty: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Problem).where(Problem.is_published == True)
    
    if difficulty:
        query = query.where(Problem.difficulty == difficulty)
    if category:
        query = query.where(Problem.category == category)
    if search:
        query = query.where(Problem.title.ilike(f"%{search}%"))
    
    query = query.order_by(Problem.id).offset(skip).limit(limit)
    result = await db.execute(query)
    problems = result.scalars().all()
    
    problem_ids = [p.id for p in problems]
    solves_result = await db.execute(
        select(ProblemSolve.problem_id, func.count(ProblemSolve.user_id))
        .where(ProblemSolve.problem_id.in_(problem_ids))
        .group_by(ProblemSolve.problem_id)
    )
    solves_map = dict(solves_result.all())
    
    response = []
    for problem in problems:
        problem_dict = {
            "id": problem.id,
            "title": problem.title,
            "difficulty": problem.difficulty,
            "time_limit": problem.time_limit,
            "memory_limit": problem.memory_limit,
            "is_published": problem.is_published,
            "author_id": problem.author_id,
            "created_at": problem.created_at,
            "updated_at": problem.updated_at,
            "category": problem.category,
            "solved_count": solves_map.get(problem.id, 0),
            "translations": [],
            "test_cases": []
        }
        response.append(problem_dict)
    
    return response

@router.get("/problems/{problem_id}")
async def get_problem(
    problem_id: int,
    lang: str = Query("ru", regex="^(tj|ru|en)$"),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    if not problem.is_published:
        raise HTTPException(status_code=403, detail="Problem is not published")

    translation_result = await db.execute(
        select(ProblemTranslation)
        .where(
            ProblemTranslation.problem_id == problem_id,
            ProblemTranslation.language == lang
        )
    )
    translation = translation_result.scalar_one_or_none()
    
    test_cases_result = await db.execute(
        select(TestCase)
        .where(TestCase.problem_id == problem_id, TestCase.is_sample == True)
        .order_by(TestCase.test_order)
    )
    test_cases = test_cases_result.scalars().all()
    
    solves_result = await db.execute(
        select(func.count(ProblemSolve.user_id))
        .where(ProblemSolve.problem_id == problem_id)
    )
    solved_count = solves_result.scalar() or 0
    
    response_data = {
        "id": problem.id,
        "title": translation.title if translation else problem.title,
        "difficulty": problem.difficulty,
        "time_limit": problem.time_limit,
        "memory_limit": problem.memory_limit,
        "is_published": problem.is_published,
        "author_id": problem.author_id,
        "created_at": problem.created_at,
        "updated_at": problem.updated_at,
        "category": problem.category,
        "solved_count": solved_count,
        "statement": translation.statement if translation else "",
        "input_format": translation.input_format if translation else "",
        "output_format": translation.output_format if translation else "",
        "notes": translation.notes if translation else "",
        "translations": [],
        "test_cases": [
            {
                "id": tc.id,
                "problem_id": tc.problem_id,
                "test_order": tc.test_order,
                "input_data": tc.input_data,
                "expected_output": tc.expected_output,
                "is_sample": tc.is_sample
            }
            for tc in test_cases
        ]
    }
    
    if translation:
        response_data["translations"].append({
            "id": translation.id,
            "problem_id": translation.problem_id,
            "language": translation.language,
            "title": translation.title,
            "statement": translation.statement,
            "input_format": translation.input_format,
            "output_format": translation.output_format,
            "notes": translation.notes
        })
    
    return response_data

@router.get("/contests")
async def get_contests(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(Contest).where(Contest.is_published == True)
    query = query.order_by(desc(Contest.start_time)).offset(skip).limit(limit)
    result = await db.execute(query)
    contests = result.scalars().all()
    
    return [
        {
            "id": c.id,
            "title": c.title,
            "description": c.description,
            "start_time": c.start_time,
            "end_time": c.end_time,
            "contest_type": c.contest_type,
            "owner_id": c.owner_id
        }
        for c in contests
    ]

@router.get("/contests/{contest_id}")
async def get_contest(
    contest_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Contest).where(Contest.id == contest_id))
    contest = result.scalar_one_or_none()
    
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    
    return {
        "id": contest.id,
        "title": contest.title,
        "description": contest.description,
        "start_time": contest.start_time,
        "end_time": contest.end_time,
        "is_published": contest.is_published,
        "contest_type": contest.contest_type,
        "owner_id": contest.owner_id
    }
