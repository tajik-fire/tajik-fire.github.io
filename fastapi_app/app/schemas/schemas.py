from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
import re
from app.utils.validators import is_safe_avatar_url
from enum import Enum


class LanguageEnum(str, Enum):
    TJ = "tj"
    RU = "ru"
    EN = "en"


class VerdictEnum(str, Enum):
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    RUNTIME_ERROR = "runtime_error"
    COMPILATION_ERROR = "compilation_error"
    PENDING = "pending"
    JUDGING = "judging"


class ProgrammingLanguageEnum(str, Enum):
    PYTHON3 = "python3"
    CPP17 = "cpp17"
    JAVA11 = "java11"


class UserBase(BaseModel):
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain alphanumeric characters, underscores, and hyphens')
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        return v


class UserCreate(UserBase):
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    login: str
    password: str

class UserResponse(UserBase):
    id: int
    avatar_url: Optional[str] = None
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}
    
    @field_validator('avatar_url')
    @classmethod
    def validate_avatar_url(cls, v):
        if v and not is_safe_avatar_url(v):
            raise ValueError('Invalid or unsafe avatar URL')
        return v

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    receiver_id: Optional[int] = None
    chat_id: Optional[int] = None

class MessageResponse(MessageBase):
    id: int
    sender_id: int
    receiver_id: Optional[int]
    chat_id: Optional[int]
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class ChatBase(BaseModel):
    name: Optional[str] = None
    is_group: bool = False

class ChatCreate(ChatBase):
    member_ids: Optional[List[int]] = None

class ChatResponse(ChatBase):
    id: int
    created_at: datetime
    updated_at: datetime
    members: Optional[List[UserResponse]] = []
    last_message: Optional[MessageResponse] = None
    unread_count: int = 0

    model_config = {"from_attributes": True}

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"

class TaskCreate(TaskBase):
    pass

class TaskResponse(TaskBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProblemTranslationBase(BaseModel):
    language: LanguageEnum
    title: str
    statement: str
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    notes: Optional[str] = None


class ProblemTranslationCreate(ProblemTranslationBase):
    problem_id: int


class ProblemTranslationResponse(ProblemTranslationBase):
    id: int
    problem_id: int

    model_config = {"from_attributes": True}


class TestCaseBase(BaseModel):
    test_order: int
    input_data: str
    expected_output: str
    is_sample: bool = False


class TestCaseCreate(TestCaseBase):
    problem_id: int


class TestCaseResponse(TestCaseBase):
    id: int
    problem_id: int

    model_config = {"from_attributes": True}


class ProblemBase(BaseModel):
    title: str
    difficulty: str = "easy"
    time_limit: float = 1.0
    memory_limit: int = 256
    category: Optional[str] = None


class ProblemCreate(ProblemBase):
    translations: List[ProblemTranslationBase]
    test_cases: List[TestCaseBase]


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
    translations: List[ProblemTranslationResponse] = []
    test_cases: List[TestCaseResponse] = []
    solved_count: int = 0

    model_config = {"from_attributes": True}


class SubmissionBase(BaseModel):
    code: str
    language: ProgrammingLanguageEnum


class SubmissionCreate(SubmissionBase):
    problem_id: int


class SubmissionResponse(SubmissionBase):
    id: int
    user_id: int
    problem_id: int
    verdict: VerdictEnum
    execution_time: Optional[float] = None
    memory_used: Optional[int] = None
    test_passed: int = 0
    test_total: int = 0
    error_message: Optional[str] = None
    created_at: datetime
    judged_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SubmissionFeedEntry(BaseModel):
    id: int
    submission_id: int
    user_id: int
    username: str
    problem_id: int
    problem_title: str
    verdict: VerdictEnum
    execution_time: Optional[float] = None
    memory_used: Optional[int] = None
    language: ProgrammingLanguageEnum
    created_at: datetime

    model_config = {"from_attributes": True}


class ContestProblemBase(BaseModel):
    problem_id: int
    position: int
    points: int = 1


class ContestBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    contest_type: str = "standard"


class ContestCreate(ContestBase):
    problems: List[ContestProblemBase] = []


class ContestResponse(ContestBase):
    id: int
    is_published: bool
    owner_id: Optional[int] = None
    created_at: datetime
    problems: List[ContestProblemBase] = []

    model_config = {"from_attributes": True}


class FriendshipBase(BaseModel):
    user_id: int
    friend_id: int
    status: str = "requested"


class FriendshipResponse(BaseModel):
    id: int
    user_id: int
    friend_id: int
    friend_username: str
    friend_avatar: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NewsBase(BaseModel):
    title: str
    content: str


class NewsCreate(NewsBase):
    pass


class NewsResponse(NewsBase):
    id: int
    author_id: Optional[int] = None
    author_username: Optional[str] = None
    is_published: bool
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class EmailVerifyRequest(BaseModel):
    email: EmailStr
    code: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str
    new_password: str
