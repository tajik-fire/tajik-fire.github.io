
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.models import User, Problem, ProblemTranslation, TestCase, Language


async def seed_problems(db: AsyncSession):
    
    

    result = await db.execute(select(User).where(User.username == "problem_author"))
    author = result.scalar_one_or_none()
    
    if not author:
        author = User(
            username="problem_author",
            email="author@problems.com",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            is_verified=True
        )
        db.add(author)
        await db.flush()
    

    problem1 = Problem(
        title="A + B",
        difficulty="easy",
        time_limit=1.0,
        memory_limit=256,
        is_published=True,
        author_id=author.id,
        category="math"
    )
    db.add(problem1)
    await db.flush()
    

    translations1 = [
        ProblemTranslation(
            problem_id=problem1.id,
            language=Language.RU,
            title="A + B",
            statement="## Условие\n\nДаны два целых числа A и B. Требуется вычислить их сумму.\n\n### Входные данные\n\nВ единственной строке записаны два целых числа A и B (0 ≤ A, B ≤ 100).\n\n### Выходные данные\n\nВыведите одно целое число — сумму A и B.",
            input_format="Два целых числа A и B",
            output_format="Одно целое число — сумма",
            notes="Пример:\n\nВход: `2 3`\nВыход: `5`"
        ),
        ProblemTranslation(
            problem_id=problem1.id,
            language=Language.EN,
            title="A + B",
            statement="## Problem Statement\n\nGiven two integers A and B. Calculate their sum.\n\n### Input\n\nTwo integers A and B (0 ≤ A, B ≤ 100).\n\n### Output\n\nPrint one integer — the sum of A and B.",
            input_format="Two integers A and B",
            output_format="One integer — the sum",
            notes="Example:\n\nInput: `2 3`\nOutput: `5`"
        ),
        ProblemTranslation(
            problem_id=problem1.id,
            language=Language.TJ,
            title="A + B",
            statement="## Шарт\n\nДу адади бутуншудаи A ва B дода шудааст. Йиғинии онҳоро ёбед.\n\n### Додаҳо\n\nДар сатри ягона ду адади бутуншудаи A ва B (0 ≤ A, B ≤ 100) навишта шудаанд.\n\n### Баромад\n\nЯк адади бутуншударо чоп кунед — йиғинии A ва B.",
            input_format="Ду адади бутуншудаи A ва B",
            output_format="Як адади бутуншуда — йиғинӣ",
            notes="Мисол:\n\nВоридот: `2 3`\nХурӯҷ: `5`"
        )
    ]
    db.add_all(translations1)
    

    test_cases1 = [
        TestCase(problem_id=problem1.id, test_order=1, input_data="2 3\n", expected_output="5\n", is_sample=True),
        TestCase(problem_id=problem1.id, test_order=2, input_data="0 0\n", expected_output="0\n", is_sample=True),
        TestCase(problem_id=problem1.id, test_order=3, input_data="100 100\n", expected_output="200\n", is_sample=False),
        TestCase(problem_id=problem1.id, test_order=4, input_data="50 75\n", expected_output="125\n", is_sample=False),
    ]
    db.add_all(test_cases1)
    

    problem2 = Problem(
        title="Maximum of Two Numbers",
        difficulty="easy",
        time_limit=1.0,
        memory_limit=256,
        is_published=True,
        author_id=author.id,
        category="math"
    )
    db.add(problem2)
    await db.flush()
    
    translations2 = [
        ProblemTranslation(
            problem_id=problem2.id,
            language=Language.RU,
            title="Максимум из двух чисел",
            statement="## Условие\n\nДаны два целых числа. Найдите наибольшее из них.\n\n### Входные данные\n\nДва целых числа (по модулю не превышающие 1000).\n\n### Выходные данные\n\nОдно число — максимум.",
            input_format="Два целых числа",
            output_format="Одно целое число"
        ),
        ProblemTranslation(
            problem_id=problem2.id,
            language=Language.EN,
            title="Maximum of Two Numbers",
            statement="## Problem Statement\n\nGiven two integers. Find the maximum of them.\n\n### Input\n\nTwo integers (absolute value ≤ 1000).\n\n### Output\n\nOne integer — the maximum.",
            input_format="Two integers",
            output_format="One integer"
        ),
        ProblemTranslation(
            problem_id=problem2.id,
            language=Language.TJ,
            title="Калонтарин аз ду адад",
            statement="## Шарт\n\nДу адади бутуншуда дода шудааст. Калонтаринашонро ёбед.\n\n### Додаҳо\n\nДу адади бутуншуда (қимати мутлақ ≤ 1000).\n\n### Баромад\n\nЯк адади бутуншуда — калонтарин.",
            input_format="Ду адади бутуншуда",
            output_format="Як адади бутуншуда"
        )
    ]
    db.add_all(translations2)
    
    test_cases2 = [
        TestCase(problem_id=problem2.id, test_order=1, input_data="5 10\n", expected_output="10\n", is_sample=True),
        TestCase(problem_id=problem2.id, test_order=2, input_data="-5 -10\n", expected_output="-5\n", is_sample=True),
        TestCase(problem_id=problem2.id, test_order=3, input_data="100 100\n", expected_output="100\n", is_sample=False),
    ]
    db.add_all(test_cases2)
    

    problem3 = Problem(
        title="Factorial",
        difficulty="easy",
        time_limit=2.0,
        memory_limit=256,
        is_published=True,
        author_id=author.id,
        category="math"
    )
    db.add(problem3)
    await db.flush()
    
    translations3 = [
        ProblemTranslation(
            problem_id=problem3.id,
            language=Language.RU,
            title="Факториал",
            statement="## Условие\n\nДано неотрицательное целое число N. Вычислите N! (факториал N).\n\nN! = 1 × 2 × 3 × ... × N\n\n### Входные данные\n\nОдно целое число N (0 ≤ N ≤ 20).\n\n### Выходные данные\n\nОдно целое число — N!.",
            input_format="Одно целое число N",
            output_format="Одно целое число — N!",
            notes="0! = 1 по определению"
        ),
        ProblemTranslation(
            problem_id=problem3.id,
            language=Language.EN,
            title="Factorial",
            statement="## Problem Statement\n\nGiven a non-negative integer N. Calculate N! (factorial of N).\n\nN! = 1 × 2 × 3 × ... × N\n\n### Input\n\nOne integer N (0 ≤ N ≤ 20).\n\n### Output\n\nOne integer — N!.",
            input_format="One integer N",
            output_format="One integer — N!",
            notes="0! = 1 by definition"
        ),
        ProblemTranslation(
            problem_id=problem3.id,
            language=Language.TJ,
            title="Факториал",
            statement="## Шарт\n\nАдади бутуншудаи ғайриманфии N дода шудааст. N! (факториали N)-ро ҳисоб кунед.\n\nN! = 1 × 2 × 3 × ... × N\n\n### Додаҳо\n\nЯк адади бутуншудаи N (0 ≤ N ≤ 20).\n\n### Баромад\n\nЯк адади бутуншуда — N!.",
            input_format="Як адади бутуншудаи N",
            output_format="Як адади бутуншуда — N!",
            notes="0! = 1 аз рӯи таъриф"
        )
    ]
    db.add_all(translations3)
    
    test_cases3 = [
        TestCase(problem_id=problem3.id, test_order=1, input_data="0\n", expected_output="1\n", is_sample=True),
        TestCase(problem_id=problem3.id, test_order=2, input_data="1\n", expected_output="1\n", is_sample=True),
        TestCase(problem_id=problem3.id, test_order=3, input_data="5\n", expected_output="120\n", is_sample=False),
        TestCase(problem_id=problem3.id, test_order=4, input_data="10\n", expected_output="3628800\n", is_sample=False),
    ]
    db.add_all(test_cases3)
    

    problem4 = Problem(
        title="Sum of Digits",
        difficulty="easy",
        time_limit=1.0,
        memory_limit=256,
        is_published=True,
        author_id=author.id,
        category="implementation"
    )
    db.add(problem4)
    await db.flush()
    
    translations4 = [
        ProblemTranslation(
            problem_id=problem4.id,
            language=Language.RU,
            title="Сумма цифр числа",
            statement="## Условие\n\nДано натуральное число N. Найдите сумму его цифр.\n\n### Входные данные\n\nОдно натуральное число N (1 ≤ N ≤ 10^9).\n\n### Выходные данные\n\nОдно целое число — сумма цифр числа N.",
            input_format="Одно натуральное число N",
            output_format="Одно целое число"
        ),
        ProblemTranslation(
            problem_id=problem4.id,
            language=Language.EN,
            title="Sum of Digits",
            statement="## Problem Statement\n\nGiven a natural number N. Find the sum of its digits.\n\n### Input\n\nOne natural number N (1 ≤ N ≤ 10^9).\n\n### Output\n\nOne integer — the sum of digits of N.",
            input_format="One natural number N",
            output_format="One integer"
        ),
        ProblemTranslation(
            problem_id=problem4.id,
            language=Language.TJ,
            title="Йиғинии рақамҳо",
            statement="## Шарт\n\nАдади табиии N дода шудааст. Йиғинии рақамҳои онро ёбед.\n\n### Додаҳо\n\nЯк адади табиии N (1 ≤ N ≤ 10^9).\n\n### Баромад\n\nЯк адади бутуншуда — йиғинии рақамҳои N.",
            input_format="Як адади табиии N",
            output_format="Як адади бутуншуда"
        )
    ]
    db.add_all(translations4)
    
    test_cases4 = [
        TestCase(problem_id=problem4.id, test_order=1, input_data="123\n", expected_output="6\n", is_sample=True),
        TestCase(problem_id=problem4.id, test_order=2, input_data="100\n", expected_output="1\n", is_sample=True),
        TestCase(problem_id=problem4.id, test_order=3, input_data="9999\n", expected_output="36\n", is_sample=False),
        TestCase(problem_id=problem4.id, test_order=4, input_data="1000000000\n", expected_output="1\n", is_sample=False),
    ]
    db.add_all(test_cases4)
    

    problem5 = Problem(
        title="Prime Number",
        difficulty="medium",
        time_limit=2.0,
        memory_limit=256,
        is_published=True,
        author_id=author.id,
        category="math"
    )
    db.add(problem5)
    await db.flush()
    
    translations5 = [
        ProblemTranslation(
            problem_id=problem5.id,
            language=Language.RU,
            title="Простое число",
            statement="## Условие\n\nДано натуральное число N. Определите, является ли оно простым.\n\nПростое число — это натуральное число больше 1, которое делится только на 1 и на само себя.\n\n### Входные данные\n\nОдно натуральное число N (1 ≤ N ≤ 10^6).\n\n### Выходные данные\n\nВыведите \"YES\", если число простое, и \"NO\" в противном случае.",
            input_format="Одно натуральное число N",
            output_format="YES или NO",
            notes="1 не является простым числом"
        ),
        ProblemTranslation(
            problem_id=problem5.id,
            language=Language.EN,
            title="Prime Number",
            statement="## Problem Statement\n\nGiven a natural number N. Determine if it is prime.\n\nA prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself.\n\n### Input\n\nOne natural number N (1 ≤ N ≤ 10^6).\n\n### Output\n\nPrint \"YES\" if the number is prime, and \"NO\" otherwise.",
            input_format="One natural number N",
            output_format="YES or NO",
            notes="1 is not a prime number"
        ),
        ProblemTranslation(
            problem_id=problem5.id,
            language=Language.TJ,
            title="Адади сода",
            statement="## Шарт\n\nАдади табиии N дода шудааст. Муайян кунед, ки оё он сода аст ё не.\n\nАдади сода — адади табиии калонтар аз 1, ки танҳо ба 1 ва ба худ тақсим мешавад.\n\n### Додаҳо\n\nЯк адади табиии N (1 ≤ N ≤ 10^6).\n\n### Баромад\n\nАгар адад сода бошад \"YES\" ва дар акси ҳол \"NO\" чоп кунед.",
            input_format="Як адади табиии N",
            output_format="YES ё NO",
            notes="1 адади сода нест"
        )
    ]
    db.add_all(translations5)
    
    test_cases5 = [
        TestCase(problem_id=problem5.id, test_order=1, input_data="2\n", expected_output="YES\n", is_sample=True),
        TestCase(problem_id=problem5.id, test_order=2, input_data="17\n", expected_output="YES\n", is_sample=True),
        TestCase(problem_id=problem5.id, test_order=3, input_data="1\n", expected_output="NO\n", is_sample=False),
        TestCase(problem_id=problem5.id, test_order=4, input_data="4\n", expected_output="NO\n", is_sample=False),
        TestCase(problem_id=problem5.id, test_order=5, input_data="997\n", expected_output="YES\n", is_sample=False),
    ]
    db.add_all(test_cases5)
    
    await db.commit()
    
    return 5
