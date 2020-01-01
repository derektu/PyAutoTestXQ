import pywinauto
import sys, os, time, datetime, json
import util
from xqbuild import XQBuild
from xqwindow import XQWindow
from testsetting import TestSetting

class SensorTester():
    def __init__(self, xq):
        self.xq = xq

    def open(self):
        # 開啟策略雷達 (Note: for xqlite可能需要不同的key sequences)
        #
        self.xq.mainwnd.set_focus()
        self.xq.mainwnd.type_keys('%D{DOWN}{DOWN}{DOWN}{DOWN}{DOWN}{DOWN}{ENTER}')
        self.connect()

    def connect(self):
        # TODO: 之後的XQ會貼上XQ version
        # for example "策略雷達 - XQ全球贏家"
        #
        self.sensorwin = self.xq.app['策略雷達']
        self.searchbox = self.sensorwin.child_window(control_id=33005)
        self.treeview = self.sensorwin.child_window(class_name='SysTreeView32')
        self.propertyview = self.sensorwin.child_window(class_name='SysTabControl32')
        self.start_button_coords = self.__get_start_button_coords()
        self.stop_button_coords = self.__get_stop_button_coords()

    def start_sensor(self, folder, name, waittime):
        """
        啟動sensor
        :param folder: sensor的完整路徑, for example: '\\系統\\出場常用\\多單出場'
        :param name: sensor的名稱
        :waittime: 執行後的等待時間
        :return: a dict with the following keys: 'all', 'run', 'error', 'wait', 'stop', 代表目前執行狀態
        """
        self.searchbox.set_edit_text(name)
        treenode = self.treeview.get_item(folder)
        treenode.ensure_visible()
        treenode.click()

        self.sensorwin.set_focus()
        pywinauto.mouse.click(button='left', coords=self.start_button_coords)

    def stop_sensor(self, folder, name, waittime):
        """
        停止sensor
        :param folder: sensor的完整路徑, for example: '\\系統\\出場常用\\多單出場'
        :param name: sensor的名稱
        :waittime: 執行後的等待時間
        :return: a dict with the following keys: 'all', 'run', 'error', 'wait', 'stop', 代表目前執行狀態
        """
        self.searchbox.set_edit_text(name)
        treenode = self.treeview.get_item(folder)
        treenode.ensure_visible()
        treenode.click()

        self.sensorwin.set_focus()
        pywinauto.mouse.click(button='left', coords=self.stop_button_coords)

        # 等待確認畫面
        confirmdlg = self.xq.app["停止策略雷達"]
        confirmdlg.wait('ready', timeout=1)
        confirmdlg["Button0"].click()

    def show_monitor_view(self):
        """
        切換到商品監控view
        """
        self.propertyview.select("商品監控")

    def get_sensor_status(self):
        """
        回傳sensor目前的狀態
        """
        self.propertyview.select("商品監控")
        monitorview = self.sensorwin.child_window(control_id=33001)

        lbl_all = monitorview.child_window(control_id=17622)
        lbl_run = monitorview.child_window(control_id=17623)
        lbl_error = monitorview.child_window(control_id=17624)
        lbl_wait = monitorview.child_window(control_id=17625)
        lbl_stop = monitorview.child_window(control_id=17626)
        return dict(all=int(lbl_all.window_text()), run=int(lbl_run.window_text()), error=int(lbl_error.window_text()), wait=int(lbl_wait.window_text()), stop=int(lbl_stop.window_text()))

    def __get_start_button_coords(self):
        # "手機傳送"右邊一個按鈕, 按鈕寬度跟"手機傳送"類似
        #
        label = self.sensorwin["手機傳送"]
        label_rect = label.rectangle()
        return (label_rect.right + (label_rect.right - label_rect.left) // 2, label_rect.top + (label_rect.bottom - label_rect.top) // 2)

    def __get_stop_button_coords(self):
        # "手機傳送"右邊兩個按鈕, 按鈕寬度跟"手機傳送"類似
        #
        label = self.sensorwin["手機傳送"]
        label_rect = label.rectangle()
        return (label_rect.right + (label_rect.right - label_rect.left) * 3 // 2, label_rect.top + (label_rect.bottom - label_rect.top) // 2)


xq = XQWindow(XQBuild.XQ)
xq.connect()

sensortester = SensorTester(xq)
sensortester.open()

sensortester.start_sensor(r'\系統\市場常用\多頭', '大單敲進', 10)

sensortester.show_monitor_view()

status = sensortester.get_sensor_status()
print(status)

sensortester.stop_sensor(r'\系統\市場常用\多頭', '大單敲進', 10)


"""
# 開啟策略雷達 (Note: for xqlite可能需要不同的key sequences)
xq.mainwnd.set_focus()
xq.mainwnd.type_keys('%D{DOWN}{DOWN}{DOWN}{DOWN}{DOWN}{DOWN}{ENTER}')


sensorwin = xq.app['策略雷達']
#sensorwin.exists()
#sensorwin.is_visible()
sensorwin.maximize()

searchbox = sensorwin.child_window(control_id=33005)
searchbox.set_edit_text('MACD')

treeview = sensorwin.child_window(class_name='SysTreeView32')
node = treeview.get_item(r'\系統\出場常用\多單出場')
node.ensure_visible()
node.click()

propertyview = sensorwin.child_window(class_name='SysTabControl32')
propertyview.select("商品監控")
monitorview = sensorwin.child_window(control_id=33001)

combobox = monitorview.child_window(control_id=17613)
combobox.item_count()

label_all = monitorview.child_window(control_id=17622)
label_run = monitorview.child_window(control_id=17623)
label_error = monitorview.child_window(control_id=17624)
label_waiting = monitorview.child_window(control_id=17625)
label_stop = monitorview.child_window(control_id=17626)


# 商品監控tab
# combobox = 0x44CD (17613)
# 全部static = 0x44D6 (17622)
# 執行中static = 0x44D7 (17623)
# 錯誤static = 0x44D8 (17624)
# 等待static = 0x44D9 (17625)
# 停止static = 0x44DA (17626)


# to locate "啟動" button
# "手機傳送"右邊一個按鈕, 按鈕寬度跟"手機傳送"類似
#
label = sensorwin["手機傳送"]
label_rect = label.rectangle()
coords = (label_rect.right + (label_rect.right - label_rect.left) // 2, label_rect.top + (label_rect.bottom - label_rect.top) // 2)

sensorwin.set_focus()
pywinauto.mouse.click(button='left', coords = coords)
# TODO: confirm it is working


# to locate "停止" button
# "手機傳送"右邊一個按鈕, 寬度跟"手機傳送"類似
#
label = sensorwin["手機傳送"]
label_rect = label.rectangle()
coords = (label_rect.right + (label_rect.right - label_rect.left) * 3 // 2, label_rect.top + (label_rect.bottom - label_rect.top) // 2)
sensorwin.set_focus()
pywinauto.mouse.click(button='left', coords = coords)
# TODO: wait a little bit, look for confirm DB
confirmdlg = xq.app["停止策略雷達"]
confirmdlg["Button0"].set_focus()
confirmdlg["Button0"].click()


"""




