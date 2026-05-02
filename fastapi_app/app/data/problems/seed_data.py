
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import Problem, ProblemTranslation, TestCase, Language


async def seed_problems(db: AsyncSession):
    
    

    problem1 = Problem(
        title="A + B",
        difficulty="easy",
        time_limit=1.0,
        memory_limit=256,
        is_published=True,
        category="math",
    )
    db.add(problem1)
    await db.flush()
    

    translations1 = [
        ProblemTranslation(
            problem_id=problem1.id,
            language=Language.RU,
            title="A + B",
            statement=,
            input_format="Два целых числа A и B в одной строке",
            output_format="Одно целое число — сумма A и B",
            notes="Числа могут быть отрицательными",
        ),
        ProblemTranslation(
            problem_id=problem1.id,
            language=Language.EN,
            title="A + B",
            statement=,
            input_format="Two integers A and B in a single line",
            output_format="A single integer — the sum of A and B",
            notes="Numbers can be negative",
        ),
        ProblemTranslation(
            problem_id=problem1.id,
            language=Language.TJ,
            title="A + B",
            statement=,
            input_format="Ду адади бутуни A ва B дар як сатр",
            output_format="Як адади бутун — йиғини A ва B",
            notes="Ададҳо метавонанд манфӣ бошанд",
        ),
    ]
    for t in translations1:
        db.add(t)
    

    test_cases1 = [
        TestCase(
            problem_id=problem1.id,
            test_order=1,
            input_data="2 3\n",
            expected_output="5\n",
            is_sample=True,
        ),
        TestCase(
            problem_id=problem1.id,
            test_order=2,
            input_data="-5 10\n",
            expected_output="5\n",
            is_sample=False,
        ),
        TestCase(
            problem_id=problem1.id,
            test_order=3,
            input_data="1000000000 1000000000\n",
            expected_output="2000000000\n",
            is_sample=False,
        ),
        TestCase(
            problem_id=problem1.id,
            test_order=4,
            input_data="0 0\n",
            expected_output="0\n",
            is_sample=False,
        ),
    ]
    for tc in test_cases1:
        db.add(tc)
    

    problem2 = Problem(
        title="Maximum of Three",
        difficulty="easy",
        time_limit=1.0,
        memory_limit=256,
        is_published=True,
        category="implementation",
    )
    db.add(problem2)
    await db.flush()
    

    translations2 = [
        ProblemTranslation(
            problem_id=problem2.id,
            language=Language.RU,
            title="Максимум из трёх",
            statement=,
            input_format="Три целых числа A, B и C в одной строке",
            output_format="Одно целое число — максимум из трёх",
        ),
        ProblemTranslation(
            problem_id=problem2.id,
            language=Language.EN,
            title="Maximum of Three",
            statement=,
            input_format="Three integers A, B and C in a single line",
            output_format="A single integer — the maximum of three",
        ),
        ProblemTranslation(
            problem_id=problem2.id,
            language=Language.TJ,
            title="Максимум аз се адад",
            statement=,
            input_format="Се адади бутуни A, B ва C дар як сатр",
            output_format="Як адади бутун — калонтарин аз се адад",
        ),
    ]
    for t in translations2:
        db.add(t)
    

    test_cases2 = [
        TestCase(
            problem_id=problem2.id,
            test_order=1,
            input_data="1 5 3\n",
            expected_output="5\n",
            is_sample=True,
        ),
        TestCase(
            problem_id=problem2.id,
            test_order=2,
            input_data="10 10 10\n",
            expected_output="10\n",
            is_sample=False,
        ),
        TestCase(
            problem_id=problem2.id,
            test_order=3,
            input_data="-1 -5 -3\n",
            expected_output="-1\n",
            is_sample=False,
        ),
        TestCase(
            problem_id=problem2.id,
            test_order=4,
            input_data="1000000000 -1000000000 0\n",
            expected_output="1000000000\n",
            is_sample=False,
        ),
    ]
    for tc in test_cases2:
        db.add(tc)
    

    problem3 = Problem(
        title="Factorial",
        difficulty="medium",
        time_limit=2.0,
        memory_limit=256,
        is_published=True,
        category="math",
    )
    db.add(problem3)
    await db.flush()
    

    translations3 = [
        ProblemTranslation(
            problem_id=problem3.id,
            language=Language.RU,
            title="Факториал",
            statement=,
            input_format="Одно целое число N",
            output_format="Одно целое число — N!",
            notes="Для N=20 ответ помещается в 64-битное целое число",
        ),
        ProblemTranslation(
            problem_id=problem3.id,
            language=Language.EN,
            title="Factorial",
            statement=,
            input_format="A single integer N",
            output_format="A single integer — N!",
            notes="For N=20 the answer fits in a 64-bit integer",
        ),
        ProblemTranslation(
            problem_id=problem3.id,
            language=Language.TJ,
            title="Факториал",
            statement=,
            input_format="Як адади бутуни N",
            output_format="Як адади бутун — N!",
            notes="Барои N=20 ҷавоб дар адади 64-бита ҷой мегирад",
        ),
    ]
    for t in translations3:
        db.add(t)
    

    test_cases3 = [
        TestCase(
            problem_id=problem3.id,
            test_order=1,
            input_data="5\n",
            expected_output="120\n",
            is_sample=True,
        ),
        TestCase(
            problem_id=problem3.id,
            test_order=2,
            input_data="0\n",
            expected_output="1\n",
            is_sample=False,
        ),
        TestCase(
            problem_id=problem3.id,
            test_order=3,
            input_data="1\n",
            expected_output="1\n",
            is_sample=False,
        ),
        TestCase(
            problem_id=problem3.id,
            test_order=4,
            input_data="10\n",
            expected_output="3628800\n",
            is_sample=False,
        ),
        TestCase(
            problem_id=problem3.id,
            test_order=5,
            input_data="20\n",
            expected_output="2432902008176640000\n",
            is_sample=False,
        ),
    ]
    for tc in test_cases3:
        db.add(tc)
    

    await db.commit()
    
    return {
        "problems_created": 3,
        "problem_ids": [problem1.id, problem2.id, problem3.id],
    }
