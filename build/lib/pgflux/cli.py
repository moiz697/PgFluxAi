import click
from pgflux.commands.init_command import init_cli
from pgflux.commands.install_command import install_cli
from pgflux.commands.start_command import start_cli
from pgflux.commands.stop_command import stop_cli
from pgflux.commands.restart_command import restart_cli
from pgflux.commands.remove_command import remove_cli
from pgflux.commands.status_command import status_cli
from pgflux.commands.run_command import run_cli

@click.group()
def pgflux():
    """Main CLI group for PgFlux."""
    pass

# Register commands
pgflux.add_command(init_cli, "init")
pgflux.add_command(install_cli, "install")
pgflux.add_command(start_cli, "start")
pgflux.add_command(stop_cli, "stop")
pgflux.add_command(restart_cli, "restart")
pgflux.add_command(remove_cli, "remove")
pgflux.add_command(status_cli, "status")
pgflux.add_command(run_cli, "run")

if __name__ == "__main__":
    pgflux()
