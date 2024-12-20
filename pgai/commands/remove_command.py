import click
import subprocess
import os
import sys

CONFIG_FILE = "/usr/local/pgai_installed_version.txt"

def detect_installed_version():
    """
    Reads the installed PostgreSQL version from the configuration file.
    """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return file.read().strip()
    return None

@click.command(help="Remove the installed PostgreSQL version.")
@click.argument("version", required=False)
def remove_cli(version):
    if not version:
        # Detect installed version if not specified
        version = detect_installed_version()
        if not version:
            click.echo("No PostgreSQL version specified and no installed version detected.")
            sys.exit(1)

    install_prefix = f"/usr/local/{version}"

    if not os.path.exists(install_prefix):
        click.echo(f"No PostgreSQL installation found at {install_prefix}.")
        sys.exit(1)

    # Stop PostgreSQL if running
    pg_ctl_path = os.path.join(install_prefix, "bin", "pg_ctl")
    data_dir = os.path.join(install_prefix, "data")
    if os.path.exists(pg_ctl_path) and os.path.exists(data_dir):
        click.echo("Stopping PostgreSQL server before removal...")
        try:
            subprocess.run([pg_ctl_path, "stop", "-D", data_dir, "-m", "fast"], check=True)
            click.echo("PostgreSQL server stopped successfully.")
        except subprocess.CalledProcessError:
            click.echo("Failed to stop PostgreSQL server. It may not be running.")

    # Remove PostgreSQL installation
    click.echo(f"Removing PostgreSQL installation at {install_prefix}...")
    try:
        subprocess.run(["rm", "-rf", install_prefix], check=True)
        # Remove the configuration file if the removed version matches
        if version == detect_installed_version():
            os.remove(CONFIG_FILE)
        click.echo("PostgreSQL removed successfully.")
    except Exception as e:
        click.echo(f"Error removing PostgreSQL: {e}")
        sys.exit(1)
