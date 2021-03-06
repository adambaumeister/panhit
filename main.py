from phlibs.host import HostList
from phlibs.config import ConfigFile
from phlibs.messages import *

from flask import Flask, escape, request, render_template
from phlibs.jqueue import Job, JobQueue
from phlibs.outputs import JsonOutput

# Default path to the configuration file for PANHIT
DEFAULT_CONFIG_FILE="server.yaml"

application = Flask(__name__)

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
        (inputs, mods, tag_policies, outputs) = c.load_from_spec(j['spec'])
        db = c.get_db()
        if 'name' in j:
            c.name = j['name']
        # Hack - currently HostList only supports one input
        hl = HostList(inputs[0], mods_enabled=mods, db=db, tags_policy=tag_policies, output=outputs)
        return c, hl


################
# VIEW METHODS #
################
@application.route('/', methods=['GET'])
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
    return render_template('index.html', summary=summary)

@application.route('/config/input', methods=['GET'])
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
    config_descr = """
    An Input is a list of host IP addresses, either statically defined or dynamically retrieved.
    """

    return render_template('config.html', items=inputs, config_type=config_type, config_descr=config_descr, item_types=input_types)

@application.route('/config/outputs', methods=['GET'])
def config_output_page():
    """
    Configuration landing page
    :return: config.html
    """
    config_type = "output"

    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)

    cdb = c.get_cdb()
    cdb.update_path(config_type)
    docs = cdb.get_all()
    outputs = []
    for doc in docs:
        i = c.get_output_from_data(doc)
        outputs.append(i)

    output_types = c.get_outputs_available()

    config_descr = """
    Outputs act as stores - seperate from the local database - for host information 
    """

    return render_template('config.html', items=outputs, config_type=config_type, config_descr=config_descr, item_types=output_types)

@application.route('/config/tags', methods=['GET'])
def config_tags():
    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)
    db = c.get_db()
    j = db.get_all_in_subdir_sorted('jqstatus', limit=5)
    cdb = c.get_cdb()

    cdb.update_path("tags")
    docs = cdb.get_all()

    return render_template('tag_config.html', jobs=j, items=docs)

@application.route('/config/taglist', methods=['GET'])
def config_taglist():
    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)
    cdb = c.get_cdb()

    cdb.update_path("tags")
    tags = cdb.get_all()
    cdb = c.get_cdb()

    cdb.update_path("taglist")
    docs = cdb.get_all()

    return render_template('taglist.html', tags=tags, items=docs)

@application.route('/config/modules', methods=['GET'])
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

    config_descr = """
    A module retrieves additional information about a host, to be later displayed or used as categorization. 
    """

    return render_template('config.html', items=mods, config_type=config_type, config_descr=config_descr, item_types=mod_types)

@application.route('/run', methods=['GET'])
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

    cdb = c.get_cdb()
    cdb.update_path("taglist")
    docs = cdb.get_all()
    tag_policies = docs

    cdb = c.get_cdb()
    cdb.update_path("output")
    docs = cdb.get_all()
    outputs = docs

    cdb = c.get_cdb()
    cdb.update_path("specs")
    docs = cdb.get_all()
    specs = docs

    return render_template('spec.html', inputs=inputs, modules=modules, tag_policies=tag_policies, outputs=outputs, specs=specs)

@application.route('/jobs', methods=['GET'])
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

@application.route('/jobs/<job_id>', methods=['GET'])
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
    job_status = db.get('jqstatus')

    return render_template('job.html', hosts=hosts, job=job_status)


###############
# API METHODS #
###############
@application.route('/api/run', methods=['POST'])
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

    j = request.get_json()
    if j["save"]:
        # Save the job as a spec
        cdb = c.get_cdb()
        cdb.update_path("specs")
        cdb.write(request.get_json())

    # Run the actual job in the background and return immediately
    jq = JobQueue()
    # Set the job quueue name to the configuration spec name
    db = c.get_db()
    db.update_path(jq.id)
    jq.set_db(db)
    jq.set_name(c.name)
    j = Job(hl.run_all_hosts, args=(jq,))

    m = JobStarted()
    m.status = "started"
    m.jid = jq.id
    j.Run()

    return m.GetMsg()


@application.route('/api/jobs/<job_id>', methods=['GET'])
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


@application.route('/api/specs/<spec_id>', methods=['GET'])
def get_job_spec(spec_id):
    """
    Get a saved job spec
    :param spec_id: ID of spec
    :return: JobSpec type
    """
    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)
    cdb = c.get_cdb()
    cdb.update_path("specs")

    json = cdb.get(spec_id)
    return json


@application.route('/api/jobs/<job_id>/result', methods=['GET'])
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
        html = request.args.get('as_html')
        m.set_table_from_json(data)
        if page:
            m.page(page, 5)

        if html:
            return m.as_html()

    else:
        m.set_from_json(data)

    return m.GetMsg()

@application.route('/api/jobs', methods=['GET'])
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
    j.reverse()
    t = request.args.get('table')
    m = JobList()
    if t:
        page = request.args.get('page')
        html = request.args.get('as_html')
        m.set_table_from_json(j)
        if page:
            m.page(page, 10)

        if html:
            return m.as_html()
    else:
        m.set_from_json(j)

    return m.GetMsg()

@application.route('/api/jobs/<job_id>/graph', methods=['GET'])
def graph_job(job_id):
    """
    Return a graph of host based data for a given job
    :return: JobGraph message type
    """
    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)
    db = c.get_db()
    db.update_path_nocreate(job_id)
    hl = HostList(db=db)
    labels,data,bg_colors = hl.stats_by_tag()

    m = JobGraph()
    m.set_graph(labels,data, bg_colors)
    return m.GetMsg()

@application.route('/api/jobs/<job_id>/tag_spec', methods=['GET'])
def get_job_tag_spec(job_id):
    """
    Job tag spec
    Returns all the fields that are taggable from the result of a job
    :param job_id: ID of job, either running, scheduled, or existing.
    :return: JobStatus JSON message type.
    """
    c = ConfigFile()
    # First load in all the configuration from the provided configuration file, if it exists
    c.load_from_file(DEFAULT_CONFIG_FILE)
    db = c.get_db()
    db.update_path(job_id)

    index = db.get("index")
    first_id = index[0]
    j = db.get(first_id)
    m = TagSpec()
    m.set_spec(j)
    if request.args.get('as_html'):
        return m.as_html()

    return m.GetMsg()

@application.route('/api/config/<config_type>', methods=['POST'])
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

@application.route('/api/config/<config_type>', methods=['GET'])
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

@application.route('/api/config/<config_type>/<config_name>', methods=['GET'])
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

@application.route('/api/config/<config_type>/<config_name>', methods=['DELETE'])
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


@application.route('/api/config/<config_type>/<module_name>/spec', methods=['GET'])
def get_config_spec(config_type, module_name):
    """
    Get the spec of the given configuration type (i.e options etc)
    :param config_type: Type of configuration object to retrieve
    :return: ConfigGet
    """
    c = ConfigFile()
    c.load_from_file(DEFAULT_CONFIG_FILE)

    if config_type == "input":
        inputs = c.get_inputs_available()
        if module_name in inputs:
            mod = inputs[module_name]
    elif config_type == "output":
        outputs = c.get_outputs_available()
        if module_name in outputs:
            mod = outputs[module_name]
    else:
        mods = c.get_mods_available()
        if module_name in mods:
            mod = mods[module_name]

    spec = mod.module_options.get_spec()

    m = ModuleSpec()
    m.set_specs(spec)
    m.set_type(config_type)
    m.set_name(module_name)

    if request.args.get("from"):
        f = request.args.get("from")
        db = c.get_cdb()
        db.update_path(config_type)
        values = db.get(f)
        m.add_values(values)

    if request.args.get('as_html'):
        return m.as_html()
    return m.GetMsg()
