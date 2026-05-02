
import asyncio
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import (
    Submission, Problem, TestCase, ProblemSolve, SubmissionFeed,
    Verdict, ProgrammingLanguage
)
from .runner import get_runner
from .verifiers import Verifier
from .languages import get_language_config


class JudgerService:
    
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.runner = get_runner()
    
    async def judge_submission(self, submission_id: int) -> Dict[str, Any]:
        

        result = await self.db.execute(
            select(Submission).where(Submission.id == submission_id)
        )
        submission = result.scalar_one_or_none()
        
        if not submission:
            return {"error": "Submission not found"}
        

        problem_result = await self.db.execute(
            select(Problem)
            .where(Problem.id == submission.problem_id)
        )
        problem = problem_result.scalar_one_or_none()
        
        if not problem:
            return {"error": "Problem not found"}
        

        submission.verdict = Verdict.JUDGING
        await self.db.commit()
        

        lang_config = get_language_config(submission.language)
        if not lang_config:
            submission.verdict = Verdict.COMPILATION_ERROR
            submission.error_message = f"Unsupported language: {submission.language}"
            submission.judged_at = datetime.now(timezone.utc)
            await self.db.commit()
            return {"verdict": "compilation_error", "error": "Unsupported language"}
        

        test_cases_result = await self.db.execute(
            select(TestCase)
            .where(TestCase.problem_id == problem.id)
            .order_by(TestCase.test_order)
        )
        test_cases = test_cases_result.scalars().all()
        
        if not test_cases:
            submission.verdict = Verdict.RUNTIME_ERROR
            submission.error_message = "No test cases found"
            submission.judged_at = datetime.now(timezone.utc)
            await self.db.commit()
            return {"verdict": "runtime_error", "error": "No test cases"}
        

        total_tests = len(test_cases)
        passed_tests = 0
        max_execution_time = 0.0
        max_memory_used = 0
        
        for i, test_case in enumerate(test_cases):

            stdout, stderr, exec_time, memory_used, error = await self.runner.run(
                code=submission.code,
                language=submission.language,
                input_data=test_case.input_data,
                time_limit=problem.time_limit,
                memory_limit=problem.memory_limit,
            )
            

            max_execution_time = max(max_execution_time, exec_time)
            max_memory_used = max(max_memory_used, memory_used)
            

            if error:
                if "Compilation" in error:
                    submission.verdict = Verdict.COMPILATION_ERROR
                    submission.error_message = error
                    submission.judged_at = datetime.now(timezone.utc)
                    await self.db.commit()
                    return {
                        "verdict": "compilation_error",
                        "error": error,
                        "test_passed": 0,
                        "test_total": total_tests,
                    }
                elif "Time Limit" in error:
                    submission.verdict = Verdict.TIME_LIMIT_EXCEEDED
                    submission.error_message = f"TLE on test {i + 1}"
                    submission.execution_time = max_execution_time
                    submission.memory_used = max_memory_used
                    submission.test_passed = passed_tests
                    submission.test_total = total_tests
                    submission.judged_at = datetime.now(timezone.utc)
                    await self.db.commit()
                    return {
                        "verdict": "time_limit_exceeded",
                        "test_passed": passed_tests,
                        "test_total": total_tests,
                        "execution_time": max_execution_time,
                        "memory_used": max_memory_used,
                    }
                elif "Memory" in error or "MLE" in error:
                    submission.verdict = Verdict.MEMORY_LIMIT_EXCEEDED
                    submission.error_message = f"MLE on test {i + 1}"
                    submission.execution_time = max_execution_time
                    submission.memory_used = max_memory_used
                    submission.test_passed = passed_tests
                    submission.test_total = total_tests
                    submission.judged_at = datetime.now(timezone.utc)
                    await self.db.commit()
                    return {
                        "verdict": "memory_limit_exceeded",
                        "test_passed": passed_tests,
                        "test_total": total_tests,
                        "execution_time": max_execution_time,
                        "memory_used": max_memory_used,
                    }
                else:
                    submission.verdict = Verdict.RUNTIME_ERROR
                    submission.error_message = f"{error} on test {i + 1}"
                    submission.execution_time = max_execution_time
                    submission.memory_used = max_memory_used
                    submission.test_passed = passed_tests
                    submission.test_total = total_tests
                    submission.judged_at = datetime.now(timezone.utc)
                    await self.db.commit()
                    return {
                        "verdict": "runtime_error",
                        "error": error,
                        "test_passed": passed_tests,
                        "test_total": total_tests,
                        "execution_time": max_execution_time,
                        "memory_used": max_memory_used,
                    }
            

            is_correct, verify_error = Verifier.compare_outputs(
                stdout,
                test_case.expected_output
            )
            
            if is_correct:
                passed_tests += 1
            else:
                submission.verdict = Verdict.WRONG_ANSWER
                submission.error_message = f"WA on test {i + 1}: {verify_error}"
                submission.execution_time = max_execution_time
                submission.memory_used = max_memory_used
                submission.test_passed = passed_tests
                submission.test_total = total_tests
                submission.judged_at = datetime.now(timezone.utc)
                await self.db.commit()
                return {
                    "verdict": "wrong_answer",
                    "error": verify_error,
                    "test_passed": passed_tests,
                    "test_total": total_tests,
                    "execution_time": max_execution_time,
                    "memory_used": max_memory_used,
                }
        

        submission.verdict = Verdict.ACCEPTED
        submission.execution_time = max_execution_time
        submission.memory_used = max_memory_used
        submission.test_passed = total_tests
        submission.test_total = total_tests
        submission.judged_at = datetime.now(timezone.utc)
        

        existing_solve = await self.db.execute(
            select(ProblemSolve).where(
                ProblemSolve.user_id == submission.user_id,
                ProblemSolve.problem_id == submission.problem_id
            )
        )
        
        if not existing_solve.scalar_one_or_none():

            solve = ProblemSolve(
                user_id=submission.user_id,
                problem_id=submission.problem_id,
                submission_id=submission.id,
                attempts_before_solve=submission.test_total - passed_tests,
            )
            self.db.add(solve)
            

            from app.models.models import User
            user_result = await self.db.execute(
                select(User).where(User.id == submission.user_id)
            )
            user = user_result.scalar_one()
            user.solved_count += 1
        
        await self.db.commit()
        

        feed_entry = SubmissionFeed(
            submission_id=submission.id,
            user_id=submission.user_id,
            problem_id=submission.problem_id,
            verdict=submission.verdict,
            execution_time=submission.execution_time,
            memory_used=submission.memory_used,
            language=submission.language,
        )
        self.db.add(feed_entry)
        await self.db.commit()
        
        return {
            "verdict": "accepted",
            "test_passed": total_tests,
            "test_total": total_tests,
            "execution_time": max_execution_time,
            "memory_used": max_memory_used,
        }
    
    async def rejudge_problem(self, problem_id: int) -> Dict[str, Any]:
        
        result = await self.db.execute(
            select(Submission)
            .where(Submission.problem_id == problem_id)
            .order_by(Submission.created_at)
        )
        submissions = result.scalars().all()
        
        results = []
        for submission in submissions:
            result = await self.judge_submission(submission.id)
            results.append({
                "submission_id": submission.id,
                "result": result,
            })
        
        return {
            "total": len(results),
            "results": results,
        }


async def process_submission(submission_id: int, db_session: AsyncSession):
    
    judger = JudgerService(db_session)
    return await judger.judge_submission(submission_id)
