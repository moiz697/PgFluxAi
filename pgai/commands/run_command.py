import click
import os
import subprocess

DEFAULT_PORT = "5432"
DEFAULT_USER = "postgres"
CONFIG_FILE = "/usr/local/pgai_installed_version.txt"
INSTALL_PREFIX_TEMPLATE = "/usr/local/{version}"


@click.command(help="Run psql to connect to a PostgreSQL database.")
@click.argument("database", required=True)
@click.option("--p", "port", default=DEFAULT_PORT, help=f"Port for connecting to the database (default: {DEFAULT_PORT}).")
@click.option("-u", "user", default=DEFAULT_USER, help=f"Database user to connect as (default: {DEFAULT_USER}).")
@click.option("--version", default=None, help="PostgreSQL version to use (e.g., pg16, pg17).")
def run_cli(database, port, user, version):
    """
    Runs the psql command to connect to the specified PostgreSQL database.
    """
    if not version:
        try:
            version = detect_installed_version()
        except RuntimeError as e:
            click.echo(str(e))
            return

    bin_path = os.path.join(INSTALL_PREFIX_TEMPLATE.format(version=version), "bin")
    psql_path = os.path.join(bin_path, "psql")

    # Check if psql exists
    if not os.path.exists(psql_path):
        click.echo(f"psql not found at {psql_path}. Is PostgreSQL {version} installed?")
        return

    click.echo(f"Connecting to database '{database}' on port {port} as user '{user}'...")

    try:
        subprocess.run([psql_path, "-U", user, "-p", port, "-d", database], check=True)
    except subprocess.CalledProcessError as e:
        click.echo("Failed to connect to the PostgreSQL server. Check the error below:")
        click.echo(e.stderr.decode() if e.stderr else "Unknown error.")
    except FileNotFoundError:
        click.echo(f"Error: psql command not found at {psql_path}. Ensure PostgreSQL is installed and accessible.")


def detect_installed_version():
    """
    Reads the installed PostgreSQL version from the configuration file.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return file.read().strip()
    raise RuntimeError("No installed PostgreSQL version found. Please install using 'pgai install'.")


if __name__ == "__main__":
    run_cli()
