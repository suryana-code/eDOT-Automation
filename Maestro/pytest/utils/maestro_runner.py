from pathlib import Path
import subprocess


ROOT_DIR = Path(__file__).resolve().parent.parent


def run_maestro(env):
    flow = ROOT_DIR / "flows" / "main.yaml"

    cmd = [
        "maestro",
        "test",
        str(flow),
        "-p",
        "android",
    ]

    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
    )