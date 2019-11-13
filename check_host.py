from host import HostList
from config import ConfigFile
from tabulate import tabulate
import getpass
import os
import argparse

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

def as_table(host_list):
    headers = []
    rows = []
    for h in host_list.get_all_hosts():
        for attr, value in h.attributes.items():
            if attr not in headers:
                headers.append(attr)

        for mod, results in h.result.items():
            for k, v in results.items():
                if k not in headers:
                    headers.append(k)

    for h in host_list.get_all_hosts():
        row = []
        for header in headers:
            v = 'None'
            if header in h.attributes:
                v = h.attributes[header]
            else:
                for mod, results in h.result.items():
                    if header in results:
                        v = results[header]

            row.append(v)

        rows.append(row)

    table = tabulate(rows, headers=headers)
    print(table)

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

    for h in host_list.get_all_hosts():
        print(h.attributes['name'], h.tag)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Copy a config from an xpath on one device to the xpath on another.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    script_options = parser.add_argument_group("Script options")

    script_options.add_argument("--config_file", help="Path to panhit configuration file.")
    script_options.add_argument("--password",
                                help="Firewall/Panorama login password. Can also use envvar PC_PASSWORD")

    args = parser.parse_args()

    pw = env_or_prompt("password", args, secret=True)

    mod_opts = {
        'pw': pw
    }

    c = ConfigFile(path=args.config_file)
    mods = c.init_modules(mod_opts)

    input = c.get_input(mod_opts)
    hl = HostList(input, mods_enabled=mods)
    hl.run_all_hosts()

    as_table(hl)
    tag(hl, c.tags)

    output = c.get_output(mod_opts)
    output.Output(hl)