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

    # If a specfile is passed, load from stored configuration instead of parsing as if it were a config file
    elif 'spec' in j:
        (inputs, mods) = c.load_from_spec(j['spec'])
        db = c.get_db()

        if 'name' in j:
            c.name = j['name']
        # Hack - currently HostList only supports one input
        hl = HostList(inputs[0], mods_enabled=mods, db=db)
        return c, hl


################
# VIEW METHODS #
################
@app.route('/', methods=['GET'])
def index():
    """
    Basic index and welcome page.
    :return: index.html
    """
    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)

    db = c.get_db()
    summary = db.summary()
    print(summary)
    return render_template('index.html', summary=summary)

@app.route('/config/input', methods=['GET'])
def config_input_page():
    """
    Configuration landing page
    :return: config.html
    """
    config_type = "input"

    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)

    cdb = c.get_cdb()
    cdb.update_path(config_type)
    docs = cdb.get_all()
    inputs = []
    for doc in docs:
        i = c.get_input_from_data(doc)
        inputs.append(i)

    input_types = c.get_inputs_available()

    return render_template('config.html', items=inputs, config_type=config_type, item_types=input_types)

@app.route('/config/modules', methods=['GET'])
def config_modules_page():
    """
    Configuration landing page
    :return: config.html
    """
    config_type = "modules"

    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)

    cdb = c.get_cdb()
    cdb.update_path(config_type)
    docs = cdb.get_all()

    mods = []
    for doc in docs:
        i = c.get_module_from_data(doc)
        mods.append(i)

    mod_types = c.get_mods_available()

    return render_template('config.html', items=mods, config_type=config_type, item_types=mod_types)

@app.route('/run', methods=['GET'])
def spec_page():
    """
    Render the job runner page
    :return: spec.html
    """
    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)

    # Grab all the inputs
    cdb = c.get_cdb()
    cdb.update_path("input")
    docs = cdb.get_all()
    inputs = []
    for doc in docs:
        i = c.get_input_from_data(doc)
        inputs.append(i)

    # Grab all the modules
    cdb = c.get_cdb()
    cdb.update_path("modules")
    docs = cdb.get_all()
    modules = []
    for doc in docs:
        i = c.get_module_from_data(doc)
        modules.append(i)

    return render_template('spec.html', inputs=inputs, modules=modules)

@app.route('/jobs', methods=['GET'])
def jobs_page():
    """
    Display running, scheduled, and completed jobs.
    :return: Jobs page
    """
    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)
    db = c.get_db()
    j = db.get_all_in_subdir_sorted('jqstatus')

    return render_template('jobs.html', jobs=j)

@app.route('/jobs/<job_id>', methods=['GET'])
def job_page(job_id):
    """
    Return the result of a specific job.
    :return: Jobs page
    """
    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)
    db = c.get_db()

    db.update_path_nocreate(job_id)
    hl = HostList(db=db)
    hosts = hl.get_all_hosts()

    return render_template('job.html', hosts=hosts)


###############
# API METHODS #
###############
@app.route('/api/run', methods=['POST'])
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
    # Set the job quueue name to the configuration spec name
    jq.set_name(c.name)
    j = Job(hl.run_all_hosts, args=(jq,))

    m = JobStarted()
    m.status = "started"
    m.jid = jq.id

    j.Run()

    return m.GetMsg()


@app.route('/api/jobs/<job_id>', methods=['GET'])
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

@app.route('/api/jobs/<job_id>/result', methods=['GET'])
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

    m = JobResult()
    t = request.args.get('table')
    if t:
        page = request.args.get('page')
        m.set_table_from_json(data)
        if page:
            m.page(page, 10)
    else:
        m.set_from_json(data)

    return m.GetMsg()

@app.route('/api/jobs', methods=['GET'])
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

    t = request.args.get('table')
    m = JobList()
    if t:
        page = request.args.get('page')
        m.set_table_from_json(j)
        if page:
            m.page(page, 10)
    else:
        m.set_from_json(j)

    return m.GetMsg()


@app.route('/api/config/<config_type>', methods=['POST'])
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
    m.set_status(0)
    m.long_status = "Sucessfully added {} object.".format(config_type)
    return m.GetMsg()

@app.route('/api/config/<config_type>', methods=['GET'])
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

@app.route('/api/config/<config_type>/<config_name>', methods=['GET'])
def get_config_item(config_type, config_name):
    """
    Retrieve all the configuration objects matching the provided type
    :param config_type: Type of configuration object to retrieve
    :return: ConfigGet
    """
    c = ConfigFile()
    c.load_from_file(DEFAULT_CONFIG_FILE)
    db = c.get_cdb()
    db.update_path(config_type)

    item = db.get(config_name)

    m = ConfigGet()
    m.set_items([item])
    return m.GetMsg()

@app.route('/api/config/<config_type>/<config_name>', methods=['DELETE'])
def delete_config_item(config_type, config_name):
    """
    Retrieve all the configuration objects matching the provided type
    :param config_type: Type of configuration object to retrieve
    :return: ConfigGet
    """
    c = ConfigFile()
    c.load_from_file(DEFAULT_CONFIG_FILE)
    db = c.get_cdb()
    db.update_path(config_type)

    db.delete_id(config_name)

    m = ConfigStatus()
    m.set_name(config_name)
    m.set_status(0)
    m.set_long_status("Deleted item.")
    return m.GetMsg()


@app.route('/api/config/<config_type>/<module_name>/spec', methods=['GET'])
def get_config_spec(config_type, module_name):
    """
    Get the spec of the given configuration type (i.e options etc)
    :param config_type: Type of configuration object to retrieve
    :return: ConfigGet
    """
    c = ConfigFile()
    if config_type == "input":
        inputs = c.get_inputs_available()
        if module_name in inputs:
            mod = inputs[module_name]

    spec = mod.module_options.get_spec()

    m = ModuleSpec()
    m.set_specs(spec)
    return m.GetMsg()