import click
from pgflux.commands.init_command import init_cli
from pgflux.commands.install_command import install_cli
from pgflux.commands.start_command import start_cli
from pgflux.commands.stop_command import stop_cli
from pgflux.commands.status_command import status_cli
from pgflux.commands.run_command import run_cli  # Import the run command


@click.group()
def pgflux_cli():
    """
    Main CLI group for PgFlux commands.
    """
    pass


# Registering commands
pgflux_cli.add_command(init_cli, "init")
pgflux_cli.add_command(install_cli, "install")
pgflux_cli.add_command(start_cli, "start")
pgflux_cli.add_command(stop_cli, "stop")
pgflux_cli.add_command(status_cli, "status")
pgflux_cli.add_command(run_cli, "run")  # Add the run command here


if __name__ == "__main__":
    pgflux_cli()
