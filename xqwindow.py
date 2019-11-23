import pywinauto
from pywinauto.application import Application

"""
提供XQ相關的測試api

xq = new XQWindow(XQBuild.xq)
xq.connect
xq.mainwnd.do_something

"""
class XQWindow():
    def __init__(self, build):
        self.build = build

    def connect(self):
        """
        Connect to running XQ instance. Will throw exception if XQ is not found.
        TODO: 之後加上launch相關的功能
        """
        spec = self.build.spec()
        self.app = Application()
        self.xqapp = self.app.connect(class_name=spec['class_name'])
        self.mainwnd = self.app.window(title_re=spec['title'])
        self.mainwnd.wait('ready')

    def enter_symbol_text(self, text):
        """
        Send the text to 商品editbox
        :param mainwnd: XQ main window
        :param text: 要輸入的文字, 例如商品代碼, 或是頁碼
        """
        toolbar = self.mainwnd.child_window(class_name='XTPToolBar', title=r"一般")
        omnibox = toolbar.child_window(class_name='RichEdit20A')
        omnibox.set_edit_text(text)
        omnibox.type_keys('{ENTER}')

    def mouse_click_center(self, win):
        """
        Mouse click at the center of win
        """
        rect = win.rectangle()
        coords = (rect.left + (rect.right - rect.left)//2, rect.top + (rect.bottom - rect.top)//2)
        pywinauto.mouse.click(coords = coords)

    def is_enabled(self, win):
        """
        return: True if win is enabled
        """
        return pywinauto.handleprops.isenabled(win)

