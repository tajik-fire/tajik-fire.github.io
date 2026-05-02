
from dataclasses import dataclass
from typing import List


@dataclass
class LanguageConfig:
    
    name: str
    extension: str
    compile_cmd: str | None
    run_cmd: str
    time_multiplier: float = 1.0
    memory_multiplier: float = 1.0



LANGUAGES = {
    "python3": LanguageConfig(
        name="Python 3",
        extension=".py",
        compile_cmd=None,
        run_cmd="python3 {source_file}",
        time_multiplier=2.0,
        memory_multiplier=1.5,
    ),
    "cpp17": LanguageConfig(
        name="C++17",
        extension=".cpp",
        compile_cmd="g++ -std=c++17 -O2 -o {executable} {source_file}",
        run_cmd="./{executable}",
        time_multiplier=1.0,
        memory_multiplier=1.0,
    ),
    "java11": LanguageConfig(
        name="Java 11",
        extension=".java",
        compile_cmd="javac {source_file}",
        run_cmd="java -cp {workdir} Main",
        time_multiplier=2.0,
        memory_multiplier=2.0,
    ),
}

SUPPORTED_LANGUAGES = list(LANGUAGES.keys())


def get_language_config(language: str) -> LanguageConfig | None:
    
    return LANGUAGES.get(language)


def is_supported(language: str) -> bool:
    
    return language in SUPPORTED_LANGUAGES
