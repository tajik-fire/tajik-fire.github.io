# Dockerfile for C++17 (GCC 12) judger environment
FROM gcc:12

WORKDIR /judge

RUN useradd -m -u 1000 judgeuser
USER judgeuser

CMD ["/bin/bash"]
