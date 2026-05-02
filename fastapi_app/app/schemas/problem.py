from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class LanguageEnum(str, Enum):
    TJ = "tj"
    RU = "ru"
    EN = "en"


class ProblemTranslationBase(BaseModel):
    language: LanguageEnum
    title: str
    statement: str
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    notes: Optional[str] = None


class TestCaseBase(BaseModel):
    test_order: int
    input_data: str
    expected_output: str
    is_sample: bool = False


class ProblemBase(BaseModel):
    title: str
    difficulty: str = "easy"
    time_limit: float = 1.0
    memory_limit: int = 256
    category: Optional[str] = None


class ProblemCreate(ProblemBase):
    translations: List[ProblemTranslationBase] = []
    test_cases: List[TestCaseBase] = []
    is_published: bool = False


class ProblemUpdate(BaseModel):
    title: Optional[str] = None
    difficulty: Optional[str] = None
    time_limit: Optional[float] = None
    memory_limit: Optional[int] = None
    category: Optional[str] = None
    is_published: Optional[bool] = None


class ProblemResponse(ProblemBase):
    id: int
    is_published: bool
    author_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    translations: List[ProblemTranslationBase] = []
    test_cases: List[TestCaseBase] = []

    model_config = {"from_attributes": True}


class ContestProblemBase(BaseModel):
    problem_id: int
    position: Optional[int] = None
    points: Optional[int] = 1


class ContestProblemCreate(BaseModel):
    problem_id: int
    points: Optional[int] = 1


class ContestBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    contest_type: str = "standard"


class ContestCreate(ContestBase):
    problem_ids: List[int] = []
    is_published: bool = False


class ContestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    contest_type: Optional[str] = None
    is_published: Optional[bool] = None


class ContestResponse(ContestBase):
    id: int
    is_published: bool
    owner_id: Optional[int] = None
    created_at: datetime
    problems: List[ContestProblemBase] = []

    model_config = {"from_attributes": True}
