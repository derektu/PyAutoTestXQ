from enum import Enum

"""
class XQBuild: provide information for different XQ build
"""
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
