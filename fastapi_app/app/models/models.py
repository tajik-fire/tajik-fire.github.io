from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Index, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.db.database import Base
import enum


class Language(str, enum.Enum):
    
    TJ = "tj"
    RU = "ru"
    EN = "en"


class Verdict(str, enum.Enum):
    
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    RUNTIME_ERROR = "runtime_error"
    COMPILATION_ERROR = "compilation_error"
    PENDING = "pending"
    JUDGING = "judging"


class ProgrammingLanguage(str, enum.Enum):
    
    PYTHON3 = "python3"
    CPP17 = "cpp17"
    JAVA11 = "java11"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    avatar_url = Column(String, default="default.svg")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    

    rating = Column(Integer, default=0)
    max_rating = Column(Integer, default=0)
    solved_count = Column(Integer, default=0)
    attempt_count = Column(Integer, default=0)
    

    messages_sent = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", overlaps="sent_messages")
    messages_received = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver", overlaps="received_messages")
    tasks = relationship("Task", back_populates="owner")
    chats = relationship("ChatMember", back_populates="user")
    

    submissions = relationship("Submission", back_populates="user", cascade="all, delete-orphan")
    solved_problems = relationship("ProblemSolve", back_populates="user", cascade="all, delete-orphan")
    contest_participations = relationship("ContestParticipation", back_populates="user", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
    friendships_as_user1 = relationship("Friendship", foreign_keys="Friendship.user1_id", back_populates="user1", cascade="all, delete-orphan")
    friendships_as_user2 = relationship("Friendship", foreign_keys="Friendship.user2_id", back_populates="user2", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    blocked_users_blocking = relationship("BlockedUser", foreign_keys="BlockedUser.blocker_id", back_populates="blocker", cascade="all, delete-orphan")
    blocked_users_blocked = relationship("BlockedUser", foreign_keys="BlockedUser.blocked_id", back_populates="blocked", cascade="all, delete-orphan")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender", overlaps="messages_sent")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver", overlaps="messages_received")
    enrollments = relationship("LearningEnrollment", back_populates="user", cascade="all, delete-orphan")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    is_group = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    members = relationship("ChatMember", back_populates="chat", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")


class ChatMember(Base):
    __tablename__ = "chat_members"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    chat = relationship("Chat", back_populates="members")
    user = relationship("User", back_populates="chats")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    file_url = Column(String, nullable=True)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="messages_received")
    chat = relationship("Chat", back_populates="messages")

    __table_args__ = (
        Index('ix_messages_chat_created', 'chat_id', 'created_at'),
    )


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="todo")
    priority = Column(String, default="medium")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="tasks")

    __table_args__ = (
        Index('ix_tasks_owner_status', 'owner_id', 'status'),
    )






class Problem(Base):
    
    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    difficulty = Column(String(32), default="easy")
    time_limit = Column(Float, default=1.0)
    memory_limit = Column(Integer, default=256)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    category = Column(String(64), nullable=True)
    

    author = relationship("User", backref="authored_problems")
    test_cases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan", order_by="TestCase.test_order")
    translations = relationship("ProblemTranslation", back_populates="problem", cascade="all, delete-orphan")
    submissions = relationship("Submission", back_populates="problem", cascade="all, delete-orphan")
    solves = relationship("ProblemSolve", back_populates="problem", cascade="all, delete-orphan")
    contest_problems = relationship("ContestProblem", back_populates="problem", cascade="all, delete-orphan")
    learning_problems = relationship("LearningProblem", back_populates="problem", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_problems_difficulty', 'difficulty'),
        Index('ix_problems_published', 'is_published'),
        Index('ix_problems_category', 'category'),
    )


class ProblemTranslation(Base):
    
    __tablename__ = "problem_translations"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    language = Column(SQLEnum(Language), nullable=False)
    title = Column(String(256), nullable=False)
    statement = Column(Text, nullable=False)
    input_format = Column(Text, nullable=True)
    output_format = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    problem = relationship("Problem", back_populates="translations")

    __table_args__ = (
        Index('ix_problem_translations_unique', 'problem_id', 'language', unique=True),
    )


class TestCase(Base):
    
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    test_order = Column(Integer, nullable=False)
    input_data = Column(Text, nullable=False)
    expected_output = Column(Text, nullable=False)
    is_sample = Column(Boolean, default=False)
    time_limit_override = Column(Float, nullable=True)
    memory_limit_override = Column(Integer, nullable=True)
    
    problem = relationship("Problem", back_populates="test_cases")

    __table_args__ = (
        Index('ix_test_cases_problem_order', 'problem_id', 'test_order'),
    )


class Submission(Base):
    
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    code = Column(Text, nullable=False)
    language = Column(SQLEnum(ProgrammingLanguage), nullable=False)
    verdict = Column(SQLEnum(Verdict), default=Verdict.PENDING)
    execution_time = Column(Float, nullable=True)
    memory_used = Column(Integer, nullable=True)
    test_passed = Column(Integer, default=0)
    test_total = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    judged_at = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="submissions")
    problem = relationship("Problem", back_populates="submissions")
    feed_entries = relationship("SubmissionFeed", back_populates="submission", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_submissions_user', 'user_id'),
        Index('ix_submissions_problem', 'problem_id'),
        Index('ix_submissions_created', 'created_at'),
        Index('ix_submissions_verdict', 'verdict'),
    )


class ProblemSolve(Base):
    
    __tablename__ = "problem_solves"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=True)
    solved_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    attempts_before_solve = Column(Integer, default=0)
    
    user = relationship("User", back_populates="solved_problems")
    problem = relationship("Problem", back_populates="solves")
    submission = relationship("Submission")

    __table_args__ = (
        Index('ix_problem_solves_unique', 'user_id', 'problem_id', unique=True),
    )


class Contest(Base):
    
    __tablename__ = "contests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    is_published = Column(Boolean, default=False)
    contest_type = Column(String(32), default="standard")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    owner = relationship("User", backref="owned_contests")
    problems = relationship("ContestProblem", back_populates="contest", cascade="all, delete-orphan", order_by="ContestProblem.position")
    participations = relationship("ContestParticipation", back_populates="contest", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_contests_start_time', 'start_time'),
        Index('ix_contests_published', 'is_published'),
    )


class ContestProblem(Base):
    
    __tablename__ = "contest_problems"

    id = Column(Integer, primary_key=True, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    position = Column(Integer, nullable=False)
    points = Column(Integer, default=1)
    
    contest = relationship("Contest", back_populates="problems")
    problem = relationship("Problem", back_populates="contest_problems")

    __table_args__ = (
        Index('ix_contest_problems_unique', 'contest_id', 'problem_id', unique=True),
        Index('ix_contest_problems_position', 'contest_id', 'position'),
    )


class ContestParticipation(Base):
    
    __tablename__ = "contest_participations"

    id = Column(Integer, primary_key=True, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_time = Column(DateTime, nullable=True)
    finish_time = Column(DateTime, nullable=True)
    score = Column(Integer, default=0)
    penalty = Column(Integer, default=0)
    rank = Column(Integer, nullable=True)
    
    contest = relationship("Contest", back_populates="participations")
    user = relationship("User", back_populates="contest_participations")

    __table_args__ = (
        Index('ix_contest_participations_unique', 'contest_id', 'user_id', unique=True),
        Index('ix_contest_participations_score', 'contest_id', 'score'),
    )


class Rating(Base):
    
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=True)
    changed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    comment = Column(String(256), nullable=True)
    
    user = relationship("User", back_populates="ratings")
    contest = relationship("Contest")

    __table_args__ = (
        Index('ix_ratings_user_changed', 'user_id', 'changed_at'),
    )


class Friendship(Base):
    
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(32), default="requested")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="friendships_as_user1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="friendships_as_user2")

    __table_args__ = (
        Index('ix_friendships_unique', 'user1_id', 'user2_id', unique=True),
        Index('ix_friendships_status', 'status'),
    )


class Notification(Base):
    
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(256), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(64), default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="notifications")

    __table_args__ = (
        Index('ix_notifications_user_read', 'user_id', 'is_read'),
    )


class BlockedUser(Base):
    
    __tablename__ = "blocked_users"

    id = Column(Integer, primary_key=True, index=True)
    blocker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blocked_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blocked_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    blocker = relationship("User", foreign_keys=[blocker_id], back_populates="blocked_users_blocking")
    blocked = relationship("User", foreign_keys=[blocked_id], back_populates="blocked_users_blocked")

    __table_args__ = (
        Index('ix_blocked_users_unique', 'blocker_id', 'blocked_id', unique=True),
    )


class SubmissionFeed(Base):
    
    __tablename__ = "submission_feed"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    verdict = Column(SQLEnum(Verdict), nullable=False)
    execution_time = Column(Float, nullable=True)
    memory_used = Column(Integer, nullable=True)
    language = Column(SQLEnum(ProgrammingLanguage), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    submission = relationship("Submission", back_populates="feed_entries")
    user = relationship("User")
    problem = relationship("Problem")

    __table_args__ = (
        Index('ix_submission_feed_created', 'created_at'),
        Index('ix_submission_feed_verdict', 'verdict'),
    )






class LearningModule(Base):
    
    __tablename__ = "learning_modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    slug = Column(String(128), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    theory_content = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    problems = relationship("LearningProblem", back_populates="module", cascade="all, delete-orphan", order_by="LearningProblem.order")
    enrollments = relationship("LearningEnrollment", back_populates="module", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_learning_modules_slug', 'slug'),
        Index('ix_learning_modules_order', 'order'),
    )


class LearningProblem(Base):
    
    __tablename__ = "learning_problems"

    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=False)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    order = Column(Integer, nullable=False)
    
    module = relationship("LearningModule", back_populates="problems")
    problem = relationship("Problem", back_populates="learning_problems")

    __table_args__ = (
        Index('ix_learning_problems_module_order', 'module_id', 'order'),
    )


class LearningEnrollment(Base):
    
    __tablename__ = "learning_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("learning_modules.id"), nullable=False)
    enrolled_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime, nullable=True)
    progress = Column(Integer, default=0)
    
    user = relationship("User", back_populates="enrollments")
    module = relationship("LearningModule", back_populates="enrollments")

    __table_args__ = (
        Index('ix_learning_enrollments_unique', 'user_id', 'module_id', unique=True),
    )






class EmailCode(Base):
    
    __tablename__ = "email_codes"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    code = Column(String(6), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class LoginAttempt(Base):
    
    __tablename__ = "login_attempts"

    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    email = Column(String, nullable=True, index=True)
    success = Column(Boolean, default=False)
    attempted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class AuthToken(Base):
    
    __tablename__ = "auth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    token_type = Column(String(32), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    revoked = Column(Boolean, default=False)
    
    user = relationship("User")


class TempUser(Base):
    
    __tablename__ = "temp_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    verification_code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))






class News(Base):
    
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    author = relationship("User")

    __table_args__ = (
        Index('ix_news_published', 'is_published'),
        Index('ix_news_published_at', 'published_at'),
    )
