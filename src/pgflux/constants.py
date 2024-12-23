import os
DEFAULT_VERSION = "pg16"
INSTALL_PREFIX = f"/usr/local/{DEFAULT_VERSION}"
BIN_PATH = os.path.join(INSTALL_PREFIX, "bin")
PG_CTL = os.path.join(BIN_PATH, "pg_ctl")
DATA_DIR = os.path.join(INSTALL_PREFIX, "data")
