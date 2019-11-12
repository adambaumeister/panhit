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
    for h in host_list.get_all_hosts():
        headers = []
        values = []
        for attr, value in h.attributes.items():
            headers.append(attr)
            values.append(value)

        for mod, results in h.result.items():
            for k, v in results.items():
                headers.append(k)
                values.append(v)

        table = tabulate([values], headers=headers)
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
        print("{} : {}".format(h.ip, h.tag))

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

    input = c.get_input()
    hl = HostList(source=input, mods_enabled=mods)
    hl.run_all_hosts()

    as_table(hl)
    tag(hl, c.tags)