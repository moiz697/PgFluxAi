import click
import subprocess
import os

CONFIG_FILE = "/usr/local/pgflux_installed_version.txt"
INSTALL_PREFIX_TEMPLATE = "/usr/local/{version}"
DATA_DIR_TEMPLATE = "{install_prefix}/data"
PG_CTL_TEMPLATE = "{install_prefix}/bin/pg_ctl"


def detect_installed_version():
    """
    Reads the installed PostgreSQL version from the configuration file.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return file.read().strip()
    return None


@click.command(help="Stop the PostgreSQL server.")
@click.option("--p", "port", default=None, help="Port on which PostgreSQL is running (optional).")
def stop_cli(port):
    """
    Stops the PostgreSQL server. Optionally ensures no processes are using the specified port.
    """
    version = detect_installed_version()
    if not version:
        click.echo("Error: No PostgreSQL version is currently installed.")
        return

    install_prefix = INSTALL_PREFIX_TEMPLATE.format(version=version)
    data_dir = DATA_DIR_TEMPLATE.format(install_prefix=install_prefix)
    pg_ctl = PG_CTL_TEMPLATE.format(install_prefix=install_prefix)

    click.echo(f"Stopping PostgreSQL server for version {version}...")

    if not os.path.exists(pg_ctl):
        click.echo(f"Error: pg_ctl not found at {pg_ctl}. Is PostgreSQL {version} installed?")
        return

    # Attempt to stop PostgreSQL using pg_ctl
    try:
        subprocess.run([pg_ctl, "stop", "-D", data_dir, "-m", "fast"], check=True)
        click.echo("PostgreSQL server stopped successfully.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Failed to stop PostgreSQL server. Error: {e}")
        return

    # Optionally clean up any processes bound to the specified port
    if port:
        if not port.isdigit():
            click.echo("Invalid port specified. Please provide a numeric value.")
            return

        click.echo(f"Checking for processes using port {port}...")
        try:
            result = subprocess.run(["sudo", "lsof", "-i", f":{port}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                processes = result.stdout.decode().strip().split("\n")
                for process in processes[1:]:
                    pid = process.split()[1]
                    subprocess.run(["sudo", "kill", "-9", pid], check=True)
                click.echo(f"Cleared all processes using port {port}.")
            else:
                click.echo(f"No processes found using port {port}.")
        except subprocess.CalledProcessError as e:
            click.echo(f"Failed to clear processes on port {port}. Error: {e.stderr.decode().strip()}")

    click.echo("PostgreSQL stop operation completed.")
