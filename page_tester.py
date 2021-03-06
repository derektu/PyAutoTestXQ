import sys, os, time, datetime, re, json
import util
from xqwindow import XQWindow
from xqbuild import XQBuild
from testsetting import TestSetting

def convert_to_key_sequences(keysequence):
    """
    convert keys to a list of pwwinauto keycode
    :param keysequence: 按鍵順序, 例如: "M,R,2R,D,2D", where
                        the first item is the menu key,
                        the subsequent items are either R(for RIGHT), D(for DOWN), or <N>R, 
                        where <N> is a number to specify number of occurrance of this key
    """
    keys = keysequence.split(',')
    if len(keys) < 1: return None
    outputs = []
    outputs.append("%" + keys[0])
    for key in keys[1:]:
        m = re.search(r"(\d*)([RD])", key)
        if not m: continue
        groups = m.groups()
        if len(groups) < 2: continue
        code = "{RIGHT}" if groups[1] == "R" else "{DOWN}"
        count = 1 if not groups[0] else int(groups[0])
        outputs.extend([code for i in range(count)])
    outputs.append("{ENTER}")        
    return outputs        

def test_page(config_file, encoding = 'utf-8'):
    """
    Run Page test defined in config_file
    :param config_file: location of the test specification file
    :param encoding: encoding for the config file.
    """
    
    # load setting
    with open(config_file, encoding=encoding) as config_json_file:
        config = json.load(config_json_file)

    # test setting 
    setting = TestSetting(config)
    setting.init()

    # TODO: 開始產生html檔案, 紀錄每個動作

    try:
        # locate XQ main window
        xq = XQWindow(setting.build)
        xq.connect()
        for item in config["items"]:
            name = util.get_property(item, "name", "")
            if not name: raise NameError("name")

            pagetype = util.get_property(item, "type", "s")
            if pagetype != "s" and pagetype != "u": raise Exception("type must be s|u")

            keys = util.get_property(item, "keys", "")
            if not keys: raise NameError("keys")

            # TODO: 紀錄動作(目前時間, 準備測試 name)

            if pagetype == "s":            
                # 系統頁面=> 點擊menu
                keycodes = convert_to_key_sequences(keys)

                xq.mainwnd.set_focus()
                for keycode in keycodes:
                    time.sleep(1)
                    xq.mainwnd.type_keys(keycode)
            else:
                # 使用者頁面=> 輸入頁碼
                xq.mainwnd.set_focus()
                xq.enter_symbol_text(keys)

            wait_time = util.get_int_property(item, "waittime", 0)
            if wait_time <= 0: wait_time = setting.default_wait_time

            time.sleep(wait_time)
            xq.mainwnd.wait('ready')

            # TODO: 紀錄動作(目前時間, 產出img: capture_filename)

            # capture screen as image file
            capture_filename = os.path.join(setting.output_folder, name + ".png")
            xq.mainwnd.capture_as_image().save(capture_filename)
            time.sleep(1)

            # 更換商品的測試
            #
            symbols = item.get('symbols') or []
            if len(symbols) > 0:
                for symbol in symbols:
                    xq.mainwnd.set_focus()
                    xq.enter_symbol_text(symbol)
                    time.sleep(wait_time)
                    xq.mainwnd.wait('ready')
                    capture_filename = os.path.join(setting.output_folder, name + "-" + symbol + ".png")
                    xq.mainwnd.capture_as_image().save(capture_filename)
                    time.sleep(1)
    except Exception as e:
        print('Exception:' + str(e))    
        # TODO 產生錯誤紀錄
        raise

def usage():
    print(r'C> page_tester.py <testfile>')

def main():
    """
    C> page_tester.py <location of testfile>
    """
    if len(sys.argv) <= 1:
        usage()
        sys.exit(2)    
    try:
        test_page(sys.argv[1])
    except Exception as e:
        print('Exception:' + str(e))
        sys.exit(1)    

#if __name__ == "__main__":
#    main()

#test_page(r'.\spec\systempage-大盤.json')
test_page(r'.\spec\userpage.json')
