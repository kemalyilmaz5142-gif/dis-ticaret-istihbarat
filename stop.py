from __future__ import annotations

import subprocess


PORTS = (3000, 8000)


def main() -> int:
    for port in PORTS:
        command = (
            f"Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue "
            "| Select-Object -ExpandProperty OwningProcess -Unique "
            "| ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", command], check=False)

    print("Proje servisleri kapatildi.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

