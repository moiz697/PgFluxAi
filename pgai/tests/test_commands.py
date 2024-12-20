import subprocess
import sys

def test_init_command():
    result = subprocess.run([sys.executable, "-m", "pgai.cli", "init"], capture_output=True, text=True)
    assert "Initializing pgai environment" in result.stdout

def test_run_command():
    result = subprocess.run([sys.executable, "-m", "pgai.cli", "run", "example_task"], capture_output=True, text=True)
    assert "Executed example_task successfully." in result.stdout

def test_status_command():
    result = subprocess.run([sys.executable, "-m", "pgai.cli", "status"], capture_output=True, text=True)
    assert "pgai environment status: OK" in result.stdout
