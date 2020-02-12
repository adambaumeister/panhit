from tabulate import tabulate

class Table():
    def __init__(self):
        pass

    def Output(self, host_list):
        headers = []
        rows = []
        for h in host_list.get_all_hosts():
            print(h.attributes)
            for attr, value in h.attributes.items():
                if attr not in headers:
                    headers.append(attr)

            for mod, results in h.result.items():
                for k, v in results.items():
                    if k not in headers:
                        headers.append(k)

        for h in host_list.hosts:
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