#!/usr/bin/env python3

from pywinauto.application import Application
import sys, getopt
import os
import time
import datetime
import re
import util

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

def test_system_page(config_file, encoding = 'utf-8'):
    """
    Run SystemPage test defined in config_file
    :param config_file: location of the test specification file
    :param encoding: encoding for the config file.
    """
    SECTION_GENERAL = 'general'
    SECTION_ITEMS = 'items'
    KEY_BUILD = 'build'
    KEY_OUTPUTFOLDER = 'outputfolder'
    KEY_WAITTIME = 'waittime'
    KEY_ITEM = 'item'

    # load setting
    dict = util.load_ini_file(config_file, encoding)

    # determine XQ build
    build = util.XQBuild.from_str(dict[SECTION_GENERAL].get(KEY_BUILD, 'xq'))
    if not build:
        raise Exception('Invalid build setting.')

    output_folder = dict[SECTION_GENERAL].get(KEY_OUTPUTFOLDER, r'.\output\${DATETIME}')
    output_folder = output_folder.replace('${DATETIME}', datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(output_folder)

    default_wait_time = int(dict[SECTION_GENERAL].get(KEY_WAITTIME, '5'))

    # TODO: 開始產生html檔案, 紀錄每個動作

    try:
        # locate XQ main window
        mainwnd = util.find_xq_mainwnd(build)
        for itemkey in dict[SECTION_ITEMS].keys():
            if not itemkey.startswith('item'): continue
            item = dict[SECTION_ITEMS][itemkey]
            fields = item.split("|")
            if len(fields) < 2 : continue
            # fields[0] = name
            # fields[1] = keycode combinations

            # TODO: 紀錄動作(目前時間, 準備測試 fields[0])

            keys = convert_to_key_sequences(fields[1])

            mainwnd.set_focus()
            for key in keys:
                time.sleep(1)
                mainwnd.type_keys(key)
            wait_time = int(fields[2]) if len(fields) >= 3 else default_wait_time
            time.sleep(wait_time)
            mainwnd.wait('ready')

            # TODO: 紀錄動作(目前時間, 產出img: capture_filename)

            # capture screen as image file
            capture_filename = os.path.join(output_folder, fields[0] + ".png")
            mainwnd.capture_as_image().save(capture_filename)
    except Exception as e:
        print('Exception:' + str(e))    
        # TODO 產生錯誤紀錄
        raise

def usage():
    print(r'C> systempage_tester.py <testfile>')

def main():
    """
    C> systempage_tester.py <location of testfile>
    """
    if len(sys.argv) <= 1:
        usage()
        sys.exit(2)    
    try:
        test_system_page(sys.argv[1])
    except Exception as e:
        print('Exception:' + str(e))
        sys.exit(1)    

if __name__ == "__main__":
    main()

