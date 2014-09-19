from IPython.core.display import HTML
def css_styles():
    return HTML("""
        <style>
        .info {
            background-color: #fcf8e3; border-color: #faebcc; border-left: 5px solid #8a6d3b; padding: 0.5em; color: #8a6d3b;
        }
        .success {
            background-color: #d9edf7; border-color: #bce8f1; border-left: 5px solid #31708f; padding: 0.5em; color: #31708f;
        }
        .error {
            background-color: #f2dede; border-color: #ebccd1; border-left: 5px solid #a94442; padding: 0.5em; color: #a94442;
        }
        .warning {
            background-color: #fcf8e3; border-color: #faebcc; border-left: 5px solid #8a6d3b; padding: 0.5em; color: #8a6d3b;
        }
        </style>
    """)

def find_dict_keys(search, d):
    if isinstance(d, dict) and search in d:
        yield d[search]
    else:
        if isinstance(d, (tuple, list)):
            for a in d:
                for x in find_dict_keys(search, a):
                    yield x
        elif isinstance(d, dict):
            for a in d:
                for x in find_dict_keys(search, d[a]):
                    yield x


def get_coords(s):
    if hasattr(s, 'boundary'):
        if hasattr(s.boundary, 'coords'):
            yield s.boundary.coords
        else:
            try:
                for p in s:
                    for x in get_coords(p):
                        yield x
            except:
                pass


def get_variable_from_standard(nc, standard_name):
    var_matches = []
    for var in nc.variables:
        try:
            sn = nc.variables[var].standard_name
            if standard_name == sn:
                var_matches.append(var)
        except StandardError:
            pass

    return [nc.variables[v] for v in var_matches]
