"""
Sets up global variables for a project: application name, version, logging

- attempts to load the file ~/.appname/config.yml (but will silently continue
  if it's missing or doesn't have expected entries)
"""

import os
import logging
import yaml

DEV_ENVIRONMENT =  os.environ.get("DEV_ENVIRONMENT") is not None
APP_NAME = "svarog-ctl"
VERSION = "0.1.0"

CONFIG_DIRECTORY: str = os.environ.get("SVAROG_CONFIG_DIR") # type: ignore
if CONFIG_DIRECTORY is None:
    if DEV_ENVIRONMENT:
        CONFIG_DIRECTORY = os.path.abspath("./config")
    else:
        CONFIG_DIRECTORY = os.path.expanduser("~/.config/%s" % (APP_NAME,))

CONFIG_PATH = os.path.join(CONFIG_DIRECTORY, "config.yml")
LOG_FILE = os.path.join(CONFIG_DIRECTORY, APP_NAME + ".log") if not DEV_ENVIRONMENT else None

if not os.path.exists(CONFIG_DIRECTORY):
    os.makedirs(CONFIG_DIRECTORY, exist_ok=True)

# Loglevel is a bit complicated. By default, it's INFO, unless it's set in the config file,
# unless it's a dev environment, then it's DEBUG.
LOGLEVEL = logging.INFO

SHORT_LOG = True

try:
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f) # type: ignore
        lv = config["logging"]["level"]
        LOGLEVEL = logging._nameToLevel[lv] # pylint: disable=protected-access
except IOError:
    pass

try:
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f) # type: ignore
        LOG_FILE = os.path.expanduser(config["logging"]["file"])
except IOError: # file not found, we don't care
    pass
except KeyError: # file found, but doesn't have logging/file key. We still don't care
    pass

if LOG_FILE == "stdout":
    LOG_FILE = None

print("Logging on level %s to file %s" % (logging.getLevelName(LOGLEVEL), LOG_FILE))

if DEV_ENVIRONMENT:
    LOGLEVEL = logging.DEBUG

if SHORT_LOG:
    fmt='%(asctime)s %(levelname)7s: %(message)s'
    datefmt='%H:%M:%S'
else:
    fmt = '%(asctime)s %(levelname)s %(filename)s:%(lineno)d: %(message)s'
    datefmt = None # This will use the default ‘%Y-%m-%d %H:%M:%S,uuu’

logging.basicConfig(level = LOGLEVEL,
                    format=fmt,
                    datefmt=datefmt,
                    filename=LOG_FILE)
