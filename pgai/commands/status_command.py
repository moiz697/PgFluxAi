import click
import subprocess
import os

CONFIG_FILE = "/usr/local/pgai_installed_version.txt"
INSTALL_PREFIX_TEMPLATE = "/usr/local/{version}"


def get_installed_version():
    """
    Retrieve the installed PostgreSQL version from the configuration file.
    """
    if not os.path.exists(CONFIG_FILE):
        click.echo(f"Error: Configuration file {CONFIG_FILE} not found. Is PostgreSQL installed?")
        raise FileNotFoundError("Installed version not found.")
    with open(CONFIG_FILE, "r") as f:
        return f.read().strip()


@click.command(help="Check the status of the pgai environment.")
def status_cli():
    """
    Checks the status of the pgai environment.
    Verifies if PostgreSQL is running and ensures binaries are accessible.
    """
    try:
        version = get_installed_version()
    except FileNotFoundError:
        return

    install_prefix = INSTALL_PREFIX_TEMPLATE.format(version=version)
    pg_ctl = os.path.join(install_prefix, "bin", "pg_ctl")
    psql = os.path.join(install_prefix, "bin", "psql")
    data_dir = os.path.join(install_prefix, "data")

    click.echo(f"Checking PostgreSQL status for version {version}...")

    # Check if pg_ctl binary exists
    if not os.path.exists(pg_ctl):
        click.echo(f"Error: pg_ctl not found at {pg_ctl}. Is PostgreSQL {version} installed?")
        return

    # Check if data directory exists
    if not os.path.exists(data_dir):
        click.echo(f"Error: Data directory not found at {data_dir}. Is PostgreSQL initialized?")
        return

    # Check PostgreSQL server status
    try:
        result = subprocess.run(
            [pg_ctl, "status", "-D", data_dir],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        click.echo("PostgreSQL server is running.")
    except subprocess.CalledProcessError as e:
        click.echo("PostgreSQL server is not running.")
        click.echo(f"Error: {e.stderr.decode().strip()}")
        click.echo("Use 'pgai start' to start the server.")

    # Check if psql binary exists
    click.echo("Verifying psql binary...")
    if os.path.exists(psql):
        click.echo(f"psql found at {psql}.")
    else:
        click.echo(f"Error: psql not found at {psql}. Ensure PostgreSQL is installed correctly.")

    click.echo("pgai environment status check completed.")
