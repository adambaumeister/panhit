import ipaddress

class ModuleOption:
    """
    A single option, passed to a module.
    """

    def __init__(self, name):
        self.name = name
        self.nice_name = name
        self.required = False
        self.secret = False
        # Default option type is str
        self.type = str
        self.type_str = "str"
        self.help = ""
        self.default = None

    def spec(self):
        return {
            "name": self.name,
            "nice_name": self.nice_name,
            "required": self.required,
            "secret": self.secret,
            "type": self.type_str,
            "help": self.help,
        }


class ModuleOptions:
    """
    Options available to a module
    """

    def __init__(self, module_options):

        self.module_options = {}
        for option in module_options:
            self.module_options[option.name] = option

        self.options = {}

    def parse_dict(self, d):
        print(d)
        for name, option in self.module_options.items():
            if name not in d:
                if option.required:
                    raise ValueError("Missing module option: {}".format(name))
                elif option.default:
                    self.options[name] = option.default
            else:
                self.options[name] = d[name]

    def add_opt(self, option):
        self.module_options[option.name] = option

    def get_opt(self, opt):
        if opt not in self.options:
            return None

        return self.options[opt]

    def get_options(self):
        return self.options.keys()

    def get_spec(self):
        spec = []
        for name, option in self.module_options.items():
            spec.append(option.spec())

        return spec

    def get_all_nice(self):
        r = {}
        for name, option in self.module_options.items():
            key = option.nice_name
            if option.secret:
                value = "*******"
            else:
                value = self.get_opt(name)

            r[key] = value
        return r

    def get_all_nice_joined(self):
        r = self.get_all_nice()
        result = []
        for option in r.values():
            if option:
                result.append(option)

        printable_result = []
        for r in result:
            if type(r) is str:
                printable_result.append(r)
            elif type(r) is list:
                s = ", ".join(r)
                printable_result.append(s)
        return " • ".join(printable_result)

    def remove_option(self, option_name):
        if option_name in self.module_options:
            del self.module_options[option_name]


class Module:
    """
    A module represents a discrete set of tools for enriching a host with additional data
    """

    def __init__(self, opts):
        self.data = {}
        self.opts = opts
        self.parse_options()

        self.result_spec = None

        if opts:
            if 'name' in opts:
                self.name = opts['name']

    def get_name(self):
        return self.name

    def Get(self, host):
        pass

    def parse_options(self):
        if self.opts:
            # If this module has defined module options
            if self.module_options:
                self.module_options.parse_dict(self.opts)

    def get_spec(self):
        return self.result_spec

class ResultSpec:
    def __init__(self):
        self.fields = {}
        pass

    def add_field(self, field):
        self.fields[field.name] = field

    def new_str_field(self, field_name):
        f = StringResultField()
        f.name = field_name
        self.add_field(f)

    def new_addr_field(self, field_name):
        f = AddressField()
        f.name = field_name
        self.add_field(f)

    def new_list_field(self, field_name):
        f = ListField()
        f.name = field_name
        self.add_field(f)

class ResultField:
    def __init__(self):
        self.name = ""
        self.data = ""
        pass

    def get_type(self):
        return type(self)

    def set(self, value):
        self.data = value


class StringResultField(ResultField):
    def __init__(self):
        super(StringResultField, self).__init__()


class AddressField(ResultField):
    def __init__(self):
        super(AddressField, self).__init__()

    def set(self, value):
        addr = ipaddress.ip_address(value)
        self.data = addr

class ListField(ResultField):
    def __init__(self):
        super(ListField, self).__init__()

    def set(self, values):
        self.data = values