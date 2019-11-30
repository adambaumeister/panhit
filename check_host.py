from phlibs.host import HostList
from phlibs.config import ConfigFile
from phlibs.db import JsonDB
from tabulate import tabulate
import getpass
import os
import argparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)



def env_or_prompt(prompt, args, prompt_long=None, secret=False):
    k = "PH_{}".format(prompt).upper()
    e = os.getenv(k)
    if e:
        return e

    if args.__dict__[prompt]:
        return args.__dict__[prompt]

    if secret:
        e = getpass.getpass(prompt + ": ")
        return e

    if prompt_long:
        e = input(prompt_long)
        return e

    e = input(prompt + ": ")
    return e

def tag(host_list, policy):
    for h in host_list.get_all_hosts():
        for t in reversed(policy):
            if 'match_any' in t:
                match = True
            else:
                match = True
                for match_attr, match_value in t['match'].items():
                    r = h.compare_attr(match_attr, match_value)
                    if not r:
                        match = False

            if match:
                h.set_tag(t['name'])




if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Copy a config from an xpath on one device to the xpath on another.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    script_options = parser.add_argument_group("Script options")

    script_options.add_argument("--config_file", help="Path to panhit configuration file.")
    script_options.add_argument("--daemon", action="store_true", help="Run panhhit as a daemon.")
    script_options.add_argument("--password",
                                help="Firewall/Panorama login password. Can also use envvar PC_PASSWORD")

    args = parser.parse_args()

    pw = env_or_prompt("password", args, secret=True)

    mod_opts = {
        'pw': pw
    }

    print("""Warning: SSL validation of PANOS device is currently disabled. Use --validate to enable it.""")

    c = ConfigFile()
    c.load_from_file(args.config_file)
    mods = c.init_modules(mod_opts)

    db = c.get_db()
    input = c.get_input(mod_opts)
    hl = HostList(input, mods_enabled=mods, db=db)
    hl.run_all_hosts()

    tag(hl, c.tags)

    output = c.get_output(mod_opts)
    output.Output(hl)