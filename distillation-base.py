import modal
import os
import subprocess
import time

cuda_version = "12.4.0"
flavor = "devel"
operating_sys = "ubuntu22.04"
tag = f"{cuda_version}-{flavor}-{operating_sys}"

MODEL = os.environ.get("MODEL", "qwen3:235b-a22b")

# Function to initialize and pull the model
def pull_model(model: str = MODEL):
    subprocess.run(["systemctl", "daemon-reload"], check=True)
    subprocess.run(["systemctl", "enable", "ollama"], check=True)
    subprocess.run(["systemctl", "start", "ollama"], check=True)
    time.sleep(2)  # Wait for the service to start
    subprocess.run(["ollama", "pull", model], stdout=subprocess.PIPE, check=True)

# Define the Modal image with dependencies and setup
ollama_image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("curl", "systemctl")
    .run_commands(
        "curl -L https://github.com/ollama/ollama/releases/download/v0.9.3/ollama-linux-amd64.tgz -o ollama-linux-amd64.tgz",
        "tar -C /usr -xzf ollama-linux-amd64.tgz",
        "useradd -r -s /bin/false -U -m -d /usr/share/ollama ollama",
        "usermod -a -G ollama $(whoami)",
    )
    .add_local_file("ollama.service", "/etc/systemd/system/ollama.service", copy=True)
    .pip_install("ollama==0.1.0", "fastapi[standard]")
    .run_function(pull_model, force_build=True)
)

app = modal.App(name="distill", image=ollama_image)

with ollama_image.imports():
    import ollama

MINUTES = 60

@app.cls(
    gpu="B200",
    scaledown_window=5 * MINUTES,
    timeout=60 * MINUTES,
    volumes={
        "/cache": modal.Volume.from_name("hf-hub-cache", create_if_missing=True),
    },
)
class Ollama:
    @modal.enter()
    def enter(self):
        subprocess.run(["systemctl", "start", "ollama"], check=True)

    @modal.method()
    def infer(self, messages: list) -> str:
        response = ollama.chat(model=MODEL, messages=messages, stream=False)
        return response["message"]["content"]

@app.function()
@modal.fastapi_endpoint(method="POST")
def main(request: dict):
    messages = request.get("messages", [])
    response = Ollama().infer.remote(messages)
    return {"choices": [{"role": "assistant", "content": response}]}
