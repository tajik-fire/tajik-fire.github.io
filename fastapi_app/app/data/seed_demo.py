from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import Problem, ProblemTranslation, TestCase, Language, User
from datetime import datetime, timezone


async def seed_demo_problems(db: AsyncSession):
    result = await db.execute(select(User).where(User.id == 1))
    admin_user = result.scalar_one_or_none()
    
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzS3MebAJu",
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
    
    demo_problems = [
        {
            "title": "A+B",
            "difficulty": "easy",
            "time_limit": 1.0,
            "memory_limit": 256,
            "category": "math",
            "translations": [
                {
                    "language": Language.EN,
                    "title": "A+B",
                    "statement": "Calculate the sum of two numbers A and B.",
                    "input_format": "Two integers A and B (0 <= A, B <= 1000)",
                    "output_format": "One integer - the sum of A and B"
                },
                {
                    "language": Language.RU,
                    "title": "A+B",
                    "statement": "Вычислите сумму двух чисел A и B.",
                    "input_format": "Два целых числа A и B (0 <= A, B <= 1000)",
                    "output_format": "Одно целое число - сумма A и B"
                },
                {
                    "language": Language.TJ,
                    "title": "A+B",
                    "statement": "Ҷамъи ду адади A ва B-ро ҳисоб кунед.",
                    "input_format": "Ду адади бутуни A ва B (0 <= A, B <= 1000)",
                    "output_format": "Як адади бутун - ҷамъи A ва B"
                }
            ],
            "test_cases": [
                {"input": "1 2", "expected": "3", "is_sample": True},
                {"input": "10 20", "expected": "30", "is_sample": False},
                {"input": "100 200", "expected": "300", "is_sample": False}
            ]
        },
        {
            "title": "Hello World",
            "difficulty": "easy",
            "time_limit": 1.0,
            "memory_limit": 256,
            "category": "basic",
            "translations": [
                {
                    "language": Language.EN,
                    "title": "Hello World",
                    "statement": "Print 'Hello, World!' to the standard output.",
                    "input_format": "No input",
                    "output_format": "Print 'Hello, World!'"
                },
                {
                    "language": Language.RU,
                    "title": "Привет Мир",
                    "statement": "Выведите 'Hello, World!' в стандартный вывод.",
                    "input_format": "Нет входных данных",
                    "output_format": "Выведите 'Hello, World!'"
                },
                {
                    "language": Language.TJ,
                    "title": "Салом Дуниё",
                    "statement": "Сатри 'Hello, World!'-ро ба баромади стандартӣ чоп кунед.",
                    "input_format": "Воридот нест",
                    "output_format": "'Hello, World!'-ро чоп кунед"
                }
            ],
            "test_cases": [
                {"input": "", "expected": "Hello, World!", "is_sample": True}
            ]
        },
        {
            "title": "Maximum of Two Numbers",
            "difficulty": "easy",
            "time_limit": 1.0,
            "memory_limit": 256,
            "category": "math",
            "translations": [
                {
                    "language": Language.EN,
                    "title": "Maximum of Two Numbers",
                    "statement": "Given two integers A and B, find the maximum of them.",
                    "input_format": "Two integers A and B (-1000 <= A, B <= 1000)",
                    "output_format": "One integer - the maximum of A and B"
                },
                {
                    "language": Language.RU,
                    "title": "Максимум из двух чисел",
                    "statement": "Даны два целых числа A и B, найдите максимальное из них.",
                    "input_format": "Два целых числа A и B (-1000 <= A, B <= 1000)",
                    "output_format": "Одно целое число - максимум из A и B"
                },
                {
                    "language": Language.TJ,
                    "title": "Максимали ду адад",
                    "statement": "Ду адади бутуни A ва B дода шудааст, максимали онҳоро ёбед.",
                    "input_format": "Ду адади бутуни A ва B (-1000 <= A, B <= 1000)",
                    "output_format": "Як адади бутун - максимали A ва B"
                }
            ],
            "test_cases": [
                {"input": "5 10", "expected": "10", "is_sample": True},
                {"input": "20 15", "expected": "20", "is_sample": False},
                {"input": "-5 -10", "expected": "-5", "is_sample": False}
            ]
        },
        {
            "title": "Even or Odd",
            "difficulty": "easy",
            "time_limit": 1.0,
            "memory_limit": 256,
            "category": "math",
            "translations": [
                {
                    "language": Language.EN,
                    "title": "Even or Odd",
                    "statement": "Given an integer N, determine if it is even or odd.",
                    "input_format": "One integer N (-1000 <= N <= 1000)",
                    "output_format": "Print 'EVEN' if N is even, 'ODD' otherwise"
                },
                {
                    "language": Language.RU,
                    "title": "Четное или Нечетное",
                    "statement": "Дано целое число N, определите, четное оно или нечетное.",
                    "input_format": "Одно целое число N (-1000 <= N <= 1000)",
                    "output_format": "Выведите 'EVEN', если N четное, иначе 'ODD'"
                },
                {
                    "language": Language.TJ,
                    "title": "Ҷуфт ё Тоқ",
                    "statement": "Адади бутуни N дода шудааст, муайян кунед, ки он ҷуфт аст ё тоқ.",
                    "input_format": "Як адади бутуни N (-1000 <= N <= 1000)",
                    "output_format": "Агар N ҷуфт бошад 'EVEN', вагарна 'ODD' чоп кунед"
                }
            ],
            "test_cases": [
                {"input": "4", "expected": "EVEN", "is_sample": True},
                {"input": "7", "expected": "ODD", "is_sample": False},
                {"input": "0", "expected": "EVEN", "is_sample": False}
            ]
        },
        {
            "title": "Sum of Digits",
            "difficulty": "easy",
            "time_limit": 1.0,
            "memory_limit": 256,
            "category": "math",
            "translations": [
                {
                    "language": Language.EN,
                    "title": "Sum of Digits",
                    "statement": "Given a positive integer N, calculate the sum of its digits.",
                    "input_format": "One positive integer N (1 <= N <= 10000)",
                    "output_format": "One integer - the sum of digits of N"
                },
                {
                    "language": Language.RU,
                    "title": "Сумма цифр",
                    "statement": "Дано положительное целое число N, вычислите сумму его цифр.",
                    "input_format": "Одно положительное целое число N (1 <= N <= 10000)",
                    "output_format": "Одно целое число - сумма цифр N"
                },
                {
                    "language": Language.TJ,
                    "title": "Ҷамъи рақамҳо",
                    "statement": "Адади бутуни мусбати N дода шудааст, ҷамъи рақамҳои онро ҳисоб кунед.",
                    "input_format": "Як адади бутуни мусбати N (1 <= N <= 10000)",
                    "output_format": "Як адади бутун - ҷамъи рақамҳои N"
                }
            ],
            "test_cases": [
                {"input": "123", "expected": "6", "is_sample": True},
                {"input": "9999", "expected": "36", "is_sample": False},
                {"input": "1000", "expected": "1", "is_sample": False}
            ]
        }
    ]
    
    existing = await db.execute(select(Problem).where(Problem.title == "A+B"))
    if existing.scalar_one_or_none():
        return
    
    for prob_data in demo_problems:
        problem = Problem(
            title=prob_data["title"],
            difficulty=prob_data["difficulty"],
            time_limit=prob_data["time_limit"],
            memory_limit=prob_data["memory_limit"],
            category=prob_data["category"],
            is_published=True,
            author_id=admin_user.id
        )
        db.add(problem)
        await db.commit()
        await db.refresh(problem)
        
        for trans in prob_data["translations"]:
            translation = ProblemTranslation(
                problem_id=problem.id,
                language=trans["language"],
                title=trans["title"],
                statement=trans["statement"],
                input_format=trans["input_format"],
                output_format=trans["output_format"]
            )
            db.add(translation)
        
        for idx, test in enumerate(prob_data["test_cases"]):
            test_case = TestCase(
                problem_id=problem.id,
                test_order=idx,
                input_data=test["input"],
                expected_output=test["expected"],
                is_sample=test["is_sample"]
            )
            db.add(test_case)
        
        await db.commit()
    
    print(f"Seeded {len(demo_problems)} demo problems")
