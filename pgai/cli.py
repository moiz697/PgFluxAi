import click
from pgai.commands.init_command import init_cli
from pgai.commands.run_command import run_cli
from pgai.commands.status_command import status_cli
from pgai.commands.install_command import install_cli
from pgai.commands.start_command import start_cli
from pgai.commands.remove_command import remove_cli
from pgai.commands.stop_command import stop_cli
@click.group(help="pgai CLI - A tool to manage and interact with PostgreSQL installations.")
def main():
    pass

main.add_command(init_cli, name="init")
main.add_command(run_cli, name="run")
main.add_command(status_cli, name="status")
main.add_command(install_cli, name="install")
main.add_command(start_cli, name="start")
main.add_command(remove_cli, name="remove")
main.add_command(stop_cli, "stop")
if __name__ == "__main__":
    main()
