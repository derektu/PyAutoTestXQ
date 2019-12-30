import pywinauto
import sys, os, time, datetime, json
import util
import ui
from xqbuild import XQBuild
from xqwindow import XQWindow
from testsetting import TestSetting

"""
preparation
- XQ預設值
    - 每個workspace都指定快捷頁(make sure每次重開時都是一樣的狀態)
    - 關閉通知(換版通知, 交易通知, 系統訊息, etc.)
- 檔案"001-K.dap", 指定快捷鍵501

"""

class KSettingDB():
    def __init__(self, xq):
        self.xq = xq

    def show(self):
        """
        開啟設定畫面(for active mode)
        """
        # type ALT+ENTER to display 設定畫面
        self.xq.mainwnd.set_focus()
        self.xq.mainwnd.type_keys(r'%{ENTER}')      
        # locate 技術分析設定 dialog
        self.dlg = self.xq.app['技術分析設定']
        self.dlg.wait('ready')

    def activate_tab(self, tabname):
        """
        切到設定DB的某個tab
        :param tabname Tab的名稱
        """
        tabctrl = self.dlg['SysTabControl32']
        tabctrl.select(tabname)
        self.xq.mainwnd.set_focus()

    def activate_tab_general(self):
        return self.activate_tab('一般')

    def activate_tab_subindicator(self):
        return self.activate_tab('副圖設定')

    def switch_freq(self, freq):
        """
        切換主圖到某個頻率
        :param freq=N (for分鐘頻率) or D / W / M / Q / H / Y / AD / AW / AM
        """
        self.activate_tab_general()
        tab = self.dlg['一般']
        freqcombo = tab.child_window(control_id = 1291)
        freqcombo.select(util.get_freq_name(freq))

    def get_sub_indicators(self, rootpath):
        """
        回傳副圖指標清單 under rootpath
        :param rootpath 定義指標的路徑, 格式為list of string, e.g. ['技術指標'] or ['XS指標', '系統']
        """
        tab = self.dlg['副圖設定']
        tv = ui.TreeViewExtension(tab.TreeView)
        return tv.get_child_paths(rootpath)

    def delete_sub_indicators(self):
        """
        刪除所有副圖指標
        :param tab 副圖tab
        """
        # 作法是click副圖指標, 之後'X'按鈕會enable, 接著就click 'X' button
        #
        tab = self.dlg['副圖設定']
        ta_list_grid = tab.child_window(class_name='MFCGridCtrl')
        rect = ta_list_grid.client_rect()
        # 點在grid左上方方1/3處, 這樣子會activate上方的toolbar
        coords = (rect.left + (rect.right - rect.left) // 3, rect.top + 20)
        self.xq.mainwnd.set_focus()
        ta_list_grid.click(coords=coords)
        self.xq.mainwnd.set_focus()

        # rect = ta_list_grid.rectangle()

        # 點在grid左上方方1/3處, 這樣子會activate上方的toolbar
        # coords = (rect.left + (rect.right - rect.left) // 3, rect.top + 20)
        # self.xq.mainwnd.set_focus()
        # pywinauto.mouse.click(coords=coords)
        # self.xq.mainwnd.set_focus()

        delete_btn = tab.child_window(control_id=1114)
        while (self.xq.is_enabled(delete_btn)):
            delete_btn.click()
            self.xq.mainwnd.set_focus()
            time.sleep(1)

    def add_sub_indicator(self, indicator_path):
        """
        加入某個副圖指標
        :param indicator_path: 指標名稱, 請傳入指標的tree路徑, 例如"\\XS指標\\系統\\XQ技術指標\\RSI"
        """
        tab = self.dlg['副圖設定']
        treeview = tab.TreeView
        node = treeview.get_item(indicator_path)
        node.ensure_visible()
        node.click(double=True)
        self.xq.mainwnd.set_focus()

    def close(self):
        ok_btn = self.dlg.child_window(control_id=1)
        ok_btn.click_input()


def test_k_sub_indicator(config_file, encoding = 'utf-8'):
    """
    Run K indicator test defined in config_file
    :param config_file: location of the test specification file
    :param encoding: encoding for the config file.
    """

    def get_indicators_to_test(xq):
        dlg = KSettingDB(xq)
        dlg.show()
        dlg.activate_tab_subindicator()
        child_paths = dlg.get_sub_indicators(rootpath)
        dlg.close()
        return child_paths

    def do_one_test(xq, symbol, freq, indicator):
        xq.enter_symbol_text(symbol)
        xq.mainwnd.set_focus()
        # 開啟K線設定DB
        dlg = KSettingDB(xq)
        dlg.show()
        # 切換頻率
        dlg.switch_freq(freq)
        # 切到副圖tab
        #
        dlg.activate_tab_subindicator()
        time.sleep(1)
        # 刪除所有副圖指標
        #
        dlg.delete_sub_indicators()
        # 加入要測試的指標
        dlg.add_sub_indicator(indicator)
        time.sleep(1)
        dlg.close()         

    # load setting
    with open(config_file, encoding=encoding) as config_json_file:
        config = json.load(config_json_file)

    # test setting 
    setting = TestSetting(config)
    setting.init()

    pagecode = setting.get_property("pagecode", "")
    if not pagecode: raise Exception("Missing setting.pagecode")

    symbols = setting.get_property("symbols", [])
    if len(symbols) == 0: raise Exception("Missing setting.symbols")

    freqs = setting.get_property("freqs", ['D'])

    rootpath = setting.get_property("rootpath", "")
    if not rootpath: raise Exception("Missing setting.rootpath")

    # 轉成list格式, separated by '\'
    rootpath = rootpath.split('\\')       

    # TODO: 開始產生html檔案, 紀錄每個動作

    try:
        # locate XQ main window
        xq = XQWindow(setting.build)
        xq.connect()

        # open the test page
        xq.enter_symbol_text(pagecode)

        # 找出要測試的指標清單
        #
        child_paths = get_indicators_to_test(xq)
        ##child_paths = child_paths[:4]

        for symbol in symbols:
            for freq in freqs:
                for indicator_path in child_paths:
                    xq.mainwnd.set_focus()
                    do_one_test(xq, symbol, freq, indicator_path)
                    time.sleep(setting.default_wait_time)
                    xq.mainwnd.wait('ready')

                    # TODO: 紀錄動作(目前時間, 產出img: capture_filename)

                    # capture screen as image file
                    fname = f"{symbol}_{freq}_{indicator_path[-1]}.png"
                    capture_filename = os.path.join(setting.output_folder, fname)
                    xq.mainwnd.capture_as_image().save(capture_filename)
                    time.sleep(1)

    except Exception as e:
        print('Exception:' + str(e))    
        # TODO 產生錯誤紀錄
        raise

def usage():
    print(r'C> k_indicator_tester2.py <testfile>')

def main():
    """
    C> k_indicator_tester2.py <location of testfile>
    """
    if len(sys.argv) <= 1:
        usage()
        sys.exit(2)    
    try:
        test_k_sub_indicator(sys.argv[1])
    except Exception as e:
        print('Exception:' + str(e))
        sys.exit(1)    

if __name__ == "__main__":
    main()
