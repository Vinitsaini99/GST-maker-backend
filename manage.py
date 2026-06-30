#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path


# def _ensure_venv():
#     """Re-launch with project venv Python when available."""
#     base_dir = Path(__file__).resolve().parent
#     venv_python = (
#         base_dir / '.venv' / 'Scripts' / 'python.exe'
#         if os.name == 'nt'
#         else base_dir / '.venv' / 'bin' / 'python'
#     )
#     if not venv_python.is_file():
#         return
#     try:
#         if Path(sys.executable).resolve() == venv_python.resolve():
#             return
#     except OSError:
#         return

#     import subprocess

#     completed = subprocess.run([str(venv_python), *sys.argv], check=False)
#     sys.exit(completed.returncode)


def main():
    """Run administrative tasks."""
    # _ensure_venv()
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
