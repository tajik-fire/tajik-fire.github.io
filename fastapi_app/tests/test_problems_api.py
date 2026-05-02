

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import User, Problem, ProblemTranslation, TestCase, Submission, Language


@pytest.mark.asyncio
async def test_get_problems_empty(client: AsyncClient, test_db: AsyncSession):
    response = await client.get("/api/olympiads/problems")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_create_problem(client: AsyncClient, test_db: AsyncSession):
    user = User(
        username="test_author",
        email="author@test.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    )
    test_db.add(user)
    await test_db.commit()
    
    problem_data = {
        "title": "Test Problem",
        "difficulty": "easy",
        "time_limit": 1.0,
        "memory_limit": 256,
        "category": "math",
        "translations": [
            {
                "language": "ru",
                "title": "Тестовая задача",
                "statement": "## Условие\n\nДаны два числа.",
                "input_format": "Два целых числа",
                "output_format": "Одно целое число"
            },
            {
                "language": "en",
                "title": "Test Problem",
                "statement": "## Statement\n\nGiven two numbers.",
                "input_format": "Two integers",
                "output_format": "One integer"
            }
        ],
        "test_cases": [
            {
                "test_order": 1,
                "input_data": "2 3\n",
                "expected_output": "5\n",
                "is_sample": True
            },
            {
                "test_order": 2,
                "input_data": "10 20\n",
                "expected_output": "30\n",
                "is_sample": False
            }
        ]
    }
    
    response = await client.post("/api/olympiads/problems", json=problem_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Problem"
    assert data["difficulty"] == "easy"
    assert len(data["translations"]) >= 0
    
    problem_id = data["id"]
    
    result = await test_db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    assert problem is not None
    assert problem.author_id == user.id


@pytest.mark.asyncio
async def test_get_problem_with_translation(client: AsyncClient, test_db: AsyncSession):
    user = User(
        username="test_author2",
        email="author2@test.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    )
    test_db.add(user)
    await test_db.commit()
    
    problem = Problem(
        title="A + B",
        difficulty="easy",
        time_limit=1.0,
        memory_limit=256,
        is_published=True,
        author_id=user.id,
        category="math"
    )
    test_db.add(problem)
    await test_db.flush()
    
    translation = ProblemTranslation(
        problem_id=problem.id,
        language=Language.RU,
        title="A + B",
        statement="## Условие\n\nДаны два числа A и B.",
        input_format="Два целых числа",
        output_format="Их сумма"
    )
    test_db.add(translation)
    
    test_case = TestCase(
        problem_id=problem.id,
        test_order=1,
        input_data="2 3\n",
        expected_output="5\n",
        is_sample=True
    )
    test_db.add(test_case)
    await test_db.commit()
    
    response = await client.get(f"/api/olympiads/problems/{problem.id}?lang=ru")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == problem.id
    assert len(data["test_cases"]) == 1
    assert data["test_cases"][0]["input_data"] == "2 3\n"


@pytest.mark.asyncio
async def test_create_submission(client: AsyncClient, test_db: AsyncSession):
    user = User(
        username="test_solver",
        email="solver@test.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    )
    test_db.add(user)
    await test_db.commit()
    
    problem = Problem(
        title="Simple Sum",
        difficulty="easy",
        time_limit=1.0,
        memory_limit=256,
        is_published=True,
        author_id=user.id
    )
    test_db.add(problem)
    await test_db.flush()
    
    test_case = TestCase(
        problem_id=problem.id,
        test_order=1,
        input_data="2 3\n",
        expected_output="5\n",
        is_sample=True
    )
    test_db.add(test_case)
    await test_db.commit()
    
    submission_data = {
        "problem_id": problem.id,
        "code": "a, b = map(int, input().split())\nprint(a + b)",
        "language": "python3"
    }
    
    response = await client.post("/api/olympiads/submissions", json=submission_data)
    assert response.status_code == 201
    data = response.json()
    assert data["problem_id"] == problem.id
    assert data["language"] == "python3"
    assert data["verdict"] == "pending"
    
    submission_id = data["id"]
    
    result = await test_db.execute(select(Submission).where(Submission.id == submission_id))
    submission = result.scalar_one_or_none()
    assert submission is not None
    assert submission.user_id == user.id


@pytest.mark.asyncio
async def test_get_submissions(client: AsyncClient, test_db: AsyncSession):
    user = User(
        username="test_solver2",
        email="solver2@test.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    )
    test_db.add(user)
    await test_db.commit()
    
    problem = Problem(
        title="Test",
        difficulty="easy",
        is_published=True,
        author_id=user.id
    )
    test_db.add(problem)
    await test_db.flush()
    
    submission = Submission(
        user_id=user.id,
        problem_id=problem.id,
        code="print(1)",
        language="python3"
    )
    test_db.add(submission)
    await test_db.commit()
    
    response = await client.get(f"/api/olympiads/submissions?problem_id={problem.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_problem_status_not_solved(client: AsyncClient, test_db: AsyncSession):
    user = User(
        username="test_user_status",
        email="status@test.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW"
    )
    test_db.add(user)
    await test_db.commit()
    
    problem = Problem(
        title="Status Test",
        difficulty="easy",
        is_published=True,
        author_id=user.id
    )
    test_db.add(problem)
    await test_db.commit()
    
    response = await client.get(f"/api/olympiads/problems/{problem.id}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["solved"] is False
    assert data["attempts"] == 0
