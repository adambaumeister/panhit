
def is_host(ip):
    """
    Checks whether an address is a subnet address or a single address
    :param ip: ip address or subnet
    :return: True if host
    """
    r = ip.split("/")
    if len(r) > 1:
        return False

    return True

