import click
import os
import subprocess
from pgflux.constants import PG_CTL


@click.command(help="Restart the PostgreSQL server.")
@click.option("--p", "port", default="5432", help="Port for PostgreSQL to listen on.")
def restart_cli(port):
    try:
        subprocess.run([PG_CTL, "stop", "-D", "/usr/local/pg16/data", "-m", "fast"], check=True)
        subprocess.run([PG_CTL, "start", "-D", "/usr/local/pg16/data", "-l", "/usr/local/pg16/data/logfile", "-w"], check=True)
        click.echo(f"PostgreSQL restarted successfully on port {port}.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Failed to restart PostgreSQL. {e}")
