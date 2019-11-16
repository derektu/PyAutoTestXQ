from pywinauto.application import Application
from enum import Enum
import configparser

class XQBuild(Enum):
    XQ = 1
    XQLite = 2
    XQ7 = 3

    @staticmethod
    def from_str(label):
        """
        convert a string to XQBuild
        :param label: should be 'XQ', 'XQLite', 'XQ7" (case-insensitive)         
        """
        label = label.lower()
        if label == 'xq':
            return XQBuild.XQ
        elif label == 'xqlite':
            return XQBuild.XQLite
        elif label == 'xq7':
            return XQBuild.XQ7
        else:
            return None

    def spec(self):
        if self.name == 'XQ':
            return {
                'class_name': 'DAQMainWnd',
                'exe_path' : r'c:\SysJust\XQ2005\daq.exe',
                'title' : 'XQ全球贏家'
            }
        elif self.name == 'XQLite':
            return {
                'class_name': 'DAQXQLiteMainWnd',
                'exe_path' : r'c:\SysJust\XQLite\daqxqlite.exe',
                'title' : 'XQ操盤高手'
            }
        elif self.name == 'XQ7':
            return {
                'class_name': 'DAQMainWnd',
                'exe_path' : r'c:\SysJust\XQ7\daq7.exe',
                'title' : 'XQ全球贏家 Beta測試版'
            }
        else:
            return None


def find_xq_mainwnd(build):
    """
    Return the main window of XQ
    :param build: one of XQBuild
    """
    spec = build.spec()
    app = Application().connect(class_name=spec['class_name'])
    mainwnd = app.window(title_re=spec['title'])
    return mainwnd


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

"""
# xtptoolbar = mainwnd[u'DAQ Menu']

# mainwin.print_control_identifers()

#notepadapp = Application().start('notepad.exe')
"""
