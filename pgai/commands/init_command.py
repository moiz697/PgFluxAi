import click
import os
import subprocess

DEFAULT_VERSION = "pg16"
INSTALL_PREFIX = f"/usr/local/{DEFAULT_VERSION}"
BIN_PATH = os.path.join(INSTALL_PREFIX, "bin")
PG_CTL = os.path.join(BIN_PATH, "pg_ctl")
DATA_DIR = os.path.join(INSTALL_PREFIX, "data")


@click.command(help="Initialize the pgai environment.")
@click.option("--config", default="default.yaml", help="Path to the configuration file.")
@click.option("--force-init", is_flag=True, help="Force reinitialization of the data directory if it exists.")
def init_cli(config, force_init):
    """
    Initializes the pgai environment by checking and preparing PostgreSQL setup.
    """
    click.echo(f"Initializing pgai environment with config: {config}")

    # Validate PostgreSQL binaries
    if not os.path.exists(PG_CTL):
        click.echo(f"Error: pg_ctl not found at {PG_CTL}. Is PostgreSQL {DEFAULT_VERSION} installed?")
        return

    # Handle existing data directory
    if os.path.exists(DATA_DIR):
        if os.listdir(DATA_DIR):
            if force_init:
                click.echo(f"Data directory '{DATA_DIR}' exists and is not empty. Forcing reinitialization.")
                try:
                    subprocess.run(["rm", "-rf", DATA_DIR], check=True)
                    os.makedirs(DATA_DIR, exist_ok=True)
                except Exception as e:
                    click.echo(f"Failed to clean and recreate data directory: {e}")
                    return
            else:
                click.echo(f"Data directory '{DATA_DIR}' exists and is not empty.")
                click.echo("To reinitialize, rerun with the '--force-init' flag.")
                return
        else:
            click.echo(f"Data directory '{DATA_DIR}' is empty. Proceeding with initialization.")
    else:
        click.echo(f"Creating new data directory at '{DATA_DIR}'...")
        os.makedirs(DATA_DIR, exist_ok=True)

    # Initialize PostgreSQL
    try:
        click.echo("Running initdb to initialize the database cluster...")
        subprocess.run([os.path.join(BIN_PATH, "initdb"), "-D", DATA_DIR, "--encoding=UTF8", "--no-locale"], check=True)
        click.echo("Database cluster initialized successfully.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error during initdb: {e}")
        return

    click.echo(f"pgai environment initialized successfully with config: {config}")
