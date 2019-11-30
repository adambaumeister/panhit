from phlibs.host import HostList
from phlibs.config import ConfigFile
from phlibs.db import JsonDB
from tabulate import tabulate
import getpass
import os
import argparse
import urllib3
from flask import Flask, escape, request

# Default path to the configuration file for PANHIT
DEFAULT_CONFIG_FILE="panhit.yaml"

app = Flask(__name__)

def configure(j):
    """
    Configures PANHIT.
    :param j: (dict) Dictionary as received from JSON
    :return: ConfigFile object, HostList object
    """
    mod_opts = {}
    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)
    # Add any configuration that the client has sent in the request
    if 'config' in j:
        c.unpickle(j['config'])

        if 'mod_opts' in j['config']:
            mod_opts = j['config']['mod_opts']

    mods = c.init_modules(mod_opts)

    db = c.get_db()
    input = c.get_input(mod_opts)
    hl = HostList(input, mods_enabled=mods, db=db)
    return c, hl


@app.route('/', methods=['POST'])
def run():
    try:
        c, hl = configure(request.get_json())
    except ValueError as e:
        return {
            "Error": str(e)
        }

    hl.run_all_hosts()
    return c.db