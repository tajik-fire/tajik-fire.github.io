from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
from app.db.database import get_db
from app.models.models import User, Problem, Contest, ContestProblem, ContestParticipation, Submission, ProblemTranslation, TestCase, Language, Verdict
from app.schemas.problem import ProblemCreate, ProblemUpdate, ProblemResponse, ContestCreate, ContestUpdate, ContestResponse, ContestProblemCreate
from app.api.auth import get_current_user

router = APIRouter()


def is_admin(user: User):
    return user.is_active and user.id == 1


@router.get("/admin/problems", response_model=List[ProblemResponse])
async def admin_get_problems(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    problems = db.query(Problem).offset(skip).limit(limit).all()
    return problems


@router.post("/admin/problems", response_model=ProblemResponse)
async def admin_create_problem(
    problem_data: ProblemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    problem = Problem(
        title=problem_data.title,
        difficulty=problem_data.difficulty or "easy",
        time_limit=problem_data.time_limit or 1.0,
        memory_limit=problem_data.memory_limit or 256,
        is_published=problem_data.is_published or False,
        author_id=current_user.id,
        category=problem_data.category
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    
    if problem_data.translations:
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
        db.commit()
    
    if problem_data.test_cases:
        for idx, test in enumerate(problem_data.test_cases):
            test_case = TestCase(
                problem_id=problem.id,
                test_order=idx,
                input_data=test.input_data,
                expected_output=test.expected_output,
                is_sample=test.is_sample or False
            )
            db.add(test_case)
        db.commit()
    
    return problem


@router.put("/admin/problems/{problem_id}", response_model=ProblemResponse)
async def admin_update_problem(
    problem_id: int,
    problem_data: ProblemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    update_data = problem_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(problem, field, value)
    
    db.commit()
    db.refresh(problem)
    return problem


@router.delete("/admin/problems/{problem_id}")
async def admin_delete_problem(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    db.delete(problem)
    db.commit()
    return {"message": "Problem deleted"}


@router.get("/admin/contests", response_model=List[ContestResponse])
async def admin_get_contests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    contests = db.query(Contest).offset(skip).limit(limit).all()
    return contests


@router.post("/admin/contests", response_model=ContestResponse)
async def admin_create_contest(
    contest_data: ContestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    contest = Contest(
        title=contest_data.title,
        description=contest_data.description,
        start_time=contest_data.start_time,
        end_time=contest_data.end_time,
        is_published=contest_data.is_published or False,
        contest_type=contest_data.contest_type or "standard",
        owner_id=current_user.id
    )
    db.add(contest)
    db.commit()
    db.refresh(contest)
    
    if contest_data.problem_ids:
        for idx, problem_id in enumerate(contest_data.problem_ids):
            contest_problem = ContestProblem(
                contest_id=contest.id,
                problem_id=problem_id,
                position=idx + 1,
                points=1
            )
            db.add(contest_problem)
        db.commit()
    
    return contest


@router.put("/admin/contests/{contest_id}", response_model=ContestResponse)
async def admin_update_contest(
    contest_id: int,
    contest_data: ContestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    
    update_data = contest_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contest, field, value)
    
    db.commit()
    db.refresh(contest)
    return contest


@router.delete("/admin/contests/{contest_id}")
async def admin_delete_contest(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    
    db.delete(contest)
    db.commit()
    return {"message": "Contest deleted"}


@router.get("/admin/contests/{contest_id}/results")
async def admin_get_contest_results(
    contest_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    
    participations = db.query(ContestParticipation).filter(
        ContestParticipation.contest_id == contest_id
    ).order_by(ContestParticipation.rank).all()
    
    results = []
    for p in participations:
        user = db.query(User).filter(User.id == p.user_id).first()
        results.append({
            "rank": p.rank,
            "user_id": p.user_id,
            "username": user.username if user else "Unknown",
            "score": p.score,
            "penalty": p.penalty,
            "finish_time": p.finish_time
        })
    
    return {
        "contest_id": contest.id,
        "contest_title": contest.title,
        "results": results
    }


@router.post("/admin/contests/{contest_id}/problems")
async def admin_add_problem_to_contest(
    contest_id: int,
    problem_data: ContestProblemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    
    problem = db.query(Problem).filter(Problem.id == problem_data.problem_id).first()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    existing = db.query(ContestProblem).filter(
        ContestProblem.contest_id == contest_id,
        ContestProblem.problem_id == problem_data.problem_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Problem already in contest")
    
    max_position = db.query(ContestProblem.position).filter(
        ContestProblem.contest_id == contest_id
    ).order_by(ContestProblem.position.desc()).first()
    position = (max_position[0] + 1) if max_position and max_position[0] else 1
    
    contest_problem = ContestProblem(
        contest_id=contest_id,
        problem_id=problem_data.problem_id,
        position=position,
        points=problem_data.points or 1
    )
    db.add(contest_problem)
    db.commit()
    db.refresh(contest_problem)
    
    return contest_problem


@router.delete("/admin/contests/{contest_id}/problems/{problem_id}")
async def admin_remove_problem_from_contest(
    contest_id: int,
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    contest_problem = db.query(ContestProblem).filter(
        ContestProblem.contest_id == contest_id,
        ContestProblem.problem_id == problem_id
    ).first()
    if not contest_problem:
        raise HTTPException(status_code=404, detail="Contest problem not found")
    
    db.delete(contest_problem)
    db.commit()
    return {"message": "Problem removed from contest"}


@router.get("/admin/users")
async def admin_get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = db.query(User).offset(skip).limit(limit).all()
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_active": u.is_active,
            "is_verified": u.is_verified,
            "rating": u.rating,
            "solved_count": u.solved_count
        }
        for u in users
    ]
