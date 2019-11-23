import sys, os, time, datetime
import util
from xqbuild import XQBuild

"""
提供test.json內"setting"的基本處理流程
"""
class TestSetting():
    def __init__(self, config):
        self.setting = config["setting"]

    def init(self):
        """
        Parse setting parameters and do test initialization
        """
        # determine XQ build
        self.build = XQBuild.from_str(util.get_property(self.setting, "build", "xq"))
        if not self.build: raise Exception('Invalid build setting.')

        # output folder
        self.output_folder = util.get_property(self.setting, "outputfolder", r'.\output\${DATETIME}')
        self.output_folder = self.output_folder.replace('${DATETIME}', datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
        os.makedirs(self.output_folder)

        # default wait time
        self.default_wait_time = util.get_int_property(self.setting, "waittime", 5)

    def get_property(self, field, default_value):
        return util.get_property(self.setting, field, default_value)

    def get_int_property(self, field, default_value):
        return util.get_int_property(self.setting, field, default_value)


