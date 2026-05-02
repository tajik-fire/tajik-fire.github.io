from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.models.models import (
    Problem, ProblemTranslation, TestCase, Submission, 
    ProblemSolve, User, Language, Verdict, ProgrammingLanguage
)
from app.schemas.schemas import (
    ProblemResponse, ProblemCreate, ProblemUpdate,
    SubmissionResponse, SubmissionCreate,
    ProblemTranslationResponse, TestCaseResponse
)
from app.services.judger.judger import process_submission

from app.api.auth import get_current_user

router = APIRouter()


@router.get("/problems", response_model=List[ProblemResponse])
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


@router.get("/problems/{problem_id}", response_model=ProblemResponse)
async def get_problem(
    problem_id: int,
    lang: str = Query("ru", regex="^(tj|ru|en)$"),
    db: AsyncSession = Depends(get_db)
):
    
    result = await db.execute(
        select(Problem).where(Problem.id == problem_id)
    )
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


@router.post("/problems", response_model=ProblemResponse, status_code=status.HTTP_201_CREATED)
async def create_problem(
    problem_data: ProblemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    problem = Problem(
        title=problem_data.title,
        difficulty=problem_data.difficulty,
        time_limit=problem_data.time_limit,
        memory_limit=problem_data.memory_limit,
        category=problem_data.category,
        author_id=current_user.id,
        is_published=False
    )
    db.add(problem)
    await db.flush()
    

    for trans in problem_data.translations:
        translation = ProblemTranslation(
            problem_id=problem.id,
            language=trans.language,
            title=trans.title,
            statement=trans.statement,
            input_format=trans.input_format,
            output_format=trans.output_format,
            notes=trans.notes
        )
        db.add(translation)
    

    for i, test in enumerate(problem_data.test_cases):
        test_case = TestCase(
            problem_id=problem.id,
            test_order=test.test_order,
            input_data=test.input_data,
            expected_output=test.expected_output,
            is_sample=test.is_sample
        )
        db.add(test_case)
    
    await db.commit()
    await db.refresh(problem)
    
    return {
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
        "solved_count": 0,
        "translations": [],
        "test_cases": []
    }


@router.put("/problems/{problem_id}", response_model=ProblemResponse)
async def update_problem(
    problem_id: int,
    problem_data: ProblemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    result = await db.execute(
        select(Problem).where(Problem.id == problem_id)
    )
    problem = result.scalar_one_or_none()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    if problem.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    update_data = problem_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(problem, field, value)
    
    problem.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(problem)
    
    return {
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
        "solved_count": 0,
        "translations": [],
        "test_cases": []
    }


@router.post("/submissions", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    submission_data: SubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    problem_result = await db.execute(
        select(Problem).where(Problem.id == submission_data.problem_id)
    )
    problem = problem_result.scalar_one_or_none()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    if not problem.is_published:
        raise HTTPException(status_code=403, detail="Problem is not published")
    
    submission = Submission(
        user_id=current_user.id,
        problem_id=submission_data.problem_id,
        code=submission_data.code,
        language=submission_data.language,
        verdict=Verdict.PENDING
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)
    

    import asyncio
    asyncio.create_task(process_submission(submission.id, db))
    
    return {
        "id": submission.id,
        "user_id": submission.user_id,
        "problem_id": submission.problem_id,
        "code": submission.code[:100] + "...",
        "language": submission.language,
        "verdict": submission.verdict,
        "execution_time": submission.execution_time,
        "memory_used": submission.memory_used,
        "test_passed": submission.test_passed,
        "test_total": submission.test_total,
        "error_message": submission.error_message,
        "created_at": submission.created_at,
        "judged_at": submission.judged_at
    }


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    result = await db.execute(
        select(Submission).where(Submission.id == submission_id)
    )
    submission = result.scalar_one_or_none()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    problem_result = await db.execute(
        select(Problem).where(Problem.id == submission.problem_id)
    )
    problem = problem_result.scalar_one_or_none()
    
    if problem and problem.author_id != current_user.id and submission.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return {
        "id": submission.id,
        "user_id": submission.user_id,
        "problem_id": submission.problem_id,
        "code": submission.code,
        "language": submission.language,
        "verdict": submission.verdict,
        "execution_time": submission.execution_time,
        "memory_used": submission.memory_used,
        "test_passed": submission.test_passed,
        "test_total": submission.test_total,
        "error_message": submission.error_message,
        "created_at": submission.created_at,
        "judged_at": submission.judged_at
    }


@router.get("/submissions")
async def get_submissions(
    problem_id: Optional[int] = None,
    user_id: Optional[int] = None,
    verdict: Optional[str] = None,
    language: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    query = select(Submission)
    
    if problem_id:
        query = query.where(Submission.problem_id == problem_id)
    if user_id:
        query = query.where(Submission.user_id == user_id)
    if verdict:
        query = query.where(Submission.verdict == verdict)
    if language:
        query = query.where(Submission.language == language)
    
    query = query.order_by(desc(Submission.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    submissions = result.scalars().all()
    
    return [
        {
            "id": s.id,
            "user_id": s.user_id,
            "problem_id": s.problem_id,
            "language": s.language,
            "verdict": s.verdict,
            "execution_time": s.execution_time,
            "memory_used": s.memory_used,
            "test_passed": s.test_passed,
            "test_total": s.test_total,
            "created_at": s.created_at,
            "judged_at": s.judged_at
        }
        for s in submissions
    ]


@router.get("/problems/{problem_id}/status")
async def get_problem_status(
    problem_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    
    solve_result = await db.execute(
        select(ProblemSolve)
        .where(
            ProblemSolve.problem_id == problem_id,
            ProblemSolve.user_id == current_user.id
        )
    )
    solve = solve_result.scalar_one_or_none()
    
    if solve:
        return {"solved": True, "solved_at": solve.solved_at, "attempts": solve.attempts_before_solve}
    
    attempts_result = await db.execute(
        select(func.count(Submission.id))
        .where(
            Submission.problem_id == problem_id,
            Submission.user_id == current_user.id
        )
    )
    attempts = attempts_result.scalar() or 0
    
    return {"solved": False, "attempts": attempts}
