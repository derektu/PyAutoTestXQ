import pywinauto
import sys, os, time, datetime, json
import util
import ui
from xqbuild import XQBuild
from xqwindow import XQWindow
from testsetting import TestSetting

#import importlib
#importlib.reload(ui)

"""
preparation
- XQ預設值
    - 每個workspace都指定快捷頁(make sure每次重開時都是一樣的狀態)
    - 關閉通知(換版通知, 交易通知, 系統訊息, etc.)
- 檔案"001-K.dap", 指定快捷鍵501

"""
def get_indicators_to_test(xq, is_main_indicator, rootpath):
    dlg = ui.KSettingDB(xq)
    dlg.show()
    dlg.activate_indicator_tab(is_main_indicator)
    child_paths = dlg.get_indicators_under(is_main_indicator, rootpath)
    dlg.close()
    return child_paths

def do_one_test(xq, symbol, freq, is_main_indicator, indicator_path):
    # 切換商品
    xq.enter_symbol_text(symbol)
    xq.mainwnd.set_focus()
    
    # 開啟K線設定DB
    dlg = ui.KSettingDB(xq)
    dlg.show()

    # 切換頻率
    dlg.switch_freq(freq)

    # 切到主圖/副圖tab
    dlg.activate_indicator_tab(is_main_indicator)
    time.sleep(1)

    # 刪除目前的指標
    dlg.delete_all_indicators(is_main_indicator)

    # 加入要測試的指標
    dlg.add_indicator(is_main_indicator, indicator_path)
    time.sleep(1)
    dlg.close()         

def test_k_sub_indicator(config_file, encoding = 'utf-8'):
    """
    Run K indicator test defined in config_file
    :param config_file: location of the test specification file
    :param encoding: encoding for the config file.
    """
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

    if setting.get_property("type", "sub") == "main":
        is_main_indicator = True
    else:
        is_main_indicator = False    

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
        child_paths = get_indicators_to_test(xq, is_main_indicator, rootpath)
        ##child_paths = child_paths[:4]

        for symbol in symbols:
            for freq in freqs:
                for indicator_path in child_paths:
                    xq.mainwnd.set_focus()
                    do_one_test(xq, symbol, freq, is_main_indicator, indicator_path)
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
