# Judger Service - Docker-based Code Execution

## Overview

The judger service securely executes and verifies user-submitted code in isolated Docker containers.

## Supported Languages

- **Python 3** (`python3`) - Python 3.11 with 2x time multiplier
- **C++17** (`cpp17`) - GCC 12 with C++17 standard
- **Java 11** (`java11`) - OpenJDK 11 JRE with 2x time/memory multipliers

## Architecture

```
app/services/judger/
├── __init__.py          # Package initialization
├── languages.py         # Language configurations
├── runner.py            # Docker-based code execution
├── verifiers.py         # Output comparison logic
└── judger.py            # Main judging orchestration
```

## Verdicts

- `ACCEPTED` - All test cases passed
- `WRONG_ANSWER` - Output doesn't match expected
- `TIME_LIMIT_EXCEEDED` - Execution took too long
- `MEMORY_LIMIT_EXCEEDED` - Used too much memory
- `RUNTIME_ERROR` - Program crashed during execution
- `COMPILATION_ERROR` - Code failed to compile
- `PENDING` - Waiting to be judged
- `JUDGING` - Currently being judged

## Resource Limits

| Language | Time Limit | Memory Limit | Network |
|----------|-----------|--------------|---------|
| Python 3 | 2.0x      | 1.5x         | Disabled |
| C++17    | 1.0x      | 1.0x         | Disabled |
| Java 11  | 2.0x      | 2.0x         | Disabled |

Default limits:
- Max CPU time: 10 seconds
- Max wall time: 30 seconds  
- Max memory: 512 MB
- Max output: 64 MB

## Building Docker Images

```bash
cd docker/judger

# Build all images
docker-compose -f docker-compose.judger.yml build

# Build specific language
docker-compose -f docker-compose.judger.yml --profile python build
docker build -f Dockerfile.python -t devstudio-judger-python:latest .
```

## Usage Example

```python
from app.services.judger.judger import JudgerService
from sqlalchemy.ext.asyncio import AsyncSession

async def judge_submission_example(db: AsyncSession, submission_id: int):
    judger = JudgerService(db)
    result = await judger.judge_submission(submission_id)
    
    print(f"Verdict: {result['verdict']}")
    print(f"Tests passed: {result.get('test_passed', 0)}/{result.get('test_total', 0)}")
    print(f"Execution time: {result.get('execution_time', 0):.3f}s")
    print(f"Memory used: {result.get('memory_used', 0)} KB")
```

## Sample Problems

Run the seed script to create sample problems:

```python
from app.data.problems.seed_data import seed_problems

async def setup_demo(db: AsyncSession):
    result = await seed_problems(db)
    print(f"Created {result['problems_created']} problems")
```

Included problems:
1. **A + B** - Basic addition (easy)
2. **Maximum of Three** - Find max of 3 numbers (easy)
3. **Factorial** - Calculate N! (medium)

Each problem has translations in:
- 🇷🇺 Russian (RU)
- 🇬🇧 English (EN)
- 🇹🇯 Tajik (TJ)

## Security Features

- ✅ Network isolation (no internet access)
- ✅ Memory limits enforced by cgroups
- ✅ CPU time limits enforced by cgroups
- ✅ Non-root user execution
- ✅ Temporary directory cleanup
- ✅ Container removal after execution
- ✅ Output size limits

## Testing

```bash
# Run judger tests
pytest tests/test_judger.py -v

# Tests cover:
# - Output verification (whitespace, case sensitivity)
# - Language configuration
# - Format validation
```

## Adding New Languages

1. Add language config in `languages.py`:
```python
LANGUAGES["rust"] = LanguageConfig(
    name="Rust",
    extension=".rs",
    compile_cmd="rustc -O -o {executable} {source_file}",
    run_cmd="./{executable}",
    time_multiplier=1.0,
    memory_multiplier=1.0,
)
```

2. Create Dockerfile in `docker/judger/`
3. Update `_get_image_name()` in `runner.py`

## Troubleshooting

### Docker daemon not running
```bash
sudo systemctl start docker
```

### Permission denied
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Container timeout
Increase `MAX_CPU_TIME` or `MAX_WALL_TIME` in `runner.py`

### Memory limit issues
Check `mem_limit` in container configuration
