import modal
import os
import subprocess
import time

from modal import build, enter, method

MODEL = os.environ.get("MODEL", "haghiri/hormoz-8b:iq_nl4")


def pull(model: str = MODEL):
    subprocess.run(["systemctl", "daemon-reload"])
    subprocess.run(["systemctl", "enable", "ollama"])
    subprocess.run(["systemctl", "start", "ollama"])
    time.sleep(2)  # 2s, wait for the service to start
    subprocess.run(["ollama", "pull", model], stdout=subprocess.PIPE)


image = (
    modal.Image.debian_slim()
    .apt_install("curl", "systemctl")
    .run_commands(  # from https://github.com/ollama/ollama/blob/main/docs/linux.md
        "curl -L https://ollama.com/download/ollama-linux-amd64.tgz -o ollama-linux-amd64.tgz",
        "tar -C /usr -xzf ollama-linux-amd64.tgz",
        "useradd -r -s /bin/false -U -m -d /usr/share/ollama ollama",
        "usermod -a -G ollama $(whoami)",
    )
    .copy_local_file("ollama.service", "/etc/systemd/system/ollama.service")
    .pip_install("ollama", "fastapi[standard]")
    .run_function(pull)
)

app = modal.App(name="ollama", image=image)

with image.imports():
    import ollama


@app.cls(gpu="h100", container_idle_timeout=300)
class Ollama:
    @build()
    def pull(self):
        # TODO(irfansharif): Was hoping that the following would use an image
        # with this explicit @build() step's results, but alas, it doesn't - so
        # we're baking it directly into the base image above. Also, would be
        # nice to simply specify the class name? Not like the method is
        # specified has any relevance.
        #
        #  $ modal shell ollama-modal.py::Ollama.infer

        pull(model=MODEL)
        

    @enter()
    def load(self):
        subprocess.run(["systemctl", "start", "ollama"])

    @method()
    def infer(self, messages: list, verbose: bool = False):
        stream = ollama.chat(
            model=MODEL, messages=messages, stream=False
        )
        return stream['message']['content']


# Convenience thing, to run using:
#
#  $ modal run ollama-modal.py [--lookup] [--text "Why is the sky blue?"]
# @app.local_entrypoint()
@app.function()
@modal.web_endpoint(method="POST")
def main(request: dict, text: str = "Why is the sky blue?", lookup: bool = False):
    if lookup:
        ollama = modal.Cls.lookup("ollama", "Ollama")
    else:
        ollama = Ollama()
    res = ollama.infer.remote(request['messages'])
    return {"choices" : [{"role" : "assistant", "content" : res}]}