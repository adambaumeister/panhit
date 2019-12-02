from phlibs.host import HostList
from phlibs.config import ConfigFile
from phlibs.messages import JobStarted

from flask import Flask, escape, request
from phlibs.jqueue import Job, JobQueue

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


@app.route('/run', methods=['POST'])
def run():
    try:
        c, hl = configure(request.get_json())
    except ValueError as e:
        return {
            "Error": str(e)
        }

    # Run the actual job in the background and return immediately
    jq = JobQueue()
    j = Job(hl.run_all_hosts, args=(jq,))

    m = JobStarted()
    m.status = "started"
    m.jid = jq.id

    j.Run()

    return m.GetMsg()