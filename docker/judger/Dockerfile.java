# Dockerfile for Java 11 judger environment
FROM openjdk:11-jre-slim

WORKDIR /judge

RUN useradd -m -u 1000 judgeuser
USER judgeuser

CMD ["/bin/bash"]
