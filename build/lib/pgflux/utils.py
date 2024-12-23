import os


def parallel_build_args():
    return f"-j{os.cpu_count() or 1}"


def write_installed_version(version):
    config_file = "/usr/local/pgflux_installed_version.txt"
    with open(config_file, "w") as f:
        f.write(version)
