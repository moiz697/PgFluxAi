import click
import subprocess
import os
import sys

POSTGRES_BRANCH_MAP = {
    "pg16": "REL_16_STABLE",
    "pg17": "REL_17_STABLE",
}

CONFIG_FILE = "/usr/local/pgai_installed_version.txt"
INSTALL_PREFIX_TEMPLATE = "/usr/local/{version}"  # Default installation prefix


def parallel_build_args():
    """
    Determine the number of CPUs for parallel build and return the `-j` argument.
    """
    cpu_count = os.cpu_count() or 1
    return f"-j{cpu_count}"


def write_installed_version(version):
    """
    Writes the installed PostgreSQL version to the configuration file.
    """
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(version)
        click.echo(f"Installed version '{version}' recorded in {CONFIG_FILE}.")
    except IOError as e:
        click.echo(f"Error writing installed version to {CONFIG_FILE}: {e}")
        sys.exit(1)


@click.command(help="Install PostgreSQL from source. Usage: pgflux install [version] [options]")
@click.argument("version", required=True)
@click.option("--p", "port", default="5432", help="Port for PostgreSQL to listen on (default: 5432).")
@click.option("-d", "data_dir", default=None, help="Data directory for the database cluster.")
@click.option("--clean", is_flag=True, help="Clean the build directory before rebuilding.")
@click.option("--force-init", is_flag=True, help="Force reinitialization of the data directory if it exists.")
@click.option("-u", "user", default="postgres", help="Default superuser for the PostgreSQL cluster (default: postgres).")
@click.option("--prefix", "install_prefix", default=None, help="Installation prefix for PostgreSQL (default: /usr/local/{version}).")
def install_cli(version, port, data_dir, clean, force_init, user, install_prefix):
    """
    Install PostgreSQL from source.
    """
    if version not in POSTGRES_BRANCH_MAP:
        click.echo(f"Unsupported version '{version}'. Supported versions: {', '.join(POSTGRES_BRANCH_MAP.keys())}")
        sys.exit(1)

    branch = POSTGRES_BRANCH_MAP[version]

    if install_prefix is None:
        install_prefix = INSTALL_PREFIX_TEMPLATE.format(version=version)
    else:
        # Ensure the install_prefix exists
        os.makedirs(install_prefix, exist_ok=True)

    if data_dir is None:
        data_dir = os.path.join(install_prefix, "data")

    click.echo(f"Installing PostgreSQL {version} from source...")
    click.echo(f"Branch: {branch}")
    click.echo(f"Install prefix: {install_prefix}")
    click.echo(f"Data directory: {data_dir}")
    click.echo(f"Port: {port}")
    click.echo(f"Default superuser: {user}")

    # Automatically fix permissions if needed
    if not os.access(install_prefix, os.W_OK):
        click.echo(f"Fixing permissions for directory '{install_prefix}'...")
        try:
            subprocess.run(["sudo", "mkdir", "-p", install_prefix], check=True)
            subprocess.run(["sudo", "chown", "-R", f"{os.getlogin()}:{os.getlogin()}", install_prefix], check=True)
        except subprocess.CalledProcessError as e:
            click.echo(f"Error fixing permissions for '{install_prefix}': {e}")
            sys.exit(1)

    # Prepare build directory
    build_dir = f"/tmp/{version}_build"
    if clean and os.path.exists(build_dir):
        click.echo(f"Cleaning build directory: {build_dir}")
        subprocess.run(["rm", "-rf", build_dir], check=True)

    if not os.path.exists(build_dir):
        click.echo("Cloning PostgreSQL source code...")
        subprocess.run(["git", "clone", "https://github.com/postgres/postgres.git", build_dir], check=True)

    click.echo(f"Checking out branch: {branch}")
    subprocess.run(["git", "checkout", branch], cwd=build_dir, check=True)

    # Configure the build
    click.echo("Configuring PostgreSQL with Python support...")
    subprocess.run(["./configure", f"--prefix={install_prefix}", "--with-python"], cwd=build_dir, check=True)

    # Build PostgreSQL
    click.echo("Building PostgreSQL...")
    subprocess.run(["make", parallel_build_args()], cwd=build_dir, check=True)

    # Install PostgreSQL
    click.echo("Installing PostgreSQL...")
    subprocess.run(["make", parallel_build_args(), "install"], cwd=build_dir, check=True)

    # Handle data directory
    if os.path.exists(data_dir):
        if os.listdir(data_dir) and not force_init:
            click.echo(f"Data directory '{data_dir}' exists and is not empty.")
            click.echo("Use '--force-init' to reinitialize the data directory.")
            sys.exit(1)
        else:
            click.echo(f"Clearing existing data directory: {data_dir}")
            subprocess.run(["rm", "-rf", data_dir], check=True)
    os.makedirs(data_dir, exist_ok=True)

    # Initialize database cluster
    initdb_path = os.path.join(install_prefix, "bin", "initdb")
    click.echo("Initializing the database cluster...")
    subprocess.run([initdb_path, "-D", data_dir, "--encoding=UTF8", "--no-locale", "--username=postgres"], check=True)

    # Update postgresql.conf
    postgresql_conf = os.path.join(data_dir, "postgresql.conf")
    with open(postgresql_conf, "a") as conf:
        conf.write(f"\nport = {port}\n")

    # Start PostgreSQL temporarily for configuration
    pg_ctl_path = os.path.join(install_prefix, "bin", "pg_ctl")
    log_file = os.path.join(data_dir, "logfile")

    click.echo("Starting PostgreSQL temporarily to configure the default superuser...")
    try:
        subprocess.run([pg_ctl_path, "start", "-D", data_dir, "-l", log_file, "-w"], check=True)

        # Create superuser role if it doesn't exist
        psql_path = os.path.join(install_prefix, "bin", "psql")
        create_role_command = (
            f"DO $$ BEGIN "
            f"IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{user}') THEN "
            f"CREATE ROLE {user} WITH LOGIN SUPERUSER PASSWORD '{user}'; "
            f"END IF; END $$;"
        )
        subprocess.run(
            [psql_path, "-U", "postgres", "-p", port, "-d", "postgres", "-c", create_role_command],
            check=True,
        )
        click.echo(f"Superuser role '{user}' created successfully.")
    except subprocess.CalledProcessError as e:
        click.echo("Error configuring default superuser role.")
        if os.path.exists(log_file):
            click.echo("PostgreSQL log output:")
            with open(log_file, "r") as lf:
                click.echo(lf.read())
        else:
            click.echo("No log file found.")
        subprocess.run([pg_ctl_path, "stop", "-D", data_dir, "-m", "immediate"], check=True)
        sys.exit(1)

    subprocess.run([pg_ctl_path, "stop", "-D", data_dir, "-m", "immediate"], check=True)

    # Record the installed version
    write_installed_version(version)

    click.echo(f"\nPostgreSQL installation and initialization complete at {install_prefix}.")
