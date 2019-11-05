from host import HostList
from config import Config

c = Config()
mods = c.init_modules()

hl = HostList(source="./ipaddr.json")
hosts = hl.get_all_hosts()
print(hosts[0].ip)