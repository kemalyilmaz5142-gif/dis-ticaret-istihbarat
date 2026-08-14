from __future__ import annotations

import os
import socket
import shutil
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "apps" / "backend"
FRONTEND = ROOT / "apps" / "frontend"
CODEX_RUNTIME = Path.home() / ".cache" / "codex-runtimes" / "codex-primary-runtime" / "dependencies"
CODEX_NODE = CODEX_RUNTIME / "node" / "bin" / "node.exe"
CODEX_NPM = CODEX_RUNTIME / "node" / "bin" / "npm.cmd"
CODEX_PNPM = CODEX_RUNTIME / "bin" / "pnpm.cmd"
CODEX_PNPM_FALLBACK = CODEX_RUNTIME / "bin" / "fallback" / "pnpm.cmd"
CODEX_PNPM_OVERRIDE = CODEX_RUNTIME / "bin" / "override" / "pnpm.cmd"
BACKEND_ENV = BACKEND / ".env"
BACKEND_ENV_EXAMPLE = BACKEND / ".env.example"
BACKEND_VENV = BACKEND / ".venv"
BACKEND_PYTHON = BACKEND_VENV / "Scripts" / "python.exe"


def print_step(message: str) -> None:
    print(f"\n==> {message}", flush=True)


def run(command: list[str], cwd: Path) -> None:
    subprocess.check_call(command, cwd=str(cwd))


def find_command(*names: str) -> str | None:
    for name in names:
        path = Path(name)
        if path.exists():
            return str(path)
        found = shutil.which(name)
        if found:
            return found
    return None


def ensure_backend_env() -> None:
    if BACKEND_ENV.exists() or not BACKEND_ENV_EXAMPLE.exists():
        return
    shutil.copyfile(BACKEND_ENV_EXAMPLE, BACKEND_ENV)


def ensure_backend() -> Path:
    ensure_backend_env()

    if not BACKEND_PYTHON.exists():
        print_step("Backend icin Python ortami hazirlaniyor")
        run([sys.executable, "-m", "venv", str(BACKEND_VENV)], ROOT)

    print_step("Backend paketleri kontrol ediliyor")
    run([str(BACKEND_PYTHON), "-m", "pip", "install", "-r", "requirements.txt"], BACKEND)
    return BACKEND_PYTHON


def ensure_frontend(frontend_port: int) -> tuple[str, list[str]]:
    node = find_command(str(CODEX_NODE), "node.exe", "node")
    npm = find_command(str(CODEX_NPM), "npm.cmd", "npm")
    pnpm = find_command(str(CODEX_PNPM), str(CODEX_PNPM_FALLBACK), str(CODEX_PNPM_OVERRIDE), "pnpm.cmd", "pnpm")
    local_next = FRONTEND / "node_modules" / "next" / "dist" / "bin" / "next"

    if pnpm:
        package_manager = pnpm
        install_command = [package_manager, "install", "--ignore-scripts"]
        dev_command = [package_manager, "dev", "--hostname", "127.0.0.1", "--port", str(frontend_port)]
    elif npm:
        package_manager = npm
        install_command = [package_manager, "install", "--ignore-scripts"]
        dev_command = [package_manager, "run", "dev", "--", "--hostname", "127.0.0.1", "--port", str(frontend_port)]
    elif node and local_next.exists():
        package_manager = "local-next"
        install_command = []
        dev_command = [node, str(local_next), "dev", "--hostname", "127.0.0.1", "--port", str(frontend_port)]
    else:
        raise RuntimeError("Node.js veya paket yoneticisi bulunamadi. Node.js kurulu olmali.")

    if not (FRONTEND / "node_modules").exists():
        if not install_command:
            raise RuntimeError("Frontend paketleri eksik ve paket yoneticisi bulunamadi.")
        print_step("Frontend paketleri kuruluyor")
        run(install_command, FRONTEND)

    return package_manager, dev_command


def find_free_port(start: int, end: int) -> int:
    for port in range(start, end + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError(f"{start}-{end} araliginda bos port bulunamadi.")


def start_process(command: list[str], cwd: Path, name: str) -> subprocess.Popen:
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    if CODEX_NODE.exists():
        node_bin = str(CODEX_NODE.parent)
        extra_bins = [
            node_bin,
            str(CODEX_RUNTIME / "bin" / "fallback"),
            str(CODEX_RUNTIME / "bin" / "override"),
            str(CODEX_RUNTIME / "bin"),
        ]
        env["PATH"] = f"{os.pathsep.join(extra_bins)}{os.pathsep}{env.get('PATH', '')}"
    print_step(f"{name} baslatiliyor")
    return subprocess.Popen(command, cwd=str(cwd), env=env)


def main() -> int:
    print("Dis Ticaret Istihbarat Platformu baslatiliyor...")

    backend_python = ensure_backend()
    frontend_port = find_free_port(3000, 3099)
    _, frontend_dev_command = ensure_frontend(frontend_port)

    backend_process = start_process(
        [str(backend_python), "-m", "uvicorn", "app.main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"],
        BACKEND,
        "Backend",
    )
    frontend_process = start_process(frontend_dev_command, FRONTEND, "Frontend")

    time.sleep(4)
    frontend_url = f"http://localhost:{frontend_port}"
    webbrowser.open(frontend_url)

    print("\nProje acildi:")
    print(f"Frontend: {frontend_url}")
    print("Backend:  http://localhost:8000/api/health")
    print("\nKapatmak icin bu pencerede Ctrl+C yapin.")

    try:
        while True:
            if backend_process.poll() is not None:
                print("Backend durdu.")
                return backend_process.returncode or 1
            if frontend_process.poll() is not None:
                print("Frontend durdu.")
                return frontend_process.returncode or 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProje kapatiliyor...")
        backend_process.terminate()
        frontend_process.terminate()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
