import subprocess
import sys
import unittest


class TestPgFluxCommands(unittest.TestCase):

    def test_init_command(self):
        """Test the initialization of the pgflux environment."""
        result = subprocess.run(
            [sys.executable, "-m", "pgflux.cli", "init", "--f"],
            capture_output=True, text=True
        )
        self.assertIn("Initializing pgflux environment", result.stdout)

    def test_run_command(self):
        """Test running a sample task in pgflux."""
        result = subprocess.run(
            [sys.executable, "-m", "pgflux.cli", "run", "example_task"],
            capture_output=True, text=True
        )
        self.assertIn("Executed example_task successfully.", result.stdout)

    def test_status_command(self):
        """Test checking the status of the pgflux environment."""
        result = subprocess.run(
            [sys.executable, "-m", "pgflux.cli", "status"],
            capture_output=True, text=True
        )
        self.assertIn("pgflux environment status: OK", result.stdout)

    def test_start_command(self):
        """Test starting the PostgreSQL server."""
        result = subprocess.run(
            [sys.executable, "-m", "pgflux.cli", "start", "--p", "5433"],
            capture_output=True, text=True
        )
        self.assertIn("Starting PostgreSQL", result.stdout)

    def test_stop_command(self):
        """Test stopping the PostgreSQL server."""
        result = subprocess.run(
            [sys.executable, "-m", "pgflux.cli", "stop", "--p", "5433"],
            capture_output=True, text=True
        )
        self.assertIn("Stopping PostgreSQL", result.stdout)

    def test_restart_command(self):
        """Test restarting the PostgreSQL server."""
        result = subprocess.run(
            [sys.executable, "-m", "pgflux.cli", "restart", "--p", "5433"],
            capture_output=True, text=True
        )
        self.assertIn("Restarting PostgreSQL", result.stdout)

    def test_install_command(self):
        """Test installing PostgreSQL."""
        result = subprocess.run(
            [sys.executable, "-m", "pgflux.cli", "install", "pg16", "--p", "5433", "--f"],
            capture_output=True, text=True
        )
        self.assertIn("Installing PostgreSQL", result.stdout)


if __name__ == "__main__":
    unittest.main()
