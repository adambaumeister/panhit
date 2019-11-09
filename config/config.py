from modules import *

class Config:
    def __init__(self):
        pass

    def init_modules(self, mod_opts):
        return [DNSHost(mod_opts), Panfw(mod_opts)]