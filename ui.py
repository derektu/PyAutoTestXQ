import pywinauto
import sys, os, time, datetime
import util
from xqbuild import XQBuild
from xqwindow import XQWindow

class KSettingDB():
    """
    技術分析設定DB
    """
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

    def activate_indicator_tab(self, is_main_indicator):
        return self.activate_tab(self.get_indicator_tabname(is_main_indicator))

    def switch_freq(self, freq):
        """
        切換主圖到某個頻率
        :param freq=N (for分鐘頻率) or D / W / M / Q / H / Y / AD / AW / AM
        """
        self.activate_tab_general()
        tab = self.dlg['一般']
        freqcombo = tab.child_window(control_id = 1291)
        freqcombo.select(util.get_freq_name(freq))

    def get_indicators_under(self, is_main_indicator, rootpath):
        """
        回傳主圖 or 副圖指標清單 under rootpath
        :param rootpath 定義指標的路徑, 格式為list of string, e.g. ['技術指標'] or ['XS指標', '系統']
        """
        tab = self.dlg[self.get_indicator_tabname(is_main_indicator)]
        return self.get_child_paths(tab.Treeview, rootpath)

    def get_child_paths(self, treeview, root_path):
        """
        Return child nodes of root_path as an array of nodepath
        :param root_path: path of the root node, defined as a list of string, for example ['技術指標'] or ['XS指標', '系統']
        return an array of list of string, for example [ ['技術指標', 'RSI], ['XS指標', '系統', '主圖指標', 'EMA']] 
        """    
        all_paths = []
        root_node = treeview.get_item(root_path)
        self.__traverse_children(all_paths, root_node, root_path)
        return all_paths

    def __traverse_children(self, all_paths, current_node, current_path):
        # print(f"current_path={','.join(current_path)}")
        if len(current_node.children()) == 0:
            all_paths.append(current_path)
        for child_node in current_node.children():
            # print(f"len of [{child_node.text()}] = {len(child_node.children())}")
            child_path = current_path.copy()
            child_path.append(child_node.text())
            self.__traverse_children(all_paths, child_node, child_path)

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

    def delete_all_indicators(self, is_main_indicator):
        """
        刪除所有主圖/副圖指標
        """
        # 作法是click 指標Listview, 之後'X'按鈕會enable, 接著就click 'X' button
        #
        tab = self.dlg[self.get_indicator_tabname(is_main_indicator)]
        ta_list_grid = tab.child_window(class_name='MFCGridCtrl')
        rect = ta_list_grid.client_rect()
        # 點在grid左上方方1/3處, 這樣子會activate上方的toolbar
        coords = (rect.left + (rect.right - rect.left) // 3, rect.top + 20)
        self.xq.mainwnd.set_focus()
        ta_list_grid.click(coords=coords)
        self.xq.mainwnd.set_focus()
        delete_btn = tab.child_window(control_id=1114)
        while (self.xq.is_enabled(delete_btn)):
            delete_btn.click()
            self.xq.mainwnd.set_focus()
            time.sleep(1)

    def add_indicator(self, is_main_indicator, indicator_path):
        """
        加入某個指標
        :param is_main_indicator: 主圖疊圖 or 副圖指標
        :param indicator_path: 指標名稱, 請傳入指標的tree路徑, 例如"\\XS指標\\系統\\XQ技術指標\\RSI"
        """
        tab = self.dlg[self.get_indicator_tabname(is_main_indicator)]
        treeview = tab.TreeView
        node = treeview.get_item(indicator_path)
        node.ensure_visible()
        node.click(double=True)
        self.xq.mainwnd.set_focus()

    def get_indicator_tabname(self, is_main_indicator):
        return '主圖疊圖' if is_main_indicator else '副圖設定'

    def close(self):
        ok_btn = self.dlg.child_window(control_id=1)
        ok_btn.click_input()


"""
TreeViewExtension: extend treeview function
"""
class TreeViewExtension():
    def __init__(self, treeview):
        self.treeview = treeview

    def get_child_paths(self, root_path):
        """
        Return child nodes of root_path as an array of nodepath
        :param root_path: path of the root node, defined as a list of string, for example ['技術指標'] or ['XS指標', '系統']
        return an array of list of string, for example [ ['技術指標', 'RSI], ['XS指標', '系統', '主圖指標', 'EMA']] 
        """    
        all_paths = []
        root_node = self.treeview.get_item(root_path)
        self.__traverse_children(all_paths, root_node, root_path)
        return all_paths

    def __traverse_children(self, all_paths, current_node, current_path):
        # print(f"current_path={','.join(current_path)}")
        if len(current_node.children()) == 0:
            all_paths.append(current_path)
        for child_node in current_node.children():
            # print(f"len of [{child_node.text()}] = {len(child_node.children())}")
            child_path = current_path.copy()
            child_path.append(child_node.text())
            self.__traverse_children(all_paths, child_node, child_path)


