import click
import os
import subprocess

INSTALL_PREFIX_TEMPLATE = "/usr/local/{version}"
DATA_DIR_TEMPLATE = "{install_prefix}/data"
PG_CTL_TEMPLATE = "{install_prefix}/bin/pg_ctl"
CONFIG_FILE = "/usr/local/pgflux_installed_version.txt"

def detect_installed_version():
    """
    Reads the installed PostgreSQL version from the configuration file.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return file.read().strip()
    return None

def write_installed_version(version):
    """
    Writes the installed PostgreSQL version to the configuration file.
    """
    try:
        with open(CONFIG_FILE, "w") as file:
            file.write(version)
        click.echo(f"Installed version '{version}' recorded in {CONFIG_FILE}.")
    except IOError as e:
        click.echo(f"Error writing installed version to {CONFIG_FILE}: {e}")
        raise

@click.command(help="Initialize the pgflux environment.")
@click.option("--config", default="default.yaml", help="Path to the configuration file.")
@click.option("--force-init", is_flag=True, help="Force reinitialization of the data directory if it exists.")
def init_cli(config, force_init):
    """
    Initializes the pgflux environment by checking and preparing PostgreSQL setup.
    """
    version = detect_installed_version() or "pg16"
    install_prefix = INSTALL_PREFIX_TEMPLATE.format(version=version)
    pg_ctl = PG_CTL_TEMPLATE.format(install_prefix=install_prefix)
    data_dir = DATA_DIR_TEMPLATE.format(install_prefix=install_prefix)

    click.echo(f"Initializing pgflux environment with config: {config}")

    # Validate PostgreSQL binaries
    if not os.path.exists(pg_ctl):
        click.echo(f"Error: pg_ctl not found at {pg_ctl}. Is PostgreSQL {version} installed?")
        return

    # Handle existing data directory
    if os.path.exists(data_dir):
        if os.listdir(data_dir):
            if force_init:
                click.echo(f"Data directory '{data_dir}' exists and is not empty. Forcing reinitialization.")
                try:
                    subprocess.run(["rm", "-rf", data_dir], check=True)
                    os.makedirs(data_dir, exist_ok=True)
                except Exception as e:
                    click.echo(f"Failed to clean and recreate data directory: {e}")
                    return
            else:
                click.echo(f"Data directory '{data_dir}' exists and is not empty.")
                click.echo("To reinitialize, rerun with the '--force-init' flag.")
                return
        else:
            click.echo(f"Data directory '{data_dir}' is empty. Proceeding with initialization.")
    else:
        click.echo(f"Creating new data directory at '{data_dir}'...")
        os.makedirs(data_dir, exist_ok=True)

    # Initialize PostgreSQL
    try:
        click.echo("Running initdb to initialize the database cluster...")
        subprocess.run([os.path.join(install_prefix, "bin", "initdb"), "-D", data_dir, "--encoding=UTF8", "--no-locale"], check=True)
        click.echo("Database cluster initialized successfully.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error during initdb: {e}")
        return

    # Write the installed version if initialization is successful
    write_installed_version(version)

    click.echo(f"pgflux environment initialized successfully with config: {config}")
