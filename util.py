import configparser

def load_ini_file(filename, encoding):
    """
    Convert an ini file as a python dict
    :param filename: ini filename
    :return: a dict that can be used as value = dict[section_name][key_name]
    """
    config = configparser.ConfigParser()
    config.read(filename, encoding)
    the_dict = {}
    for section in config.sections():
        the_dict[section] = {}
        for key, val in config.items(section):
            the_dict[section][key] = val
    return the_dict

def get_property(obj, field, default_value):
    """
    return obj[field] or default_value if field does not exist
    """     
    return obj.get(field) or default_value

def get_int_property(obj, field, default_value):
    """
    return obj[field] or default_value if field does not exist
    """    
    value = obj.get(field)
    if value is None:
        return default_value
    try:
        return int(value)
    except:
        return default_value     

"""
# xtptoolbar = mainwnd[u'DAQ Menu']

# mainwin.print_control_identifers()

#notepadapp = Application().start('notepad.exe')
"""
