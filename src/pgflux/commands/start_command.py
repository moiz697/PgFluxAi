import click
import os
import subprocess

DEFAULT_PORT = "5432"
DEFAULT_USER = "postgres"
INSTALL_PREFIX_TEMPLATE = "/usr/local/{version}"
DATA_DIR_TEMPLATE = "{install_prefix}/data"
PG_CTL_TEMPLATE = "{install_prefix}/bin/pg_ctl"
PSQL_TEMPLATE = "{install_prefix}/bin/psql"
CONFIG_FILE = "/usr/local/pgflux_installed_version.txt"


def detect_installed_version():
    """
    Reads the installed PostgreSQL version from the configuration file.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return file.read().strip()
    raise RuntimeError("No installed PostgreSQL version found. Please install using 'pgflux install'.")


@click.command(help="Start the PostgreSQL server.")
@click.option("--p", "port", default=DEFAULT_PORT, help=f"Port for PostgreSQL to listen on (default: {DEFAULT_PORT}).")
@click.option("--u", "user", default=DEFAULT_USER, help=f"Database superuser to ensure exists (default: {DEFAULT_USER}).")
@click.option("--d", "data_dir", default=None, help="Custom data directory for PostgreSQL.")
def start_cli(port, user, data_dir):
    """
    Start the PostgreSQL server using the installed version or custom options.
    """
    try:
        version = detect_installed_version()
    except RuntimeError as e:
        click.echo(str(e))
        return

    install_prefix = INSTALL_PREFIX_TEMPLATE.format(version=version)
    pg_ctl = PG_CTL_TEMPLATE.format(install_prefix=install_prefix)
    psql = PSQL_TEMPLATE.format(install_prefix=install_prefix)

    # Use custom data directory if provided
    if not data_dir:
        data_dir = DATA_DIR_TEMPLATE.format(install_prefix=install_prefix)

    if not os.path.exists(pg_ctl):
        click.echo(f"Error: pg_ctl not found at {pg_ctl}. Is PostgreSQL {version} installed correctly?")
        return

    if not os.path.exists(data_dir):
        click.echo(f"Error: Data directory not found at {data_dir}. Ensure it exists and is initialized.")
        return

    click.echo(f"Starting PostgreSQL {version} on port {port}...")

    try:
        subprocess.run([pg_ctl, "start", "-D", data_dir, "-l", os.path.join(data_dir, "logfile"), "-w"], check=True)
        click.echo(f"PostgreSQL {version} started successfully.")

        # Ensure the superuser exists
        click.echo(f"Ensuring superuser role '{user}' exists...")
        create_superuser(psql, user, port)

    except subprocess.CalledProcessError as e:
        click.echo(f"Failed to start PostgreSQL {version}. Error: {e}")
        click.echo(f"Check the logfile at {os.path.join(data_dir, 'logfile')} for more details.")
    except FileNotFoundError:
        click.echo(f"Error: Required PostgreSQL binaries not found. Ensure PostgreSQL is installed and accessible.")


def create_superuser(psql, user, port):
    """
    Ensure the specified superuser role exists in PostgreSQL.
    """
    try:
        result = subprocess.run(
            [psql, "-U", user, "-p", port, "-d", "postgres", "-c", "\\du"],
            capture_output=True,
            text=True
        )
        if user not in result.stdout:
            click.echo(f"Superuser '{user}' does not exist. Creating...")
            create_role_command = f"CREATE ROLE {user} WITH SUPERUSER LOGIN PASSWORD 'pgflux';"
            subprocess.run(
                [psql, "-U", user, "-p", port, "-d", "postgres", "-c", create_role_command],
                check=True
            )
            click.echo(f"Superuser role '{user}' created successfully.")
        else:
            click.echo(f"Superuser role '{user}' already exists.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Failed to ensure superuser role. Error: {e.stderr if e.stderr else 'Unknown error'}")


if __name__ == "__main__":
    start_cli()
