from phlibs.host import HostList
from phlibs.config import ConfigFile
from phlibs.messages import *

from flask import Flask, escape, request, render_template
from phlibs.jqueue import Job, JobQueue
from phlibs.outputs import JsonOutput

# Default path to the configuration file for PANHIT
DEFAULT_CONFIG_FILE="server.yaml"

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

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/run', methods=['POST'])
def run():
    """
    Primary job schedular
    This route takes a complete job spec from the API and outputs the scheduled job ID as a valid JobQueue ID, which
    it then runs.
    :return: JobStarted JSON message type
    """
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


@app.route('/jobs/get/<job_id>', methods=['GET'])
def get_job(job_id):
    """
    Individual job retrieval
    This route retreives a job, either current or historical, from the configured database type.
    :param job_id: ID of job, either running, scheduled, or existing.
    :return: JobStatus JSON message type.
    """
    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)
    db = c.get_db()
    db.update_path(job_id)

    jqstatus = db.get('jqstatus')
    m = JobStatus()
    m.set_from_json(jqstatus)

    return m.GetMsg()

@app.route('/jobs/get/<job_id>/result', methods=['GET'])
def get_job_result(job_id):
    """
    Job result retrieval
    This route retreives a job, either current or historical, from the configured database type.
    :param job_id: ID of completed job.
    :return: JobResult message type
    """
    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)
    db = c.get_db()
    db.update_path(job_id)
    data = {}
    jqstatus = db.get('jqstatus')

    o = JsonOutput()
    if jqstatus['completed'] == jqstatus['queued']:
        hl = HostList(db=db)
        data = o.Output(hl)

    return data

@app.route('/jobs/list', methods=['GET'])
def list_jobs():
    """
    List all current and past jobs.
    This call can be paginated but is not by default
    :return: JobList JSON message type
    """
    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)
    db = c.get_db()
    j = db.get_all_in_subdir_sorted('jqstatus')

    m = JobList()
    m.set_from_json(j)

    return m.GetMsg()


@app.route('/config/<config_type>', methods=['POST'])
def add_config(config_type):
    """
    Add a configuration object of the given type with the given object value
    Object is expected as JSON.
    :param config_type: Type of configuration object to add
    :return: ConfigStatus
    """
    c = ConfigFile()
    c.load_from_file(DEFAULT_CONFIG_FILE)
    db = c.get_cdb()
    db.update_path(config_type)
    input_json = request.get_json()

    name = input_json['name']

    db.write_id(name, input_json)

    m = ConfigStatus()
    m.set_name(name)
    m.set_status('Added.')
    return m.GetMsg()

@app.route('/config/<config_type>', methods=['GET'])
def get_config(config_type):
    """
    Retrieve all the configuration objects matching the provided type
    :param config_type: Type of configuration object to retrieve
    :return: ConfigGet
    """
    c = ConfigFile()
    c.load_from_file(DEFAULT_CONFIG_FILE)
    db = c.get_cdb()
    db.update_path(config_type)

    names = []
    for item in db.get_all():
        names.append(item['name'])

    m = ConfigGet()
    m.set_items(names)
    return m.GetMsg()