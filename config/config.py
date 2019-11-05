from modules import *

class Config:
    def __init__(self):
        pass

    def init_modules(self):
        return [DNSHost, Panfw]