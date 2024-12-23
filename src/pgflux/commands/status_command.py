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

@click.command(help="Check the status of the PostgreSQL server.")
@click.option("--p", "port", default=None, help="Port on which PostgreSQL is running (optional).")
def status_cli(port):
    """
    Checks the status of the PostgreSQL server. Optionally checks the specified port.
    """
    version = detect_installed_version()
    if not version:
        click.echo("Error: No PostgreSQL version is currently installed.")
        return

    install_prefix = INSTALL_PREFIX_TEMPLATE.format(version=version)
    pg_ctl = PG_CTL_TEMPLATE.format(install_prefix=install_prefix)

    if not os.path.exists(pg_ctl):
        click.echo(f"Error: pg_ctl not found at {pg_ctl}. Is PostgreSQL {version} installed?")
        return

    # Check PostgreSQL status
    try:
        result = subprocess.run([pg_ctl, "status", "-D", DATA_DIR_TEMPLATE.format(install_prefix=install_prefix)],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            click.echo(f"PostgreSQL {version} is running.")
            click.echo(result.stdout)
        else:
            click.echo(f"PostgreSQL {version} is not running.")
            click.echo(result.stderr)
    except subprocess.CalledProcessError as e:
        click.echo(f"Failed to check status. Error: {e.stderr.decode().strip()}")

    # Optionally check for port usage
    if port:
        if not port.isdigit():
            click.echo("Invalid port specified. Please provide a numeric value.")
            return

        click.echo(f"Checking for processes using port {port}...")
        try:
            result = subprocess.run(["lsof", "-i", f":{port}"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0 and result.stdout:
                click.echo(f"Processes are using port {port}:")
                click.echo(result.stdout.strip())
            else:
                click.echo(f"No processes found using port {port}.")
        except subprocess.CalledProcessError as e:
            click.echo(f"Failed to check port usage. Error: {e.stderr.decode().strip()}")

    click.echo("Status check completed.")
