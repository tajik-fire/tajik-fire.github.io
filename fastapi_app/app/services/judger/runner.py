import docker
import time
import tempfile
import os
from typing import Optional, Tuple
from app.services.judger.languages import get_language_config


class DockerRunner:
    def __init__(self):
        self.client = docker.from_env()

    async def run(
        self,
        code: str,
        language: str,
        input_data: str,
        time_limit: float,
        memory_limit: int
    ) -> Tuple[Optional[str], Optional[str], float, int, Optional[str]]:
        config = get_language_config(language)
        
        if not config:
            return None, None, 0, 0, f"Unsupported language: {language}"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            if language == "java11":
                filename = "Main.java"
            else:
                filename = f"solution{config.extension}"
            
            code_path = os.path.join(temp_dir, filename)
            with open(code_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            container = None
            try:
                image_map = {
                    "python3": "python:3.11-slim",
                    "cpp17": "gcc:12-slim",
                    "java11": "eclipse-temurin:11-jre-alpine"
                }
                
                container = self.client.containers.run(
                    image_map.get(language, "python:3.11-slim"),
                    command="sleep 3600",
                    detach=True,
                    remove=False,
                    mem_limit=f"{memory_limit}m",
                    nano_cpus=int(time_limit * 1e9),
                    network_disabled=True,
                )
                
                with open(code_path, "rb") as f:
                    container.put_archive("/tmp", f.read())
                
                if config.compile_cmd:
                    compile_cmd = config.compile_cmd.format(
                        source_file=f"/tmp/{filename}",
                        executable="/tmp/solution"
                    )
                    compile_result = container.exec_run(compile_cmd)
                    
                    if compile_result.exit_code != 0:
                        error_msg = compile_result.output.decode("utf-8", errors="ignore")
                        return None, None, 0, 0, f"Compilation Error: {error_msg}"
                
                start_time = time.time()
                
                if language == "java11":
                    run_cmd = "java -cp /tmp Main"
                elif config.compile_cmd:
                    run_cmd = "/tmp/solution"
                else:
                    run_cmd = f"python3 /tmp/{filename}"
                
                exec_result = container.exec_run(
                    run_cmd,
                    stdin=True,
                    socket=True,
                    workdir="/tmp"
                )
                
                sock = exec_result.output
                sock.sendall(input_data.encode("utf-8"))
                sock.shutdown()
                
                stdout = b""
                
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    stdout += chunk
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                if execution_time > time_limit:
                    return None, None, time_limit, 0, "Time Limit Exceeded"
                
                stats = container.stats(stream=False)
                memory_used = stats["memory_stats"]["usage"] / (1024 * 1024)
                
                if memory_used > memory_limit:
                    return None, None, execution_time, int(memory_used), "Memory Limit Exceeded"
                
                container.stop()
                
                output_str = stdout.decode("utf-8", errors="ignore").strip()
                
                return output_str, None, execution_time, int(memory_used), None
                
            except Exception as e:
                return None, None, 0, 0, f"Runtime Error: {str(e)}"
            finally:
                if container:
                    try:
                        container.remove(force=True)
                    except:
                        pass


def get_runner():
    return DockerRunner()
