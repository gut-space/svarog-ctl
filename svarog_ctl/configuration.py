"""
Several functions to manage a configuration
"""

import os
import shutil
import yaml

from .globalvars import CONFIG_PATH

def open_config():
    """
    Opens configuration file (typically ~/.appname/config.yaml, but please see
    the glovalvars for details) and returns the yaml dictionary"""
    config_path = CONFIG_PATH
    config_exists = os.path.exists(config_path)
    if not config_exists:
        directory = os.path.dirname(config_path)
        os.makedirs(directory, exist_ok=True)

        template_dir = os.getcwd()
        shutil.copyfile(os.path.join(template_dir, 'config.yml.template'), config_path)
        print("WARNING: config file (%s) was missing, generated using template." % config_path)

    with open(config_path) as f:
        return yaml.safe_load(f) # type: ignore


def save_config(config):
    """Saves the configuration back to config file on disk."""
    with open(CONFIG_PATH, "w") as f:
        return yaml.safe_dump(config, f)
