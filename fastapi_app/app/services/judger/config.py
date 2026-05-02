import enum


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


LANGUAGE_CONFIG = {
    ProgrammingLanguage.PYTHON3: {
        "image": "python:3.11-slim",
        "compile_cmd": None,
        "run_cmd": "python3 /app/solution.py",
        "file_ext": ".py",
        "memory_overhead": 50,
    },
    ProgrammingLanguage.CPP17: {
        "image": "gcc:12-slim",
        "compile_cmd": "g++ -std=c++17 -O2 -o /app/solution /app/solution.cpp",
        "run_cmd": "/app/solution",
        "file_ext": ".cpp",
        "memory_overhead": 20,
    },
    ProgrammingLanguage.JAVA11: {
        "image": "eclipse-temurin:11-jre-alpine",
        "compile_cmd": "javac -d /app /app/Solution.java",
        "run_cmd": "java -cp /app Solution",
        "file_ext": ".java",
        "memory_overhead": 100,
        "class_name": "Solution",
    },
}
