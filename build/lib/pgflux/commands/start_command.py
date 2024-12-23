import click
import os
import subprocess

INSTALL_PREFIX_TEMPLATE = "/usr/local/{version}"
DATA_DIR_TEMPLATE = "/usr/local/{version}/data"
CONFIG_FILE = "/usr/local/pgflux_installed_version.txt"

def get_installed_version():
    """
    Reads the installed PostgreSQL version from the configuration file.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return file.read().strip()
    return None

@click.command(help="Start the PostgreSQL server.")
def start_cli():
    """
    Start the PostgreSQL server using the installed version.
    """
    version = get_installed_version()
    if not version:
        click.echo(f"Error: No installed version found. Ensure PostgreSQL is installed using 'pgflux install'.")
        return

    install_prefix = INSTALL_PREFIX_TEMPLATE.format(version=version)
    data_dir = DATA_DIR_TEMPLATE.format(version=version)
    pg_ctl = os.path.join(install_prefix, "bin", "pg_ctl")

    if not os.path.exists(pg_ctl):
        click.echo(f"Error: pg_ctl not found at {pg_ctl}. Is PostgreSQL {version} installed correctly?")
        return

    if not os.path.exists(data_dir):
        click.echo(f"Error: Data directory not found at {data_dir}. Ensure it exists and is initialized.")
        return

    click.echo(f"Starting PostgreSQL {version} from {data_dir}...")
    try:
        subprocess.run([pg_ctl, "start", "-D", data_dir, "-l", os.path.join(data_dir, "logfile"), "-w"], check=True)
        click.echo(f"PostgreSQL {version} started successfully.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Failed to start PostgreSQL {version}.")
        click.echo(f"Error details: {e}")
        click.echo(f"Check the logfile at {os.path.join(data_dir, 'logfile')} for more details.")
