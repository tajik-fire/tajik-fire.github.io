from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.db.database import get_db
from app.models.models import LearningModule, LearningProblem, LearningEnrollment, Problem, User
from app.api.auth import get_current_user

router = APIRouter()

@router.get("/modules")
async def get_learning_modules(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(LearningModule).where(LearningModule.is_published == True)
    query = query.order_by(LearningModule.order).offset(skip).limit(limit)
    result = await db.execute(query)
    modules = result.scalars().all()
    
    return [
        {
            "id": m.id,
            "title": m.title,
            "slug": m.slug,
            "description": m.description,
            "order": m.order,
            "theory_content": m.theory_content
        }
        for m in modules
    ]

@router.get("/modules/{module_id}")
async def get_learning_module(
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(LearningModule).where(LearningModule.id == module_id))
    module = result.scalar_one_or_none()
    
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    problems_result = await db.execute(
        select(LearningProblem, Problem)
        .join(Problem, LearningProblem.problem_id == Problem.id)
        .where(LearningProblem.module_id == module_id)
        .order_by(LearningProblem.order)
    )
    problems = problems_result.all()
    
    enrollment_result = await db.execute(
        select(LearningEnrollment)
        .where(
            LearningEnrollment.module_id == module_id,
            LearningEnrollment.user_id == current_user.id
        )
    )
    enrollment = enrollment_result.scalar_one_or_none()
    
    return {
        "id": module.id,
        "title": module.title,
        "slug": module.slug,
        "description": module.description,
        "theory_content": module.theory_content,
        "order": module.order,
        "problems": [
            {
                "id": lp.problem_id,
                "order": lp.order,
                "title": p.title,
                "difficulty": p.difficulty
            }
            for lp, p in problems
        ],
        "enrolled": enrollment is not None,
        "progress": enrollment.progress if enrollment else 0
    }

@router.post("/modules/{module_id}/enroll")
async def enroll_in_module(
    module_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(LearningModule).where(LearningModule.id == module_id))
    module = result.scalar_one_or_none()
    
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    
    enrollment_result = await db.execute(
        select(LearningEnrollment)
        .where(
            LearningEnrollment.module_id == module_id,
            LearningEnrollment.user_id == current_user.id
        )
    )
    enrollment = enrollment_result.scalar_one_or_none()
    
    if enrollment:
        return {"message": "Already enrolled"}
    
    enrollment = LearningEnrollment(
        user_id=current_user.id,
        module_id=module_id,
        progress=0
    )
    db.add(enrollment)
    await db.commit()
    
    return {"message": "Successfully enrolled"}

@router.get("/my-modules")
async def get_my_modules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(LearningEnrollment, LearningModule)
        .join(LearningModule, LearningEnrollment.module_id == LearningModule.id)
        .where(LearningEnrollment.user_id == current_user.id)
        .order_by(LearningEnrollment.enrolled_at)
    )
    enrollments = result.all()
    
    return [
        {
            "id": module.id,
            "title": module.title,
            "slug": module.slug,
            "description": module.description,
            "progress": enrollment.progress,
            "completed_at": enrollment.completed_at,
            "enrolled_at": enrollment.enrolled_at
        }
        for enrollment, module in enrollments
    ]
